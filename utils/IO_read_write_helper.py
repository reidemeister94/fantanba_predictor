import json
import os


def read_data_from_disk(dunkest_bot):
    with open('data/data_computed.txt') as json_file:
        data = json.load(json_file)
        dunkest_bot.players_filtered = data[0]
        dunkest_bot.coaches_filtered = data[1]
        dunkest_bot.credits_total = data[2]
        dunkest_bot.credits_computed = data[2]
        dunkest_bot.teams_and_bets_from_sisal = data[3]
        dunkest_bot.rotowire_proj = data[4]
    dunkest_bot.create_list_with_captain_bench()
    dunkest_bot.fill_list_all_combinations()


def read_data_from_disk_telegram(dunkest_bot):
    with open('data/data_computed.txt') as json_file:
        data = json.load(json_file)
        dunkest_bot.players_filtered = data[0]
        dunkest_bot.teams_and_bets_from_sisal = data[3]
        dunkest_bot.rotowire_proj = data[4]
    dunkest_bot.create_list_with_captain_bench()
    dunkest_bot.fill_list_all_combinations()


def write_data_to_disk(dunkest_bot):
    if os.path.isfile('data/data_computed.txt'):
        os.remove('data/data_computed.txt')
    with open('data/data_computed.txt', 'w') as outfile:
        json.dump([
            dunkest_bot.players_filtered, dunkest_bot.coaches_filtered,
            dunkest_bot.credits_total, dunkest_bot.teams_and_bets_from_sisal,
            dunkest_bot.rotowire_proj
        ], outfile)
