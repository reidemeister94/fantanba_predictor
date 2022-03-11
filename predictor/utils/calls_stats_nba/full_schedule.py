import requests
import urllib3
import ssl
import random
import string
import json
from pprint import pprint
from datetime import datetime, timedelta
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def full_schedule():
    user_agent_string = randomword(random.randint(3, 25))

    headers = {"User-Agent": user_agent_string}
    response = requests.get(
        'https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2019/league/00_full_schedule_week.json',
        headers=headers,
        verify=False)
    return response.text


with open('../../../data/timezone_teams.json') as json_file:
    timezone_offsets = json.load(json_file)

schedule = full_schedule()
schedule = json.loads(schedule)
output_schedule_dict = {}
months = schedule['lscd']
for month in months:
    games = month['mscd']['g']
    for game in games:
        home_team = (game['h']['tc'].lower() + " " +
                     game['h']['tn'].lower()).strip().replace(
                         'la clippers', 'los angeles clippers')
        away_team = (game['v']['tc'].lower() + " " +
                     game['v']['tn'].lower()).strip().replace(
                         'la clippers', 'los angeles clippers')
        time_game = game['htm'].replace('T', " ")
        time_game = datetime.strptime(time_game, '%Y-%m-%d %H:%M:%S')
        offset_tz = timedelta(hours=timezone_offsets[home_team])
        time_game += offset_tz
        if output_schedule_dict.get(home_team) is None:
            output_schedule_dict[home_team] = [('home', away_team,
                                                str(time_game), 0)]
        else:
            previous_game_time = datetime.strptime(
                output_schedule_dict[home_team][-1][2], '%Y-%m-%d %H:%M:%S')
            days_delta = datetime.strptime(
                time_game.strftime('%Y-%m-%d'),
                '%Y-%m-%d') - datetime.strptime(
                    previous_game_time.strftime('%Y-%m-%d'), '%Y-%m-%d')
            days_rest = len(range(days_delta.days)) - 1
            output_schedule_dict[home_team].append(('home', away_team,
                                                    str(time_game), days_rest))
        if output_schedule_dict.get(away_team) is None:
            output_schedule_dict[away_team] = [('away', home_team,
                                                str(time_game), 0)]
        else:
            previous_game_time = datetime.strptime(
                output_schedule_dict[away_team][-1][2], '%Y-%m-%d %H:%M:%S')
            days_delta = datetime.strptime(
                time_game.strftime('%Y-%m-%d'),
                '%Y-%m-%d') - datetime.strptime(
                    previous_game_time.strftime('%Y-%m-%d'), '%Y-%m-%d')
            days_rest = len(range(days_delta.days)) - 1
            output_schedule_dict[away_team].append(('away', home_team,
                                                    str(time_game), days_rest))
with open('../../../data/full_schedule.json', 'w') as outfile:
    json.dump(output_schedule_dict, outfile)
