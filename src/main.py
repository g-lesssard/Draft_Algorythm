import PlayerAnalyser

print("Sorting players...")

data_dir = "D://Git//Draft//Draft_Algorythm//CSVs//Official//"

defs = PlayerAnalyser.create_dict_from_file(data_dir + "Def.csv")
att = PlayerAnalyser.create_dict_from_file(data_dir + "Att.csv")
goalies = PlayerAnalyser.create_dict_from_file(data_dir + "Goalies.csv")
forbidden = PlayerAnalyser.create_dict_from_file(data_dir + "ForbiddenPlayers.csv")

available_defs = PlayerAnalyser.remove_players(defs, forbidden)
available_att = PlayerAnalyser.remove_players(att, forbidden)
available_goalies = PlayerAnalyser.remove_players(goalies,forbidden)
#evaluated_players = PlayerAnalyser.calculate_player_score(available_players)

#sorted_players = PlayerAnalyser.sort_by_key(available_players, "PastPoints")


available_att = PlayerAnalyser.set_max_age(available_att, 34)
available_defs = PlayerAnalyser.set_max_age(available_defs, 37)

print("There are {} players".format(len(available_defs + available_att)))

PlayerAnalyser.print_players_file(available_defs,"draft_defs.csv")
PlayerAnalyser.print_players_file(available_att,"draft_atts.csv")
PlayerAnalyser.print_players_file(available_goalies, "draft_goalies.csv")
