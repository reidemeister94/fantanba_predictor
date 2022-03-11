import csv
import json
import pandas as pd
from pprint import pprint

players_dict = {}
df = pd.read_csv('../../../data/list_players_espn.csv', header=0)
for index, row in df.iterrows():
    name_player = row['name_player'].strip().lower().replace('.', '')
    id_player = row['link_id']
    index_id = id_player.find('id')
    id_player = id_player[index_id + 3:].strip()
    players_dict[name_player] = id_player

with open('../../../data/players_nba_espn.json', 'w') as outfile:
    json.dump(players_dict, outfile)
