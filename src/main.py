from src import PlayerAnalyser

print("Sorting players...")

data_dir = "C://Users//casto//Documents//Git//Draft//Draft_Algorythm//CSVs//Draft-2019//"

defs = PlayerAnalyser.create_dict_from_file(data_dir + "Def.csv")
att = PlayerAnalyser.create_dict_from_file(data_dir + "Att.csv")
forbidden = PlayerAnalyser.create_dict_from_file(data_dir + "ForbiddenPlayers.csv")

available_players = defs + att
available_players = PlayerAnalyser.remove_players(available_players, forbidden)
evaluated_players = PlayerAnalyser.calculate_player_score(available_players)

sorted_players = PlayerAnalyser.sort_by_key(evaluated_players, "Score")
for item in sorted_players:
    print(item)

print("There are {} players".format(len(sorted_players)))

PlayerAnalyser.print_players_file(sorted_players,"test_draft.csv")
