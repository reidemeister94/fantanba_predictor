import requests
import urllib3
import ssl
import random
import string
import json
import ast
from itertools import cycle
from pprint import pprint
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def call_general_splits(id_player, proxies):
    user_agent_string = randomword(random.randint(5, 15))
    params = {
        "MeasureType": "Base",
        "PerMode": "PerGame",
        "PlusMinus": "N",
        "PaceAdjust": "N",
        "Rank": "N",
        "LeagueID": "00",
        "Season": "2019-20",
        "SeasonType": "Regular Season",
        "PORound": 0,
        "PlayerID": id_player,
        "Outcome": "",
        "Location": "",
        "Month": 0,
        "SeasonSegment": "",
        "DateFrom": "",
        "DateTo": "",
        "OpponentTeamID": 0,
        "VsConference": "",
        "VsDivision": "",
        "GameSegment": "",
        "Period": 0,
        "ShotClockRange": "",
        "LastNGames": 0
    }
    headers = {"User-Agent": user_agent_string}
    random.shuffle(proxies)
    proxy_pool = cycle(proxies)
    proxy = next(proxy_pool)
    #print(proxy)
    response = requests.get(
        'https://stats.nba.com/stats/playerdashboardbygeneralsplits',
        params=params,
        headers=headers,
        #proxies={
        #    "http": "http://" + str(proxy),
        #    "https": "https://" + str(proxy)
        #},
        verify=False)
    return response


def update_splits_dict(split, splits_dict):
    splits_dict[split[1].strip().lower().replace('road', 'away')] = split[2:-1]
    return splits_dict


def compute_general_splits(id_player, proxies):
    splits_dict = {}
    splits_player = call_general_splits(id_player, proxies).text
    splits_player = json.loads(splits_player)['resultSets']
    for elem in splits_player:
        for key, values in elem.items():
            if key == 'rowSet':
                for split in values:
                    splits_dict = update_splits_dict(split, splits_dict)
    return splits_dict
