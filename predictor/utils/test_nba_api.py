import requests
import urllib3
import ssl
import random
import string
from pprint import pprint
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


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
        "StarterBench": ""
    }

    user_agent_string = randomword(random.randint(3, 25))

    headers = {"User-Agent": user_agent_string}
    response = requests.get(
        'https://stats.nba.com/stats/leaguedashteamstats',
        params=params,
        headers=headers,
        verify=False)
    return response.text
