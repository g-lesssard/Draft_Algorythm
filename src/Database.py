import logging

import requests
import csv
import os
import numpy as np
import difflib
import re
from enum import Enum
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

confirmation_mutex = Lock()


class Filters(Enum):
    id = 0
    fullname = 1
    points_last_season = 2
    average_last_seasons = 3
    transferred = 4
    drafted = 5


similarity_level = 0.8

filters = ['ID', 'Full Name', 'Points Last Season', 'Average Last Seasons', 'Transferred', 'Drafted']
active_seasons = ["20212022", "20202021", "20192020"]

if not os.path.exists("../outputs"):
    os.makedirs("../outputs")


def isForward(code):
    return (code == 'R' or code == 'L' or code == 'C')


def isDefensemen(code):
    return code == 'D'


def isGoalie(code):
    return code == 'G'


def addPlayer(player, players, drafted_players, current_team_id):
    stats = requests.get(
        "https://statsapi.web.nhl.com" + str(player["person"]["link"]) + "/stats?stats=yearByYear").json()
    pointsLastSeason = 0
    average = 0
    count = 0
    drafted = 0
    transferred = 0
    try:
        seasons = stats["stats"][0]["splits"]
        pointsLastSeason = seasons[-1]["stat"]["points"]
        for season in seasons[-min(3, len(seasons)):]:
            average += season["stat"]["points"]
            count += 1

        if count:
            average /= count

        transferred = int(seasons[-1]["team"]["id"] != current_team_id)

        if max([difflib.SequenceMatcher(None, player['person']['fullName'].upper().split(" ")[-1], d).ratio() for d in
                drafted_players]) >= similarity_level:
            drafted = 1

        players.writerow({filters[Filters.id.value]: player['person']['id'],
                          filters[Filters.fullname.value]: player['person']['fullName'],
                          filters[Filters.points_last_season.value]: pointsLastSeason,
                          filters[Filters.average_last_seasons.value]: average,
                          filters[Filters.transferred.value]: transferred,
                          filters[Filters.drafted.value]: drafted})
    except KeyError:
        pass
    return drafted


def addGoalie(player, team, goalies, drafted_players, current_team_name):
    statsLastSeason = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(
        player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=" + active_seasons[0]).json()
    pointsLastSeason = 0
    average = 0
    count = 0
    drafted = 0
    try:
        pointsLastSeason = statsLastSeason["stats"][0]["splits"][0]["stat"]["wins"] * 2 + \
                           statsLastSeason["stats"][0]["splits"][0]["stat"]["ties"]
        average += pointsLastSeason
        count += 1
    except:
        pass
    stats = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(
        player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=" + active_seasons[1]).json()
    try:
        average += stats["stats"][0]["splits"][0]["stat"]["wins"] * 2 + stats["stats"][0]["splits"][0]["stat"]["ties"]
        count += 1
    except:
        pass
    stats = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(
        player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=" + active_seasons[2]).json()
    try:
        average += stats["stats"][0]["splits"][0]["stat"]["wins"] * 2 + stats["stats"][0]["splits"][0]["stat"]["ties"]
        count += 1
    except:
        pass
    if (count):
        average /= count

    if max([difflib.SequenceMatcher(None, player['person']['fullName'].upper().split(" ")[-1], d).ratio() for d in
            drafted_players]) >= similarity_level:
        drafted = 1

    goalies.writerow({filters[Filters.id.value]: player['person']['id'],
                      filters[Filters.fullname.value]: player['person']['fullName'],
                      filters[Filters.points_last_season.value]: pointsLastSeason,
                      filters[Filters.average_last_seasons.value]: average,
                      filters[Filters.transferred.value]: current_team_name,
                      filters[Filters.drafted.value]: drafted})
    return drafted


def analysePlayersFromTeam(team_id, team_name, forwards, defensemen, goalies, drafted_players):
    request = "https://statsapi.web.nhl.com/api/v1/teams/" + str(team_id) + "/roster"
    roster = requests.get(request).json()["roster"]
    drafted_count = 0
    for player in roster:
        if isForward(player["position"]["code"]):
            drafted_count += addPlayer(player, forwards, drafted_players["forwards"], team_id)
            pass
        elif isDefensemen(player["position"]["code"]):
            drafted_count += addPlayer(player, defensemen, drafted_players["defensemen"], team_id)
            pass
        elif isGoalie(player["position"]["code"]):
            drafted_count += addGoalie(player, team_id, goalies, drafted_players["goalies"], team_name)

    return drafted_count


def generatePlayerList():
    forwardsFile = open('../outputs/forwards.csv', 'w+', newline='')
    forwards = csv.DictWriter(forwardsFile, fieldnames=filters)

    defensemenFile = open('../outputs/defensemen.csv', 'w+', newline='')
    defensemen = csv.DictWriter(defensemenFile, fieldnames=filters)

    goaliesFile = open('../outputs/goalies.csv', 'w+', newline='')
    goalies = csv.DictWriter(goaliesFile, fieldnames=filters)

    drafted_players = generated_forbidden_lists()
    expected_drafted_count = 0
    for el in drafted_players.items():
        expected_drafted_count += len(el[1])
    total_drafted_count = 0

    forwards.writeheader()
    defensemen.writeheader()
    goalies.writeheader()

    teams = dict()

    for team in requests.get("https://statsapi.web.nhl.com/api/v1/teams").json()["teams"]:
        teams.update({team["id"]: team["name"]})

    with tqdm(total=len(teams), desc="Generating Database", colour="green") as pbar:
        with ThreadPoolExecutor(max_workers=len(teams)) as executors:
            futures = [
                executors.submit(analysePlayersFromTeam, t, teams[t], forwards, defensemen, goalies, drafted_players)
                for t in teams]
            for future in as_completed(futures):
                total_drafted_count += future.result()
                pbar.update(1)

    print("CSVs generated")
    if total_drafted_count == len(drafted_players):
        logging.info("Found same number of drafted players than from list")
    else:
        logging.warning(f"Drafted player count differs from number of forbidden players. Found {total_drafted_count}"
                        f" drafted players instead of {expected_drafted_count}")
    pass

def generated_forbidden_lists():
    drafted_players = dict()

    text_file = open(os.path.join(os.getcwd(), "../forbidden_forwards.raw"), 'r', encoding="utf8")
    as_string = text_file.read()

    drafted_players.update({"forwards": as_string.split()})

    text_file = open(os.path.join(os.getcwd(), "../forbidden_defensemen.raw"), 'r', encoding="utf8")
    as_string = text_file.read()
    drafted_players.update({"defensemen": as_string.split()})

    text_file = open(os.path.join(os.getcwd(), "../forbidden_goalies.raw"), 'r', encoding="utf8")
    as_string = text_file.read()
    drafted_players.update({"goalies": as_string.split()})

    return drafted_players




def test_forbidden_players():
    drafted_players = generated_forbidden_lists()
    expected_drafted_count = 0
    for el in drafted_players.items():
        expected_drafted_count += len(el[1])

    drafted_name = "Torey Claude Krug"
    non_drafted_name = "Jean Guy"
    diff1 = [difflib.SequenceMatcher(None, drafted_name.upper().split(" ")[-1], d).ratio() for d in drafted_players]
    diff2 = [difflib.SequenceMatcher(None, non_drafted_name.upper().split(" ")[-1], d).ratio() for d in drafted_players]
    r1 = max([difflib.SequenceMatcher(None, drafted_name.upper(), d).ratio() for d in drafted_players])
    if r1 > 0.2:
        a = 0

    r2 = max(
        [difflib.SequenceMatcher(None, non_drafted_name.upper().split(" ")[1], d).ratio() for d in drafted_players])
    if r2 > 0.2:
        a = 0


if __name__ == "__main__":
    generatePlayerList()
    test_forbidden_players()
