from src import PlayerAnalyser

print("Sorting players...")

data_file = "/home/casto/Documents/Git/Draft_Algorythm/CSVs/TopPlayers.csv"
players = PlayerAnalyser.create_dict_from_file(data_file)

sorted_players = PlayerAnalyser.sort_by_key(players, "ExpectedPoints")
for item in sorted_players:
	print(item)


