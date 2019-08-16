def create_dict_from_file(file):
    items = []
    with open(file) as f:
        try:
            headers = f.readline()
            headers = headers.split(",")
            headers[0] = headers[0][3:]
            headers[len(headers) - 1] = headers[len(headers) - 1].rstrip('\n')
            lines = f.readlines()
            for line in lines:
                line = line.split(",")
                line[len(line) - 1] = line[len(line) - 1].rstrip('\n')
                item = dict(zip(headers, line))
                items.append(item)
        except ValueError as e:
            print("Value error: {0}".format(e))
    return items


def sort_by_key(list_to_sort, key):
    return sorted(list_to_sort, key=lambda x: int(x[key]), reverse=True)


def calculate_player_score(list_of_players):
    for player in list_of_players:
        past_factor = 0.7
        age_factor = -5
        score = past_factor * int(player['PastPoints']) + age_factor * (1995 - int(player["Year"]))
        player.update({"Score": score})
    return list_of_players


def remove_players(base_players, forbidden_players):
    for forbidden_player in forbidden_players:
        for player in base_players:
            if player["Name"] == forbidden_player["Name"]:
                base_players.remove(player)
    return base_players


def print_players_file(players, file):
    f = open(file, "w+")
    for player in players:
        f.write(player["Name"] + "\n")
    f.close()
