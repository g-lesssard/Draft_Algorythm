import requests
import csv
from enum import Enum
from tqdm import tqdm


class Filters(Enum):
    id = 0
    fullname = 1
    points_last_season = 2
    average_last_seasons = 3


filters = ['id', 'fullName', 'points(2020-2021)', 'average(2018-2021)']
active_seasons = ["20202021", "20192020", "20182019"]


forwardsFile = open('forwards.csv', 'w', newline='') 
forwards = csv.DictWriter(forwardsFile, fieldnames=filters)

defensemenFile = open('defensemen.csv', 'w', newline='')
defensemen = csv.DictWriter(defensemenFile, fieldnames=filters)

goaliesFile = open('goalies.csv', 'w', newline='')
goalies = csv.DictWriter(goaliesFile, fieldnames=filters)


def isForward(code):
    return (code == 'R' or code == 'L' or code == 'C')

def isDefensemen(code):
    return code == 'D'

def isGoalie(code):
    return code == 'G'


def addForward(player):
    statsLastSeason = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=" + active_seasons[0]).json()
    pointsLastSeason = 0
    average = 0
    count = 0
    try:
        pointsLastSeason = statsLastSeason["stats"][0]["splits"][0]["stat"]["points"]
        average += pointsLastSeason
        count += 1
    except:
        pass
    stats = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=" + active_seasons[1]).json()
    try:
        average += stats["stats"][0]["splits"][0]["stat"]["points"]
        count += 1
    except:
        pass
    stats = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=" + active_seasons[2]).json()
    try:
        average += stats["stats"][0]["splits"][0]["stat"]["points"]
        count += 1
    except:
        pass
    if(count):
        average /= count
    forwards.writerow( {filters[Filters.id.value]: player['person']['id'],
                        filters[Filters.fullname.value]: player['person']['fullName'],
                        filters[Filters.points_last_season.value]: pointsLastSeason,
                        filters[Filters.average_last_seasons.value]: average})
    return True

def addDefenseman(player):
    statsLastSeason = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=" + active_seasons[0]).json()
    pointsLastSeason = 0
    average = 0
    count = 0
    try:
        pointsLastSeason = statsLastSeason["stats"][0]["splits"][0]["stat"]["points"]
        average += pointsLastSeason
        count += 1
    except:
        pass
    stats = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=" + active_seasons[1]).json()
    try:
        average += stats["stats"][0]["splits"][0]["stat"]["points"]
        count += 1
    except:
        pass
    stats = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=" + active_seasons[2]).json()
    try:
        average += stats["stats"][0]["splits"][0]["stat"]["points"]
        count += 1
    except:
        pass
    if(count):
        average /= count
    defensemen.writerow( {filters[Filters.id.value]: player['person']['id'],
                        filters[Filters.fullname.value]: player['person']['fullName'],
                        filters[Filters.points_last_season.value]: pointsLastSeason,
                        filters[Filters.average_last_seasons.value]: average})
    return True

def addGoalie(player, team):
    statsLastSeason = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=" + active_seasons[0]).json()
    pointsLastSeason = 0
    average = 0
    count = 0
    try:
        pointsLastSeason = statsLastSeason["stats"][0]["splits"][0]["stat"]["wins"] * 2 + statsLastSeason["stats"][0]["splits"][0]["stat"]["ties"]
        average += pointsLastSeason
        count += 1
    except:
        pass
    stats = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=" + active_seasons[1]).json()
    try:
        average += stats["stats"][0]["splits"][0]["stat"]["wins"] * 2 + stats["stats"][0]["splits"][0]["stat"]["ties"]
        count += 1
    except:
        pass
    stats = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=" + active_seasons[2]).json()
    try:
        average += stats["stats"][0]["splits"][0]["stat"]["wins"] * 2 + stats["stats"][0]["splits"][0]["stat"]["ties"]
        count += 1
    except:
        pass
    if(count):
        average /= count
    goalies.writerow( {filters[Filters.id.value]: player['person']['id'],
                        filters[Filters.fullname.value]: player['person']['fullName'],
                        filters[Filters.points_last_season.value]: pointsLastSeason,
                        filters[Filters.average_last_seasons.value]: average})
    return True


def generatePlayerList():
    forwards.writeheader()
    defensemen.writeheader()
    goalies.writeheader()
    
    teams = dict()
    
    for team in requests.get("https://statsapi.web.nhl.com/api/v1/teams").json()["teams"]:
        teams.update({team["id"]:team["name"]})
        
    for team in tqdm(teams):
        request = "https://statsapi.web.nhl.com/api/v1/teams/" + str(team) + "/roster"
        roster = requests.get(request).json()["roster"]
        for player in tqdm(roster):
            if isForward(player["position"]["code"]):
                addForward(player)
                pass
            elif isDefensemen(player["position"]["code"]):
                addDefenseman(player)
                pass
            elif isGoalie(player["position"]["code"]):
                addGoalie(player, team)
    print("CSVs generated")


if __name__ == "__main__":
    generatePlayerList()
        


