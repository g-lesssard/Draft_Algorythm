from src import TableSorter

print("Sorting players...")

data_file = "/home/casto/Documents/Git/Draft_Algorythm/CSVs/TopPlayers.csv"
players = TableSorter.createDictFromFile(data_file)

sorted_players = TableSorter.sortByKey(players,"ExpectedPoints")
for item in sorted_players:
	print(item)

number_of_teams = 1
number_of_players = len(sorted_players)
teams = []
for player in sorted_players:
	i = 0
	if number_of_teams == 1:
		continue
	else:
		print("Splitting Teams")

print("Done!")
