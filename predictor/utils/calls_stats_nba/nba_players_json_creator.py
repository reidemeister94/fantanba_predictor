import csv
import json


def sanitize_name(name_player_temp):
    name_player = name_player_temp[1].replace('_', ' ').replace(
        '.', '').lower().strip()
    surname_player = name_player_temp[0].replace('_', ' ').replace(
        '.', '').lower().strip()
    return name_player, surname_player


players_dict = {}
with open('../../../data/players_nba.csv', mode='r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter='\t')
    for row in csv_reader:
        name_player_temp = row[0].split(',')
        if len(name_player_temp) > 1:
            name_player, surname_player = sanitize_name(name_player_temp)
            name_player_final = (name_player + " " + surname_player)
        else:
            name_player = (name_player_temp[0]).lower().strip().replace(
                '.', '').replace('_', ' ')
        id_player = row[1]
        players_dict[name_player_final] = id_player

with open('../../../data/players_nba.json', 'w') as outfile:
    json.dump(players_dict, outfile)
