from src import PlayerAnalyser

print("Sorting players...")

data_file = "/home/casto/Documents/Git/Draft_Algorythm/CSVs/TopPlayers.csv"
data_file = "C://Users//casto//Documents//Git//Draft//Draft_Algorythm//CSVs//TopPlayers.csv"
forbidden_file = "C://Users//casto//Documents//Git//Draft//Draft_Algorythm//CSVs//ForbiddenPlayers.csv"

available_players = PlayerAnalyser.create_dict_from_file(data_file)
forbidden_players = PlayerAnalyser.create_dict_from_file(forbidden_file)
available_players = PlayerAnalyser.remove_players(available_players,forbidden_players)

evaluated_players = PlayerAnalyser.calculate_player_score(available_players)

sorted_players = PlayerAnalyser.sort_by_key(evaluated_players, "Score")
for item in sorted_players:
	print(item)