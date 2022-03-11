import requests
import urllib3
import ssl
import random
import string
import json
from pprint import pprint
from pathlib import Path
import os.path

path_data = str(Path(os.getcwd()))

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def make_json_stats_per_position(stats, position_player):
    PATH_DATA = path_data + '/data/'

    dict_to_write = {}
    stats = json.loads(stats)
    stats_all_teams = stats['resultSets'][0]['rowSet']
    for team in stats_all_teams:
        name_team = team[1].lower().strip()
        dict_to_write[name_team.replace('la clippers',
                                        'los angeles clippers')] = team[2:-1]
    with open(PATH_DATA + 'opponent_stats_' + position_player + '.json',
              'w') as outfile:
        json.dump(dict_to_write, outfile)


def defense_stats_vs_position(position_player):
    params = {
        "MeasureType": "Opponent",
        "PerMode": "PerGame",
        "PlusMinus": "N",
        "PaceAdjust": "N",
        "Rank": "N",
        "LeagueID": "00",
        "Season": "2019-20",
        "SeasonType": "Regular Season",
        "PORound": 0,
        "Outcome": "",
        "Location": "",
        "Month": 0,
        "SeasonSegment": "",
        "DateFrom": "",
        "DateTo": "",
        "OpponentTeamID": 0,
        "VsConference": "",
        "VsDivision": "",
        "TeamID": 0,
        "Conference": "",
        "Division": "",
        "GameSegment": "",
        "Period": 0,
        "ShotClockRange": "",
        "LastNGames": 0,
        "GameScope": "",
        "PlayerExperience": "",
        "PlayerPosition": position_player,
        "StarterBench": "",
        "TwoWay": 0
    }

    user_agent_string = randomword(random.randint(3, 50))
    headers = {"User-Agent": user_agent_string,
                "x-nba-stats-origin": "stats",
                "Referer": "https://stats.nba.com/teams/opponent/?sort=W&dir=-1"}
    response = requests.get(
        'https://stats.nba.com/stats/leaguedashteamstats',
        params=params,
        headers=headers,
        verify=False)
    return response.text


def main():
    stats = defense_stats_vs_position('G')
    make_json_stats_per_position(stats, 'G')
    stats = defense_stats_vs_position('F')
    make_json_stats_per_position(stats, 'F')
    stats = defense_stats_vs_position('C')
    make_json_stats_per_position(stats, 'C')


main()
