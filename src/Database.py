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


class Filters(Enum):
    id = 0
    fullname = 1
    points_last_season = 2
    average_last_seasons = 3
    drafted = 4


similarity_level = 0.95

filters = ['id', 'fullName', 'points(2020-2021)', 'average(2018-2021)', 'drafted']
active_seasons = ["20202021", "20192020", "20182019"]

if not os.path.exists("../outputs"):
    os.makedirs("../outputs")


def isForward(code):
    return (code == 'R' or code == 'L' or code == 'C')


def isDefensemen(code):
    return code == 'D'


def isGoalie(code):
    return code == 'G'


def addPlayer(player, players, drafted_players):
    stats = requests.get(
        "https://statsapi.web.nhl.com" + str(player["person"]["link"]) + "/stats?stats=yearByYear").json()
    pointsLastSeason = 0
    average = 0
    count = 0
    drafted = 0
    try:
        seasons = stats["stats"][0]["splits"]
        pointsLastSeason = seasons[-1]["stat"]["points"]
        for season in seasons[-min(3, len(seasons)):]:
            average += season["stat"]["points"]
            count += 1

        if count:
            average /= count

        if max([difflib.SequenceMatcher(None, player['person']['fullName'].upper().split(" ")[-1], d).ratio() for d in
                drafted_players]) == 1:
            drafted = 1

        players.writerow({filters[Filters.id.value]: player['person']['id'],
                          filters[Filters.fullname.value]: player['person']['fullName'],
                          filters[Filters.points_last_season.value]: pointsLastSeason,
                          filters[Filters.average_last_seasons.value]: average,
                          filters[Filters.drafted.value]: drafted})
    except KeyError:
        pass
    return drafted


def addGoalie(player, team, goalies, drafted_players):
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
            drafted_players]) == 1:
        drafted = 1

    goalies.writerow({filters[Filters.id.value]: player['person']['id'],
                      filters[Filters.fullname.value]: player['person']['fullName'],
                      filters[Filters.points_last_season.value]: pointsLastSeason,
                      filters[Filters.average_last_seasons.value]: average,
                      filters[Filters.drafted.value]: drafted})
    return drafted


def analysePlayersFromTeam(team_id, team_name, forwards, defensemen, goalies, drafted_players):
    request = "https://statsapi.web.nhl.com/api/v1/teams/" + str(team_id) + "/roster"
    roster = requests.get(request).json()["roster"]
    drafted_count = 0
    for player in roster:
        if isForward(player["position"]["code"]):
            drafted_count += addPlayer(player, forwards, drafted_players)
            pass
        elif isDefensemen(player["position"]["code"]):
            drafted_count += addPlayer(player, defensemen, drafted_players)
            pass
        elif isGoalie(player["position"]["code"]):
            drafted_count += addGoalie(player, team_id, goalies, drafted_players)

    return drafted_count


def generatePlayerList():
    forwardsFile = open('../outputs/forwards.csv', 'w+', newline='')
    forwards = csv.DictWriter(forwardsFile, fieldnames=filters)

    defensemenFile = open('../outputs/defensemen.csv', 'w+', newline='')
    defensemen = csv.DictWriter(defensemenFile, fieldnames=filters)

    goaliesFile = open('../outputs/goalies.csv', 'w+', newline='')
    goalies = csv.DictWriter(goaliesFile, fieldnames=filters)

    text_file = open(os.path.join(os.getcwd(), "../forbidden_players.raw"), 'r', encoding="utf8")
    as_string = text_file.read()
    drafted_players = re.split(r"\n+", as_string)
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
                        f" drafted players instead of {len(drafted_players)}")
    pass


def test_forbidden_players():
    text_file = open(os.path.join(os.getcwd(), "../forbidden_players.raw"), 'r', encoding="utf8")
    as_string = text_file.read()
    drafted_players = re.split(r"\n+", as_string)

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
