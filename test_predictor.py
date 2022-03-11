import Dunkest_BOT
import sys
import os
from pathlib import Path
from pprint import pprint
import ssl
import urllib3

path_util = Path(os.getcwd())
path_util = str(path_util) + '/predictor/utils/calls_stats_nba/'
sys.path.append(path_util)

import general_splits
from predictor import predictor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context


'''
###CHECK GOODNESS OF OFFSETS###
bot = Dunkest_BOT.dunkest_bot()
bot.download_games()
bot.download_dunkest_players()
predictor = predictor.predictor(bot)
predictor.main(False,False)
#predictor.compute_next_game_all_teams()
#predictor.check_difference_no_yes_offset()
'''
# pprint(general_splits.compute_general_splits(2216))
bot = Dunkest_BOT.dunkest_bot()
print("Downloading games data from dunkest")
bot.download_games()
print("Games data downloaded")
print("Downloading players data from dunkest")
bot.download_dunkest_players()
print("Players data downloaded")
predictor = predictor.predictor(bot)
# pprint(predictor.players_filtered)

predictor.main(False, True)
# predictor.main_append(347)
# predictor.load_csv_predictions()
# predictor.compute_next_game_all_teams()
# predictor.post_main()
#predictor.add_offset_opponent('lonzo ball', ['los angeles lakers', 'G'])
