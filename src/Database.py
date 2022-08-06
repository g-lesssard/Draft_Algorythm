import requests
import csv
import os
from enum import Enum
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed


class Filters(Enum):
    id = 0
    fullname = 1
    points_last_season = 2
    average_last_seasons = 3


filters = ['id', 'fullName', 'points(2020-2021)', 'average(2018-2021)']
active_seasons = ["20202021", "20192020", "20182019"]

if not os.path.exists("../outputs"):
    os.makedirs("../outputs")

forwardsFile = open('../outputs/forwards.csv', 'w+', newline='')
forwards = csv.DictWriter(forwardsFile, fieldnames=filters)

defensemenFile = open('../outputs/defensemen.csv', 'w+', newline='')
defensemen = csv.DictWriter(defensemenFile, fieldnames=filters)

goaliesFile = open('../outputs/goalies.csv', 'w+', newline='')
goalies = csv.DictWriter(goaliesFile, fieldnames=filters)


def isForward(code):
    return (code == 'R' or code == 'L' or code == 'C')


def isDefensemen(code):
    return code == 'D'


def isGoalie(code):
    return code == 'G'


def addPlayer(player, players):
    stats = requests.get(
        "https://statsapi.web.nhl.com" + str(player["person"]["link"]) + "/stats?stats=yearByYear").json()
    pointsLastSeason = 0
    average = 0
    count = 0
    try:
        seasons = stats["stats"][0]["splits"]
        pointsLastSeason = seasons[-1]["stat"]["points"]
        for season in seasons[-min(3, len(seasons)):]:
            average += season["stat"]["points"]
            count += 1

        if count:
            average /= count

        players.writerow({filters[Filters.id.value]: player['person']['id'],
                          filters[Filters.fullname.value]: player['person']['fullName'],
                          filters[Filters.points_last_season.value]: pointsLastSeason,
                          filters[Filters.average_last_seasons.value]: average})
    except KeyError:
        pass
    return True


def addGoalie(player, team):
    statsLastSeason = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(
        player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=" + active_seasons[0]).json()
    pointsLastSeason = 0
    average = 0
    count = 0
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
    goalies.writerow({filters[Filters.id.value]: player['person']['id'],
                      filters[Filters.fullname.value]: player['person']['fullName'],
                      filters[Filters.points_last_season.value]: pointsLastSeason,
                      filters[Filters.average_last_seasons.value]: average})
    return True


def analysePlayersFromTeam(team_id, team_name=""):
    request = "https://statsapi.web.nhl.com/api/v1/teams/" + str(team_id) + "/roster"
    roster = requests.get(request).json()["roster"]
    for player in roster:
        if isForward(player["position"]["code"]):
            addPlayer(player, forwards)
            pass
        elif isDefensemen(player["position"]["code"]):
            addPlayer(player, defensemen)
            pass
        elif isGoalie(player["position"]["code"]):
            addGoalie(player, team_id)


def generatePlayerList():
    forwards.writeheader()
    defensemen.writeheader()
    goalies.writeheader()

    teams = dict()

    for team in requests.get("https://statsapi.web.nhl.com/api/v1/teams").json()["teams"]:
        teams.update({team["id"]: team["name"]})

    with tqdm(total=len(teams), desc="Generating Database", colour="green") as pbar:
        with ThreadPoolExecutor(max_workers=len(teams)) as executors:
            futures = [executors.submit(analysePlayersFromTeam, t, teams[t]) for t in teams]
            for future in as_completed(futures):
                pbar.update(1)

    print("CSVs generated")


if __name__ == "__main__":
    generatePlayerList()
