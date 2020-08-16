"""this is for ordered dict which can solve counting string"""
# !/usr/bin/env python3
# coding=utf-8
# https://www.php.cn/python-tutorials-358247.html   --refer to this link
from collections import OrderedDict

def main():
    # list of sport teams with wins and losses
    sport_teams = [('Royals', (18, 12)), ('Rockets', (24, 6)),
                   ('Dragons', (22, 8)), ('Kings', (15, 15)),
                   ('Jets', (16, 14)), ('Warriors', (25, 5))]
    # TODO: Sort the team by number of wins
    sorted_teams = sorted(sport_teams, key=lambda t: t[1][0], reverse=True)
    # TODO: Create an ordered dictionary of teams
    teams = OrderedDict(sorted_teams)
    # TODO: use popitem to remove the top item
    tm, wl = teams.popitem(False)    # you can also use True to remove the last one
    print('Top team: ', tm, wl)
    # TODO: what are the next top 4 teams
    for i, team in enumerate(teams, start=1):
        print(i, team)
        if i == 4:
            break
    print(teams.keys())
    print(teams.values())
    teams.move_to_end('Rockets')
    print(teams)




if __name__ == '__main__':
    main()