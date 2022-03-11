def final_print(dunkest_bot):
    # FINAL PRINT OF THE TEAM, MAXIMIZING THE TOTAL SCORE #
    result_msg = ""
    result_msg += "TOTAL CREDITS AVAILABLE: " + str(
        dunkest_bot.credits_total) + "\n"
    result_msg += "***********************************" + "\n"

    result_msg += "COACH: " + "\n"
    result_msg += "NAME: " + str(dunkest_bot.coach_selected[0].upper()) + "\n"
    result_msg += "TEAM: " + str(
        dunkest_bot.coach_selected[1][0]).upper() + "\n"
    result_msg += "COST: " + str(dunkest_bot.coach_selected[1][1]) + "\n"
    result_msg += ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" + "\n" + "\n"
    result_msg += "PLAYERS" + "\n"

    if len(dunkest_bot.keep_players) > 0:
        for p in dunkest_bot.keep_players:
            result_msg += "PLAYER: " + p.upper() + "\n"
            result_msg += "ROLE: " + str(
                dunkest_bot.list_all_combinations[p][1]) + "\n"
            result_msg += "COST: " + str(
                dunkest_bot.list_all_combinations[p][2]) + "\n"
            #result_msg += "SCORE: " + str(dunkest_bot.list_all_combinations[p][3]) + "\n"
            result_msg += "PREDICTION: " + str(
                dunkest_bot.list_all_combinations[p][4]) + "\n"
            result_msg += "-------------------" + "\n"
    for player_, role, cost, pred, pts in dunkest_bot.portfolio:
        dunkest_bot.total_cost += cost
        dunkest_bot.total_points += pts
        result_msg += "PLAYER: " + player_.upper() + "\n"
        result_msg += "ROLE: " + str(role) + "\n"
        result_msg += "COST: " + str(cost) + "\n"
        #result_msg += "SCORE: " + str(pred) + "\n"
        result_msg += "PREDICTION: " + str(pts) + "\n"
        result_msg += "-------------------" + "\n"
    result_msg += "TOTAL COST: " + str(dunkest_bot.total_cost) + "\n"
    result_msg += "TOTAL POINTS PREDICTED: " + str(dunkest_bot.total_points)
    return result_msg


def print_players_list(dunkest_bot):
    for k, v in dunkest_bot.players_filtered_by_score:
        print(k.upper())
        print("TEAM: " + str(v[0]))
        print("ROLE: " + str(v[1]))
        print("COST: " + str(v[2]))
        print("SCORE: " + str(v[3]))
        print("PREDICTION: " + str(v[4]))
        print("-----------")
