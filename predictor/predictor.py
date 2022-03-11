import json
from pprint import pprint
import sys
import time
import requests
from datetime import datetime, timedelta
import pandas as pd
import csv
import ast
import os
from pathlib import Path
import os.path

path_util = Path(os.getcwd())
path_util = str(path_util) + '/predictor/utils/'
sys.path.append(path_util)
sys.path.append(path_util + 'calls_stats_nba/')
#import get_proxy
#import get_proxy_advanced
import general_splits
import splits_espn
import defense_stats_vs_position
from statistics import mean
import ssl


class predictor:

    def __init__(self, dunkest_bot=None):
        # {player_name: [name team, position, cost, score,
        # fantasy pts predicted]}
        self.PATH_DATA = str(Path(os.getcwd())) + '/data/'

        with open(self.PATH_DATA + 'config.json') as config:
            self.config = json.load(config)
        self.next_game_dict = {}
        self.players_filtered = dunkest_bot.players_filtered \
            if dunkest_bot is not None else None
        with open(self.PATH_DATA + 'players_nba.json') as players_nba:
            self.players_name_id = json.load(players_nba)
        with open(self.PATH_DATA
                  + 'players_nba_espn.json') as players_nba_espn:
            self.players_name_id_espn = json.load(players_nba_espn)
        with open(self.PATH_DATA + 'full_schedule.json') as schedule:
            self.full_schedule = json.load(schedule)
        with open(self.PATH_DATA + 'teams_nba.json') as teams:
            self.teams_name_id = json.load(teams)
        self.opponent_stats_G = {}
        self.opponent_stats_F = {}
        self.opponent_stats_C = {}
        self.predictions_rows_dict = {}
        #self.proxies = self.grab_proxies()

    def create_csv_predictions(self, offset):
        if offset is False:
            name_file = 'nba_players_predictions_no_offset.csv'
        else:
            name_file = 'nba_players_predictions_yes_offset.csv'
        with open(self.PATH_DATA + name_file, mode='w') as csv_file:
            fieldnames = [
                'PLAYER NAME', 'MIN', 'PTS', 'FGM', 'FGA', 'FTM', 'FTA',
                'OREB', 'DREB', 'AST', 'TOV', 'STL', 'BLK',
                'FANTASY PTS PREDICTION'
            ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

    def load_csv_predictions(self):
        players_dict = {}
        df = pd.read_csv(
            self.PATH_DATA + 'nba_players_predictions_no_offset.csv', header=0)
        # print(df)
        for index, row in df.iterrows():
            name_player = row['PLAYER NAME'].strip().lower().replace('.', '')
            players_dict[name_player] = row[1:]
        self.predictions_rows_dict = players_dict

    def check_difference_no_yes_offset(self):
        # pprint(self.players_filtered)
        players_dict_no_offset = {}
        players_dict_yes_offset = {}
        df = pd.read_csv(
            self.PATH_DATA + 'nba_players_predictions_no_offset.csv', header=0)
        # print(df)
        for index, row in df.iterrows():
            name_player = row['PLAYER NAME'].strip().lower().replace('.', '')
            players_dict_no_offset[name_player] = row[1:]
        df = pd.read_csv(
            self.PATH_DATA + 'nba_players_predictions_yes_offset.csv',
            header=0)
        # print(df)
        for index, row in df.iterrows():
            name_player = row['PLAYER NAME'].strip().lower().replace('.', '')
            players_dict_yes_offset[name_player] = row[1:]
        offset_g = []
        offset_f = []
        offset_c = []
        for p, data in players_dict_no_offset.items():
            print(p)
            print()
            print(data)
            if self.players_filtered[p][1] == 'G':
                role = "GUARD"
            elif self.players_filtered[p][1] == 'A':
                role = "FORWARD"
            elif self.players_filtered[p][1] == 'C':
                role = "CENTER"
            vs_team = self.next_game_dict[
                self.players_filtered[p][0]][1].upper()
            print(p.upper() + ", " + role + "  VS: " + vs_team)
            no_offset = data[-1]
            yes_offset = players_dict_yes_offset[p][-1]
            diff = yes_offset - no_offset
            if role == 'GUARD':
                offset_g.append(diff)
            elif role == 'FORWARD':
                offset_f.append(diff)
            elif role == 'CENTER':
                offset_c.append(diff)
            print("MINS PLAYED: {}".format(players_dict_no_offset[p][0]))
            print("PREDICTION -> NO OFFSET: {}".format(no_offset))
            print("PREDICTION -> YES OFFSET: {}".format(yes_offset))
            print("OFFSET: {}".format(diff))
            print("------------------------")
        print("MEAN OFFSET GUARD: {}".format(mean(offset_g)))
        print("MEAN OFFSET FORWARD: {}".format(mean(offset_f)))
        print("MEAN OFFSET CENTER: {}".format(mean(offset_c)))

    def grab_proxies(self):
        countries = ['IT', 'CH', 'NL', 'US']
        response = requests.get(
            'https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list',
            verify=False)
        proxies_list = response.text
        proxies_list = proxies_list.split('\n')
        list_result = []
        for line in proxies_list[:-1]:
            line = line.replace('null', '\"\"')
            line = ast.literal_eval(line)
            if line['type'] == 'https' and line['country'] in countries and line[
                    'response_time'] < 1:  # and line["anonymity"] == "high_anonymous":
                list_result.append(
                    (str(line['host']) + ':' + str(line['port'])))
        return list_result

    def append_row_to_csv(self, player, row, offset):
        self.predictions_rows_dict[player] = row
        row.insert(0, player)
        if offset is False:
            name_file = 'nba_players_predictions_no_offset.csv'
        else:
            name_file = 'nba_players_predictions_yes_offset.csv'
        with open(self.PATH_DATA + name_file, mode='a') as csv_file:
            writer = csv.writer(
                csv_file,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL)
            writer.writerow(row)

    def compute_next_game(self, player_name, player_data):
        team_player = player_data[0]
        games_team_player = self.full_schedule[team_player]
        now = datetime.now()
        minimium_difference = now - datetime(2000, 1, 1, 1, 00)
        next_game = None
        for game in games_team_player:
            game_time = datetime.strptime(game[2], '%Y-%m-%d %H:%M:%S')
            if game_time - now > pd.Timedelta(0):
                if game_time - now < minimium_difference:
                    minimium_difference = game_time - now
                    next_game = game
        return next_game

    def compute_next_game_all_teams(self):
        for team, id_team in self.teams_name_id.items():
            games_team = self.full_schedule[team]
            now = datetime.now()
            minimium_difference = now - datetime(2000, 1, 1, 1, 00)
            next_game = None
            for game in games_team:
                # print(game)
                game_time = datetime.strptime(game[2], '%Y-%m-%d %H:%M:%S')
                if game_time - now > pd.Timedelta(0):
                    if game_time - now < minimium_difference:
                        minimium_difference = game_time - now
                        next_game = game
            self.next_game_dict[team] = next_game
        with open(self.PATH_DATA + 'next_game_teams.json',
                  'w') as outfile:
            json.dump(self.next_game_dict, outfile)

    def create_dict_opponent_stats_all_teams(self):
        defense_stats_vs_position.main()
        with open(self.PATH_DATA + 'opponent_stats_G.json') as G:
            self.opponent_stats_G = json.load(G)
        with open(self.PATH_DATA + 'opponent_stats_F.json') as F:
            self.opponent_stats_F = json.load(F)
        with open(self.PATH_DATA + 'opponent_stats_C.json') as C:
            self.opponent_stats_C = json.load(C)

    def filter_split(self, split_row):
        split_row = [
            # MIN           PTS                FGM               FGA
            split_row[1],
            split_row[16],
            split_row[2].split('-')[0],
            split_row[2].split('-')[1],
            # FTM                FTA               OREB
            split_row[6].split('-')[0],
            split_row[6].split('-')[1],
            split_row[8],
            # DREB                AST               TOV
            split_row[9],
            split_row[11],
            split_row[15],
            # STL                 BLK
            split_row[13],
            split_row[12]
        ]
        return split_row

    def add_double_double_triple_double(self, prediction, row):
        stats = [row[1], row[6] + row[7], row[8], row[10], row[11]]
        count = sum(1 for elem in stats if elem >= 10)
        if count == 2:
            prediction += 5
        elif count == 3:
            prediction += 10
        elif count >= 4:
            prediction += 50
        return prediction

    def create_prediction_value(self, row):
        # simple fantasy point value using dunkest rules
        row = [float(elem) for elem in row]
        prediction = row[1] - (row[3] - row[2]) - (
            row[5] - row[4]) + 1.25 * row[6] + row[7] + 1.5 * row[
                8] - 1.5 * row[9] + 1.5 * row[10] + 1.5 * row[11]
        prediction = self.add_double_double_triple_double(prediction, row)
        return prediction

    def create_base_prediction_row(self,
                                   overall_split,
                                   days_rest_split=None,
                                   where_to_play_split=None):
        if days_rest_split is not None and where_to_play_split is not None:
            base_prediction_row = [
                0.5 * float(overall_split[i])
                + 0.35 * float(days_rest_split[i])
                + 0.15 * float(where_to_play_split[i])
                for i in range(1, len(overall_split))
            ]
            base_prediction_row.insert(0, overall_split[0])
        else:
            base_prediction_row = overall_split
        prediction_base = self.create_prediction_value(base_prediction_row)
        base_prediction_row.append(prediction_base)
        return base_prediction_row

    def strange_computation(self, useful_splits):
        overall_split = useful_splits[1][0]
        overall_split = self.filter_split(overall_split)
        base_prediction_row = self.create_base_prediction_row(overall_split)
        return base_prediction_row

    def standard_computation(self, useful_splits):
        overall_split = useful_splits[1][0]
        overall_split = self.filter_split(overall_split)
        days_rest_split = useful_splits[1][1]
        days_rest_split = self.filter_split(days_rest_split)
        where_to_play_split = useful_splits[1][2]
        where_to_play_split = self.filter_split(where_to_play_split)
        base_prediction_row = self.create_base_prediction_row(
            overall_split, days_rest_split, where_to_play_split)
        return base_prediction_row

    def compute_predictions(self, season, player, position_player,
                            splits_player, days_rest_player, vs_team,
                            where_to_play):
        useful_splits = [[], []]
        # print("dentro!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # pprint(splits_player)
        if splits_player.get('all splits') is None:
            return None
        useful_splits[1].append(splits_player['all splits'])
        useful_splits[0].append('overall')
        if splits_player.get(str(days_rest_player) + ' days rest',
                             None) is not None:
            useful_splits[1].append(
                splits_player[str(days_rest_player) + ' days rest'])
            useful_splits[0].append('rest')
        elif splits_player.get(str(days_rest_player) + '+ days rest',
                               None) is not None:
            useful_splits[1].append(
                splits_player[str(days_rest_player) + '+ days rest'])
            useful_splits[0].append('rest')
        if splits_player.get(where_to_play, None) is not None:
            useful_splits[1].append(splits_player[where_to_play])
            useful_splits[0].append('where')
        if len(useful_splits[0]) < 3:
            base_prediction_row = self.strange_computation(useful_splits)
        else:
            base_prediction_row = self.standard_computation(useful_splits)
        return base_prediction_row

    def compute_offset(
            self,
            player,
            role_player,
            row_prediction_player,
            row_opponent_stats,
    ):
        '''
        print(row_prediction_player)
        print("------------")
        print(row_opponent_stats)
        print("------------")
        '''
        mins_player = row_prediction_player['MIN']
        n_player_g = 1.65  # to think better
        n_player_f = 1.65
        n_player_c = 1
        if role_player == 'G':
            row_opponent_stats = [
                float(elem) / n_player_g for elem in row_opponent_stats
            ]
        elif role_player == 'A':
            row_opponent_stats = [
                float(elem) / n_player_f for elem in row_opponent_stats
            ]
        elif role_player == 'C':
            row_opponent_stats = [
                float(elem) / n_player_c for elem in row_opponent_stats
            ]
        for i in range(1, len(row_prediction_player) - 1):
            offset_temp = (float(row_opponent_stats[i - 1]) / 48) * mins_player
            offset = offset_temp - row_prediction_player[i]
            row_prediction_player[i] += (offset * 0.3)
        prediction_player = self.create_prediction_value(row_prediction_player)
        self.players_filtered[player][4] = prediction_player
        row_prediction_player = list(row_prediction_player)
        row_prediction_player[-1] = prediction_player
        #print(player, self.players_filtered[player])
        self.append_row_to_csv(
            str(player), list(row_prediction_player), offset=True)

    def add_offset_opponent(self, player, data_player):
        row_prediction_player = self.predictions_rows_dict.get(player)
        if row_prediction_player is None:
            return None
        next_game_player = self.next_game_dict[data_player[0]]
        vs_team = next_game_player[1]
        print("vs team: {}".format(vs_team))
        role_player = data_player[1]
        rows_opponent_stats = {}
        if role_player == 'G':
            rows_opponent_stats = self.opponent_stats_G
        elif role_player == 'A':
            rows_opponent_stats = self.opponent_stats_F
        elif role_player == 'C':
            rows_opponent_stats = self.opponent_stats_C
        row_opponent_stats = rows_opponent_stats[vs_team]
        row_opponent_stats = [
            row_opponent_stats[24], row_opponent_stats[5],
            row_opponent_stats[6], row_opponent_stats[11],
            row_opponent_stats[12], row_opponent_stats[14],
            row_opponent_stats[15], row_opponent_stats[17],
            row_opponent_stats[18], row_opponent_stats[19],
            row_opponent_stats[20]
        ]
        self.compute_offset(player, role_player, row_prediction_player,
                            row_opponent_stats)
        #print(mins_player, vs_team, row_opponent_stats)

    def main(self, splits_already_saved, add_offset):
        self.compute_next_game_all_teams()
        if splits_already_saved:
            if add_offset:
                self.post_main()
            else:
                self.load_csv_predictions()
                for p, data in self.players_filtered.items():
                    if self.predictions_rows_dict.get(p) is not None:
                        self.players_filtered[p][
                            4] = self.predictions_rows_dict[p][-1]
            return self.players_filtered
        season = self.config['SEASON']
        self.create_csv_predictions(offset=False)
        if os.path.isfile(self.PATH_DATA + 'full_players_splits.json'):
            os.remove(self.PATH_DATA + 'full_players_splits.json')
        total_players = len(self.players_filtered)
        index = 1
        for player, data_player in self.players_filtered.items():
            print(player, str(index) + ' of ' + str(total_players))
            next_game_player = self.next_game_dict[data_player[0]]
            print("next game player: {}".format(next_game_player))
            days_rest_player = next_game_player[3]
            id_player = self.players_name_id_espn.get(player, None)
            print("id player: {}".format(id_player))
            if id_player is None:
                index += 1
                continue
            splits_player = splits_espn.get_splits_player(id_player)
            if splits_player is None or len(splits_player) == 0:
                index += 1
                continue
            vs_team = next_game_player[1]
            print("vs: {}".format(vs_team))
            position_player = data_player[1]
            where_to_play = next_game_player[0]
            splits_to_write = {player: splits_player}
            if os.path.isfile(self.PATH_DATA + 'full_players_splits.json'):
                with open(self.PATH_DATA + 'full_players_splits.json',
                          'a') as outfile:
                    json.dump(splits_to_write, outfile)
            else:
                with open(self.PATH_DATA + 'full_players_splits.json',
                          'w') as outfile:
                    json.dump(splits_to_write, outfile)
            base_prediction_row = self.compute_predictions(
                season, player, position_player, splits_player,
                days_rest_player, vs_team, where_to_play)
            print(base_prediction_row)
            if base_prediction_row is not None:
                self.append_row_to_csv(
                    player, base_prediction_row, offset=False)
                if not add_offset:
                    self.players_filtered[player][4] = base_prediction_row[-1]
            index += 1
            print("--------")
        if add_offset:
            self.post_main()
        with open(self.PATH_DATA + 'players_filtered.json',
                  'w') as outfile:
            json.dump(self.players_filtered, outfile)
        return self.players_filtered

    def post_main(self):
        self.create_dict_opponent_stats_all_teams()
        self.create_csv_predictions(offset=True)
        self.load_csv_predictions()
        for player, data_player in self.players_filtered.items():
            self.add_offset_opponent(player, data_player)
