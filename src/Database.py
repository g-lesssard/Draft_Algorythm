import logging

import pandas
import pandas as pd
import requests
import csv
import os
import difflib
from enum import Enum
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from pandas import DataFrame
from datetime import date

confirmation_mutex = Lock()
today = date.today()
similarity_level = 0.8

if not os.path.exists("../outputs"):
    os.makedirs("../outputs")


def addPlayer(id, team, list_to_add: DataFrame, drafted: DataFrame):
    stats = requests.get(f"https://api-web.nhle.com/v1/player/{id}/landing").json()
    if not stats["isActive"]: return 0

    # if max([difflib.SequenceMatcher(None, stats['playerSlug']).ratio() for d in drafted]) >= similarity_level:
    #    drafted = 1
    player = pd.Series()
    player["firstName"] = stats["firstName"]["default"]
    player["lastName"] = stats["lastName"]["default"]
    player["age"] = today.year - int(stats["birthDate"].split("-")[0])
    player["team"] = team["fullName"]
    seasons_stats = stats["seasonTotals"]
    last_seasons = DataFrame.from_records(seasons_stats)
    last_seasons = last_seasons[last_seasons["leagueAbbrev"] == "NHL"]
    last_seasons = last_seasons[["season", "points", "gamesPlayed", "plusMinus"]].groupby("season").sum()
    if len(last_seasons) == 0:
        return list_to_add
    last_seasons = last_seasons.iloc[-5:]

    try:
        player["Last Season Points"] = last_seasons[-1:]["points"].iloc[0]
        player["Last Season Games Played"] = last_seasons[-1:]["gamesPlayed"].iloc[0]
        player["Last Season +/-"] = last_seasons[-1:]["plusMinus"].iloc[0]

        player["Average Points"] = last_seasons["points"].mean()
        player["Average Games Played"] = last_seasons["gamesPlayed"].mean().real
        player["Average +/-"] = last_seasons["plusMinus"].mean()

        player["Differential Points"] = last_seasons["points"].diff().mean()
    except IndexError:
        print(f"Last Seasons: {last_seasons.to_string()}")
        pass

    # player["transferred"] = last_seasons[-1:]["teamName"]["default"] is not last_seasons[-2:]["teamName"]["default"]

    list_to_add = pd.concat([list_to_add, player.to_frame().T])
    return list_to_add


def addGoalie(id, team, list_to_add: DataFrame, drafted: DataFrame):
    stats = requests.get(f"https://api-web.nhle.com/v1/player/{id}/landing").json()
    if not stats["isActive"]: return 0

    # if max([difflib.SequenceMatcher(None, stats['playerSlug']).ratio() for d in drafted]) >= similarity_level:
    #    drafted = 1
    player = pd.Series()
    player["firstName"] = stats["firstName"]["default"]
    player["lastName"] = stats["lastName"]["default"]
    player["age"] = today.year - int(stats["birthDate"].split("-")[0])
    player["team"] = team["fullName"]
    seasons_stats = stats["seasonTotals"]
    try:
        last_seasons = DataFrame.from_records(seasons_stats)
        last_seasons = last_seasons[last_seasons["leagueAbbrev"] == "NHL"]
        if len(last_seasons) == 0:
            return list_to_add
        last_seasons = last_seasons[["season", "wins", "otLosses", "shutouts", "goals", "assists", "gamesPlayed"]].groupby("season").sum()
        last_seasons = last_seasons.iloc[-5:]

        last_seasons["points"] = 2 * last_seasons["wins"] + \
                                                last_seasons["otLosses"] + \
                                                3 * last_seasons["shutouts"] + \
                                                10 * last_seasons["goals"] + \
                                                2 * last_seasons["assists"]
    except KeyError:
        print(f"Error running goaler: {id}")
        return list_to_add

    try:
        player["Last Season Points"] = last_seasons[-1:]["points"].iloc[0]
        player["Last Season Games Played"] = last_seasons[-1:]["gamesPlayed"].iloc[0]

        player["Average Points"] = last_seasons["points"].mean()
        player["Average Games Played"] = last_seasons["gamesPlayed"].mean().real
    except IndexError:
        print(f"Last Seasons: {last_seasons.to_string()}")
        pass

    # player["transferred"] = last_seasons[-1:]["teamName"]["default"] is not last_seasons[-2:]["teamName"]["default"]

    list_to_add = pd.concat([list_to_add, player.to_frame().T])
    return list_to_add


def analysePlayersFromTeam(team, drafted_players: DataFrame):
    forwards = DataFrame()
    defensemen = DataFrame()
    goalies = DataFrame()

    team_code = team['triCode']
    request = f"https://api-web.nhle.com/v1/roster/{team_code}/current"
    try:
        roster = requests.get(request).json()
    except ValueError:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    drafted_count = 0
    for player in roster["forwards"]:
        forwards = addPlayer(player["id"], team, forwards, DataFrame())
    for player in roster["defensemen"]:
        defensemen = addPlayer(player["id"], team, defensemen, DataFrame())
    for goalie in roster["goalies"]:
        goalies = addGoalie(goalie["id"], team, goalies, DataFrame())
    return forwards, defensemen, goalies


def generatePlayerList():
    drafted_players = generated_forbidden_lists()
    expected_drafted_count = 0
    for el in drafted_players.items():
        expected_drafted_count += len(el[1])
    total_drafted_count = 0

    teams_json = requests.get("https://api.nhle.com/stats/rest/en/team").json()["data"]
    teams = DataFrame.from_records(teams_json)
    # forwards, defensemen, goalies = analysePlayersFromTeam("MTL", forwards, defensemen, goalies, drafted_players)

    results_dict = {"F": [], "D": [], "G": []}

    test_team = {"triCode": "TOR", "fullName": "Toronto_test"}
    #analysePlayersFromTeam(test_team, drafted_players)

    with tqdm(total=len(teams), desc="Generating Database", colour="green") as pbar:
        with ThreadPoolExecutor(max_workers=len(teams)) as executors:
            futures = [
                executors.submit(analysePlayersFromTeam, team, drafted_players)
                for k, team in teams.iterrows()]
            for future in as_completed(futures):
                f, d, g = future.result()
                results_dict["F"].append(f)
                results_dict["D"].append(d)
                results_dict["G"].append(g)
                pbar.update(1)

    forwards = pd.concat(results_dict["F"])
    defensemen = pd.concat(results_dict["D"])
    goalies = pd.concat(results_dict["G"])

    forwards.to_csv("../outputs/forwards.csv", index=False)
    defensemen.to_csv("../outputs/defensemen.csv", index=False)
    goalies.to_csv("../outputs/goalies.csv", index=False)

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
