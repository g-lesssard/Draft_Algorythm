import requests
import csv

filters = ['id', 'fullName', 'points(2019-2020)', 'average(2017-2020)']

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
    statsLastSeason = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=20192020").json()
    pointsLastSeason = 0
    average = 0
    count = 0
    try:
        pointsLastSeason = statsLastSeason["stats"][0]["splits"][0]["stat"]["points"]
        average += pointsLastSeason
        count += 1
    except:
        pass
    stats2017 = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=20172018").json()
    try:
        average += stats2017["stats"][0]["splits"][0]["stat"]["points"]
        count += 1
    except:
        pass
    stats2018 = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=20182019").json()
    try:
        average += stats2018["stats"][0]["splits"][0]["stat"]["points"]
        count += 1
    except:
        pass
    if(count):
        average /= count
    forwards.writerow( {'id': player['person']['id'],
                        'fullName': player['person']['fullName'],
                        'points(2019-2020)': pointsLastSeason,
                        'average(2017-2020)': average})  
    return True

def addDefenseman(player):
    statsLastSeason = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=20192020").json()
    pointsLastSeason = 0
    average = 0
    count = 0
    try:
        pointsLastSeason = statsLastSeason["stats"][0]["splits"][0]["stat"]["points"]
        average += pointsLastSeason
        count += 1
    except:
        pass
    stats2017 = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=20172018").json()
    try:
        average += stats2017["stats"][0]["splits"][0]["stat"]["points"]
        count += 1
    except:
        pass
    stats2018 = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=20182019").json()
    try:
        average += stats2018["stats"][0]["splits"][0]["stat"]["points"]
        count += 1
    except:
        pass
    if(count):
        average /= count
    defensemen.writerow( {'id': player['person']['id'],
                        'fullName': player['person']['fullName'],
                        'points(2019-2020)': pointsLastSeason,
                        'average(2017-2020)': average})  
    return True

def addGoalie(player, team):
    statsLastSeason = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=20192020").json()
    pointsLastSeason = 0
    average = 0
    count = 0
    try:
        pointsLastSeason = statsLastSeason["stats"][0]["splits"][0]["stat"]["wins"] * 2 + statsLastSeason["stats"][0]["splits"][0]["stat"]["ties"]
        average += pointsLastSeason
        count += 1
    except:
        pass
    stats2017 = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=20172018").json()
    try:
        average += stats2017["stats"][0]["splits"][0]["stat"]["wins"] * 2 + stats2017["stats"][0]["splits"][0]["stat"]["ties"]
        count += 1
    except:
        pass
    stats2018 = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=20182019").json()
    try:
        average += stats2018["stats"][0]["splits"][0]["stat"]["wins"] * 2 + stats2018["stats"][0]["splits"][0]["stat"]["ties"]
        count += 1
    except:
        pass
    if(count):
        average /= count
    goalies.writerow( {'id': player['person']['id'],
                        'fullName': player['person']['fullName'],
                        'points(2019-2020)': pointsLastSeason,
                        'average(2017-2020)': average})  
    return True


def generatePlayerList():
    forwards.writeheader()
    defensemen.writeheader()
    goalies.writeheader()
    
    teams = dict()
    
    for team in requests.get("https://statsapi.web.nhl.com/api/v1/teams").json()["teams"]:
        teams.update({team["id"]:team["name"]})
        
    for team in teams:
        request = "https://statsapi.web.nhl.com/api/v1/teams/" + str(team) + "/roster"
        roster = requests.get(request).json()["roster"]
        for player in roster:
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
        


