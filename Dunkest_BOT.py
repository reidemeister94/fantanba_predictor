import wget
import csv
from pathlib import Path
import os
import json
from pprint import pprint
import requests
import urllib3
import ssl
from utils import scraper, minor_things_helper
from predictor import predictor
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context


class dunkest_bot:
    def __init__(self):
        print("Bot started")
        print("--------------------------------------")
        self.turn_number = 0
        self.credits_total = 0.0
        self.credits_computed = 0.0
        self.games = []
        self.games_list = []
        self.players_filtered = {}
        self.coaches_filtered = {}
        self.players_only = []
        self.predictions = []
        self.costs = []
        self.roles = []
        self.predicted_fantasy_pts = []
        self.teams_and_bets_from_sisal = {}
        self.coach_selected = []
        self.keep_players = []
        self.total_cost = 0
        self.total_points = 0
        self.ROTOGRINDER = True
        self.players_filtered_by_score = []
        self.portfolio = []
        self.players = {}
        self.coaches = {}
        self.guards_keeped = 0
        self.forwards_keeped = 0
        self.centers_keeped = 0
        self.captain_keeped = False
        self.bench_keeped = 0
        self.rotowire_proj = {}
        self.list_all_combinations = []
        self.captain_flags = []
        self.bench_flags = []
        self.remove_players = []
        self.teams_nba = []
        self.code_teams = {}
        self.scraper = None
        self.predictor = None

    def start_chrome(self):
        self.scraper = scraper.scraper()

    def download_dunkest_players(self):
        self.credits_computed = 96.4
        self.credits_total = 96.4
        response = requests.get(
            'https://api.dunkest.com/api/players?league_id=1', verify=False)
        json_data = json.loads(response.text)
        for player in json_data:
            first_name_player = player["name"]
            surname_player = player["surname"]
            name_player = (first_name_player +
                           " " + surname_player).strip().lower().replace(
                               ".", "").replace('byombo', 'biyombo').replace(
                                   'malcom', 'malcolm').replace(
                                       'mohamed bamba', 'mo bamba').replace(
                                           'hilario nene',
                                           'nene hilario').replace(
                                               'kelly oubre',
                                               'kelly oubre jr').replace(
                                                   'edrice adebayo',
                                                   'bam adebayo')
            name_team = player["team_name"].lower().strip()
            position = minor_things_helper.compute_position(player["role_tag"])
            credits_player = player["quotation"]
            if position == "HC":
                self.coaches[name_player] = [
                    name_team.lower(), credits_player, 0.0
                ]
            else:
                # player = [name team, position, cost, score, fantasy pts
                # predicted]
                if player['lineup_tag'] != 'QUESTIONABLE' and player['lineup_tag'] != 'INJURED' and player[
                        'lineup_tag'] != 'DISQUALIFIED' and 'IN_DOUBT' not in player['lineup_tag']:
                    self.players[name_player] = [
                        name_team.lower(), position, credits_player, 0.0, 0.0
                    ]
        self.create_dicts()

    def download_games(self):
        response_round_number = requests.get(
            'https://api.dunkest.com/api/rounds/current?league_id=1&fanta_league_id=1',
            verify=False)
        self.turn_number = json.loads(response_round_number.text)['id']
        response = requests.get(
            'https://api.dunkest.com/api/rounds/' +
            str(self.turn_number) + '/games/v2',
            verify=False)
        json_data = json.loads(response.text)
        for game in json_data["games"]:
            away_team = game["away_team_name"].lower().strip()
            home_team = game["home_team_name"].lower().strip()
            self.games.append([away_team, home_team])
            if home_team not in self.games_list:
                self.games_list.append(home_team)
            if away_team not in self.games_list:
                self.games_list.append(away_team)

    def check_last_page(self):
        return self.scraper.check_last_page()

    def scraping_bets(self):
        ##SCRAPING BETS FOR THE GAMES TO BE PLAYED##
        self.scraper.scraping_bets(self)

    def compute_predictions(self, splits_already_saved=False,
                            add_offset=False):
        print("--------------------------------------")
        print("Initializing the predictor instance..")
        self.predictor = predictor.predictor(self)
        print("Predictor initialized")
        print("--------------------------------------")
        print("Computing the predictions for every player")
        self.players_filtered = self.predictor.main(splits_already_saved,
                                                    add_offset)
        print("Predictions computed")
        print("--------------------------------------")
        # pprint(self.players_filtered)
        print(
            "Creating lists useful for selecting the best mix of payers later on"
        )
        self.create_list_with_captain_bench()
        self.fill_list_all_combinations()
        print("Completed")
        print("--------------------------------------")

    '''
    def download_predictions_rotowire(self):
        response = requests.get(
            'https://www.rotowire.com/daily/tables/optimizer-nba.php?sport=NBA&site=FanDuel&projections=&type=main&slate=Main',
            verify=False)
        json_data = json.loads(response.text)
        for elem in json_data:
            first_name_player = elem["first_name"]
            surname_player = elem["last_name"]
            name_player = (first_name_player + " " +
                           surname_player).strip().lower().replace(".", "")
            pts = elem["proj_points"]
            self.rotowire_proj[name_player] = float(pts)


    def download_data_projections(self):
        ##download projections and connect them to dunkest data##
        # sportsline_url = "https://www.sportsline.com/sportsline-web/service/v1/playerProjectionsCsv?league=nba&position=all-players&sourceType=FD&page=PS&desc=false&optimal=false"
        rotogrinder_url = "https://rotogrinders.com/projected-stats/nba-player.csv?site=fanduel"
        rotogrinder_file = Path(
            "/Users/silvio/OneDrive - Politecnico di Milano/kingpredictor_fantanba/data/nba-player.csv"
        )
        if rotogrinder_file.is_file():
            # file exists
            os.remove(
                "/Users/silvio/OneDrive - Politecnico di Milano/kingpredictor_fantanba/data/nba-player.csv"
            )
        wget.download(
            rotogrinder_url,
            "/Users/silvio/OneDrive - Politecnico di Milano/kingpredictor_fantanba/data/"
        )
    '''

    ##ALL THE DATA HAVE BEEN COLLECTED, NOW JUST LOGIC##

    def create_dicts(self):
        for key, value in self.players.items():
            if value[0] in self.games_list:
                self.players_filtered[key] = self.players[key]

        for key, value in self.coaches.items():
            if value[0] in self.games_list:
                self.coaches_filtered[key] = self.coaches[key]

    def create_list_with_captain_bench(self):
        for k, v in self.players_filtered.items():
            default = (k, [v[0], v[1], v[2], v[3], v[4], False, False])
            captain = (str(k) + "_captain",
                       [v[0], v[1], v[2], v[3], v[4] * 2, True, False])
            bench = (str(k) + "_bench",
                     [v[0], v[1], v[2], v[3], v[4] / 2, False, True])
            self.list_all_combinations.append(default)
            self.list_all_combinations.append(captain)
            self.list_all_combinations.append(bench)

    def fill_list_all_combinations(self):
        for k, v in self.list_all_combinations:
            self.players_only.append(k)
            self.teams_nba.append(v[0])
            self.roles.append(v[1])
            self.costs.append(v[2])
            self.predictions.append(v[3])
            self.predicted_fantasy_pts.append(float(v[4]))
            self.captain_flags.append(v[5])
            self.bench_flags.append(v[6])
        self.players_filtered_by_score = sorted(
            self.players_filtered.items(), key=lambda e: e[1][3], reverse=True)

    def fill_list_not_combinations(self):
        for k, v in self.players_filtered.items():
            self.players_only.append(k)
            self.teams_nba.append(v[0])
            self.roles.append(v[1])
            self.costs.append(v[2])
            self.predictions.append(v[3])
            self.predicted_fantasy_pts.append(float(v[4]))
        self.players_filtered_by_score = sorted(
            self.players_filtered.items(), key=lambda e: e[1][3], reverse=True)

    def close_webdriver(self):
        self.scraper.driver.quit()

    def compute_offset_prediction(self, name_player):
        team_player = self.players_filtered[name_player][0]
        bet_team = self.teams_and_bets_from_sisal.get(team_player)
        if bet_team is not None:
            prob_win = 1 / float(bet_team)
            if prob_win > 0.5:
                offset_win = 3 * prob_win
            else:
                offset_win = -3 * (1 - prob_win)
            return offset_win, 0
        return 0, 0

    '''
    ##ROTOGRINDER##
    def join_projections_dunkest(self):
        # print("filtered: ")
        # print(self.players_filtered)
        with open(
                "/Users/silvio/OneDrive - Politecnico di Milano/kingpredictor_fantanba/data/nba-player.csv",
                'r') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                name_p = row[0].lower().strip().replace(".", "")
                if name_p in self.players_filtered.keys():
                    low = float(row[6].strip())
                    high = float(row[5].strip())
                    proj_rotogrinder = float(row[7])
                    rotowire = self.rotowire_proj.get(name_p)
                    # if rotogrinder has the low and high prediction
                    win_offset, place_offset = self.compute_offset_prediction(
                        name_p)
                    proj_rotogrinder += win_offset
                    if rotowire != None:
                        rotowire += win_offset
                    high += win_offset
                    low += win_offset
                    if len(row[6].strip()) > 0:
                        if rotowire != None:
                            if rotowire != 0:
                                # old
                                # score = (low/high)*roto
                                # new
                                score = (rotowire - low) / (high - low)
                                # print(rotowire,high,low,score)
                                self.players_filtered[name_p][4] = rotowire
                        else:
                            # old
                            # score = (low/high)*proj_rotogrinder
                            # new
                            score = (proj_rotogrinder - low) / (high - low)
                            # print(proj_rotogrinder,high,low,score)
                            self.players_filtered[name_p][4] = proj_rotogrinder
                        self.players_filtered[name_p][3] = score
                    else:
                        if rotowire != None:
                            if rotowire != 0:
                                self.players_filtered[name_p][4] = rotowire
                        else:
                            self.players_filtered[name_p][4] = proj_rotogrinder
        self.create_list_with_captain_bench()
        self.fill_list_all_combinations()
    '''

    def select_coach(self):
        ##SELECT THE BEST COACH##
        for k, v in self.coaches_filtered.items():
            if self.teams_and_bets_from_sisal.get(v[0]) is not None:
                score = 1 / (
                    self.teams_and_bets_from_sisal[v[0]] * float(v[1]))
                self.coaches_filtered[k] = [v[0], v[1], score]
        coaches_sorted = sorted(
            self.coaches_filtered.items(), key=lambda e: e[1][2], reverse=True)
        self.coach_selected = coaches_sorted[0]
        self.total_cost += self.coach_selected[1][1]

    def override_credits(self):
        self.credits_computed = float(
            input("Number of credits of your team: " + "\n"))
        self.credits_total = self.credits_computed

    def remove_players_choosed(self, name_to_check):
        for p in self.players_only:
            index = self.players_only.index(p)
            if p.startswith(name_to_check):
                self.teams_nba.pop(index)
                self.players_only.pop(index)
                self.roles.pop(index)
                self.predictions.pop(index)
                self.costs.pop(index)
                self.predicted_fantasy_pts.pop(index)

    def check_remove_players_correctly(self):
        count = 0
        for i in range(0, len(self.remove_players)):
            for j in range(0, len(self.players_only)):
                if self.players_only[j].startswith(self.remove_players[i]):
                    count += 1
                    index = j
                    self.players_only.pop(index)
                    self.teams_nba.pop(index)
                    self.roles.pop(index)
                    self.predictions.pop(index)
                    self.costs.pop(index)
                    self.predicted_fantasy_pts.pop(index)
                    break
        if count == 0:
            return True
        else:
            return False

    def remove_players_choice(self):
        self.remove_players = [
            str(x).lower().strip() for x in input(
                "Insert a list of players you want to remove, separated by a comma: "
            ).split(",")
        ]
        for i in range(0, len(self.remove_players)):
            print(self.remove_players[i])
            if (len(self.remove_players[i]) == 0) or (
                    self.remove_players[i] not in self.players_filtered):
                self.remove_players.pop(i)
        finished = self.check_remove_players_correctly()
        while finished is not True:
            finished = self.check_remove_players_correctly()

    def keep_players_choice(self):
        correctness = False
        while correctness is not True:
            count_captain = 0
            count_bench = 0
            self.keep_players = [
                str(x).lower().strip() for x in input(
                    "Insert a list of players you want to keep, separated by a comma: "
                ).split(",")
            ]
            for elem in self.keep_players:
                if len(elem.split("_")) > 1:
                    if elem.split("_")[1] == "captain":
                        count_captain += 1
                if len(elem.split("_")) > 1:
                    if elem.split("_")[1] == "bench":
                        count_bench += 1
            if count_captain > 1 or count_bench > 4:
                print(
                    "Choice not correct. There must be only 1 captain and at most 4 player in the bench."
                )
            else:
                correctness = True

        for i in range(0, len(self.keep_players)):
            if (len(self.keep_players[i]) == 0) or (self.keep_players[i].split(
                    "_")[0] not in self.players_filtered):
                self.keep_players.pop(i)
        self.credits_computed = self.credits_computed - sum(
            self.players_filtered[elem.split("_")[0]][2]
            for elem in self.keep_players)

        self.list_all_combinations = dict(self.list_all_combinations)

        for i in range(0, len(self.keep_players)):
            if self.players_filtered[self.keep_players[i].split("_")
                                     [0]][1] == "G":
                self.guards_keeped += 1
            if self.players_filtered[self.keep_players[i].split("_")
                                     [0]][1] == "A":
                self.forwards_keeped += 1
            if self.players_filtered[self.keep_players[i].split("_")
                                     [0]][1] == "C":
                self.centers_keeped += 1
            if len(self.keep_players[i].split("_")) > 1:
                if self.keep_players[i].split("_")[1] == "captain":
                    self.captain_keeped = True
            if len(self.keep_players[i].split("_")) > 1:
                if self.keep_players[i].split("_")[1] == "bench":
                    self.bench_keeped += 1
            name_to_check = self.keep_players[i].split("_")[0]
            self.remove_players_choosed(name_to_check)
            self.remove_players_choosed(name_to_check)
            self.total_cost += self.list_all_combinations[self.
                                                          keep_players[i]][2]
            self.total_points += self.list_all_combinations[self.
                                                            keep_players[i]][4]

    def select_coach_choice(self):
        correct_init = False
        coach_choiche = ""
        while correct_init is not True:
            coach_choiche = str(
                input(
                    "Do you want to select your coach manually? YES for inserting it, NO for letting the bot to choose it for you." +
                    "\n")).lower().strip()
            if coach_choiche != "yes" and coach_choiche != "no":
                print("Answer not correct, insert yes or no.")
                print()
            else:
                correct_init = True
        if coach_choiche == "yes":
            correct = False
            while correct is not True:
                choice_coach = str(
                    input("Insert the name of the coach that you want: " +
                          "\n")).lower().strip()
                if choice_coach not in self.coaches_filtered:
                    print(
                        "The coach that you choosed is not valid. Choose a valid coach for tonight games."
                    )
                    print()
                else:
                    correct = True
                    self.coach_selected = [
                        choice_coach, self.coaches_filtered[choice_coach]
                    ]
                    self.total_cost += self.coaches_filtered[choice_coach][1]
        else:
            self.select_coach()
