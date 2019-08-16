from src import PlayerAnalyser

print("Sorting players...")

data_dir = "C://Users//casto//Documents//Git//Draft//Draft_Algorythm//CSVs//Draft-2019//"

available_players = PlayerAnalyser.create_dict_from_file(data_dir + "Def.csv")

evaluated_players = PlayerAnalyser.calculate_player_score(available_players)

sorted_players = PlayerAnalyser.sort_by_key(evaluated_players, "Score")
for item in sorted_players:
    print(item)

print("There are {} players".format(len(sorted_players)))
