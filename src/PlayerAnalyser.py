def create_dict_from_file(file):
	items = []
	with open(file) as f:
		try:
			headers = f.readline()
			headers = headers.split(";")
			headers.remove(headers[len(headers) - 1])
			lines = f.readlines()
			for line in lines:
				line = line.split(";")
				line.remove(line[len(line) - 1])
				item = dict(zip(headers, line))
				items.append(item)
		except ValueError as e:
			print("Value error: {0}".format(e))
	return items


def sort_by_key(list_to_sort, key):
	return sorted(list_to_sort, key=lambda x: int(x[key]), reverse=True)
