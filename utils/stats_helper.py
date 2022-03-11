import requests
import urllib3
import ssl
import json
from pprint import pprint
from statistics import mean
import pandas as pd
from sklearn.metrics import mean_squared_error
from math import sqrt
from datetime import datetime
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context


def get_current_round():
    response = requests.get(
        'https://api.dunkest.com/api/rounds/current?league_id=1&fanta_league_id=1',
        verify=False)
    current_round = json.loads(response.text)
    return current_round['id']


def get_score_player(id_round, id_player):
    response = requests.get(
        'https://api.dunkest.com/api/players/' + str(id_player)
        + '/details?league_id=1&round_id=' + str(id_round),
        verify=False)
    current_round_stats = json.loads(response.text)
    return current_round_stats['score']


def clean_name(first_name_player, surname_player):
    return (first_name_player + " " + surname_player).strip().lower().replace(
        ".", "").replace('byombo',
                         'biyombo').replace('malcom', 'malcolm').replace(
                             'mohamed bamba', 'mo bamba').replace(
                                 'hilario nene', 'nene hilario').replace(
                                     'kelly oubre', 'kelly oubre jr').replace(
                                         'edrice adebayo', 'bam adebayo')


def get_players_scores(new_round):
    players_list = {}
    id_round = get_current_round()
    if new_round:
        id_round -= 1
    print("id round: {}".format(id_round))
    response = requests.get(
        'https://api.dunkest.com/api/players?league_id=1', verify=False)
    players = json.loads(response.text)
    i = 1
    len_p = len(players)
    for player in players:
        if player['role_tag'] != "COACH" and player['lineup_tag'] != 'QUESTIONABLE'\
           and player['lineup_tag'] != 'INJURED' and player['lineup_tag'] != 'DISQUALIFIED'\
           and 'IN_DOUBT' not in player['lineup_tag']:
            first_name_player = player["name"]
            surname_player = player["surname"]
            name_player = clean_name(first_name_player, surname_player)
            print("{}   {} of {}".format(name_player, i, len_p))
            score = get_score_player(id_round, player['id'])
            players_list[name_player] = (score, player['role_tag'])
            print("score: {}".format(score))
        i += 1
    return players_list


def load_players():
    with open('../data/score_players_official_dunkest.json') as out:
        return json.load(out)


def main(offset=False, new_round=False):
    players_official = get_players_scores(new_round)
    with open('../data/score_players_official_dunkest.json', 'w') as out:
        json.dump(players_official, out)
    #players_official = load_players()
    players_pred = {}
    if offset is False:
        df = pd.read_csv(
            '../data/nba_players_predictions_no_offset.csv', header=0)
    elif offset is True:
        df = pd.read_csv(
            '../data/nba_players_predictions_yes_offset.csv', header=0)
    for index, row in df.iterrows():
        name_player = row['PLAYER NAME'].strip().lower().replace('.', '')
        players_pred[name_player] = row[-1]
    players_official = {
        k: v
        for k, v in players_official.items() if k in players_pred and v != 0
    }
    players_pred = {
        k: v
        for k, v in players_pred.items() if k in players_official
    }
    with open('../data/players_scores_official.json', 'w') as outfile:
        json.dump(players_official, outfile)
    players_official = list(players_official.items())
    players_pred = list(players_pred.items())
    players_official.sort(key=lambda x: x[0])
    players_pred.sort(key=lambda x: x[0])
    y_real = [score_role[0] for p, score_role in players_official]
    y_pred = [score for p, score in players_pred]
    names = [p for p, _ in players_pred]
    roles = [score_role[1] for _, score_role in players_official]
    y_real_g = []
    y_pred_g = []
    y_real_f = []
    y_pred_f = []
    y_real_c = []
    y_pred_c = []
    diff = []
    output_to_write = ""
    for i in range(0, len(names)):
        if y_real[i] != 0:
            print(names[i], roles[i])
            output_to_write += names[i] + "    " + roles[i] + '\n'
            print("y_real: " + str(y_real[i]), "y_pred: " + str(y_pred[i]))
            output_to_write += "y_real: " + str(
                y_real[i]) + "    " + "y_pred: " + str(y_pred[i]) + "\n"
            print("----------")
            output_to_write += "--------------------------------------------\n\n"
            diff.append(abs(y_real[i] - y_pred[i]))
            if roles[i] == 'GUARD':
                y_real_g.append(y_real[i])
                y_pred_g.append(y_pred[i])
            elif roles[i] == 'FORWARD':
                y_real_f.append(y_real[i])
                y_pred_f.append(y_pred[i])
            elif roles[i] == 'CENTER':
                y_real_c.append(y_real[i])
                y_pred_c.append(y_pred[i])
    rms = sqrt(mean_squared_error(y_real, y_pred))
    rms_g = sqrt(mean_squared_error(y_real_g, y_pred_g))
    rms_f = sqrt(mean_squared_error(y_real_f, y_pred_f))
    rms_c = sqrt(mean_squared_error(y_real_c, y_pred_c))
    print("MEAN DIFFERENCE BETWEEN REAL AND PREDICTED: {}".format(mean(diff)))
    print("TOTAL RMS: " + str(rms))
    print("GUARD RMS: " + str(rms_g))
    print("FORWARD RMS: " + str(rms_f))
    print("CENTER RMS: " + str(rms_c))
    output_to_write += "MEAN DIFFERENCE BETWEEN REAL AND PREDICTED: {}".format(
        mean(diff)) + "\n"
    output_to_write += "TOTAL RMS: " + str(rms) + "\n"
    output_to_write += "GUARD RMS: " + str(rms_g) + "\n"
    output_to_write += "FORWARD RMS: " + str(rms_f) + "\n"
    output_to_write += "CENTER RMS: " + str(rms_c) + "\n"
    now = datetime.now()
    now = now.strftime("%d_%m_%Y")
    with open(
            '../data/statistics_' + now + '_round' + str(get_current_round())
            + '.txt', 'w') as out:
        out.write(output_to_write)


main()
