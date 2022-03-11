from pulp import *


def maximization_scores(dunkest_bot, order_by_score, order_by_pts):
    P = range(len(dunkest_bot.players_only))
    # Declare problem instance, maximization problem
    prob = LpProblem("Portfolio", LpMaximize)
    # Declare decision variable x, which is 1 if a
    # player is part of the portfolio and 0 else
    x = LpVariable.matrix("x", list(P), 0, 1, LpInteger)
    # Objective function -> Maximize votes
    if order_by_score:
        prob += sum(dunkest_bot.predictions[p] * x[p] for p in P)
    if order_by_pts:
        prob += sum(dunkest_bot.predicted_fantasy_pts[p] * x[p] for p in P)
    # Constraint definition #

    # constraint for the number of players in the team
    prob += sum(x[p] for p in P) == 10 - len(dunkest_bot.keep_players)
    # constraint on the total amount of credits
    prob += sum(dunkest_bot.costs[p] * x[p] for p in P) <= (
        dunkest_bot.credits_computed - dunkest_bot.coach_selected[1][1])
    # constraints for the numbers of players for every role
    prob += sum(
        x[p] for p in P
        if dunkest_bot.roles[p] == "G") == 4 - dunkest_bot.guards_keeped
    prob += sum(
        x[p] for p in P
        if dunkest_bot.roles[p] == "A") == 4 - dunkest_bot.forwards_keeped
    prob += sum(
        x[p] for p in P
        if dunkest_bot.roles[p] == "C") == 2 - dunkest_bot.centers_keeped
    # constraint for having every player only once in the final team
    for elem in dunkest_bot.players_only:
        prob += sum(x[p] for p in P if dunkest_bot.players_only[p].split("_")
                    [0] == elem.split("_")[0]) <= 1

    # constraint for having at most n players of the same team
    for team in dunkest_bot.teams_nba:
        # check team of players keeped
        count = 0
        for elem in dunkest_bot.keep_players:
            elem = elem.split("_")[0]
            pl_team = dunkest_bot.players_filtered[elem][0]
            if team == pl_team:
                count += 1
        if team == dunkest_bot.coach_selected[1][0]:
            prob += sum(x[p] for p in P
                        if dunkest_bot.teams_nba[p] == team) <= 1 - count
        else:
            prob += sum(x[p] for p in P
                        if dunkest_bot.teams_nba[p] == team) <= 2 - count
    # constraints on captain
    if dunkest_bot.captain_keeped:
        prob += sum(
            x[p] for p in P if dunkest_bot.captain_flags[p] == True) == 0
    else:
        prob += sum(
            x[p] for p in P if dunkest_bot.captain_flags[p] == True) == 1

    # constraint on the bench
    prob += sum(
        x[p] for p in P
        if dunkest_bot.bench_flags[p] == True) == 4 - dunkest_bot.bench_keeped
    # constraint for having at least 1 center on the floor
    prob += sum(x[p] for p in P if dunkest_bot.bench_flags[p] == True
                and dunkest_bot.roles[p] == "C") == 1
    # Start solving the problem instance
    prob.solve()
    # Extract solution
    dunkest_bot.portfolio = [(dunkest_bot.players_only[p],
                              dunkest_bot.roles[p], dunkest_bot.costs[p],
                              dunkest_bot.predictions[p],
                              dunkest_bot.predicted_fantasy_pts[p]) for p in P
                             if x[p].varValue]
    dunkest_bot.portfolio = sorted(
        dunkest_bot.portfolio, key=lambda x: x[4], reverse=True)
