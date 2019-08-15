import csv
import datetime
import json
import os
import re
import socket
import sys
import time

print("Sorting players...")

data_file = "/home/casto/Documents/Git/Draft_Algorythm/CSVs/TopPlayers.csv"
players = []

with open(data_file) as f:
	try:
		headers = f.readline()
		headers = headers.split(";")
		headers.remove(headers[len(headers)-1])
		lines = f.readlines()
		for line in lines:
			line = line.split(";")
			line.remove(line[len(line)-1])
			player = dict(zip(headers, line))
			players.append(player)
	except ValueError as e:
		print("Value error: {0}".format(e))

sorted_players = sorted(players, key=lambda x: int(x['ExpectedPoints']), reverse=True)
for item in sorted_players:
	print(item)
