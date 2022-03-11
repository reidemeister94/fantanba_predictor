import requests
import urllib3
import ssl
import random
import string
import json
from pprint import pprint
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def make_call():
    teams_nba_json_dict = {}
    user_agent_string = randomword(random.randint(3, 25))

    headers = {"User-Agent": user_agent_string}
    response = requests.get(
        'https://stats.nba.com/stats/leaguedashteamstats?Conference=&DateFrom=&DateTo=&Division=&GameScope=&GameSegment=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=2019-20&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&TwoWay=0&VsConference=&VsDivision=',
        headers=headers,
        verify=False)
    teams_nba = json.loads(response.text)
    teams_nba = teams_nba['resultSets'][0]['rowSet']
    for team in teams_nba:
        name_team = team[1].strip().lower().replace('la clippers',
                                                    'los angeles clippers')
        teams_nba_json_dict[name_team] = team[0]
    return teams_nba_json_dict


teams_nba_json_dict = make_call()
with open('../../../data/teams_nba.json', 'w') as outfile:
    json.dump(teams_nba_json_dict, outfile)
