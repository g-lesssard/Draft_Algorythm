import requests


teams = dict()
players = list()

for team in requests.get("https://statsapi.web.nhl.com/api/v1/teams").json()["teams"]:
    teams.update({team["id"]:team["name"]})
    
for team in teams:
    request = "https://statsapi.web.nhl.com/api/v1/teams/" + str(team) + "/roster"
    roster = requests.get(request).json()["roster"]
    for player in roster:
        statsLastSeason = requests.get("https://statsapi.web.nhl.com/api/v1/people/" + str(player["person"]["id"]) + "/stats?stats=statsSingleSeason&season=20192020").json()
        
        if player["position"]["code"] != "G":
            try:
                player["lastSeasonPoints"] = statsLastSeason["stats"][0]["splits"][0]["stat"]["points"]
            except:
                i = 0
        print(player)
        players.append(player)

        


