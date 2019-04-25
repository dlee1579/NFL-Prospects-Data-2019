from test_folder import *
# import requests
# import matplotlib.pyplot as plt
# from numpy import *
from scipy.stats import skew, skewtest, percentileofscore
import time


def create_database_lb(category="TT"):
	# initialize DataFrame object
	df = pd.DataFrame()

	# initialize url template for total tackles

	tackle_dict = {
		"TT": "34/p",
		"TFL": "39/p"
	}
	url_template = "https://www.ncaa.com/stats/football/fbs/current/individual/"
	total_tackles_template = "http://www.ncaa.com/stats/football/fbs/current/individual/34/p"
	tackles_for_loss_template = "https://www.ncaa.com/stats/football/fbs/current/individual/39/p"

	# needs header to run read_html on NCAA website
	header = {
		"User-Agent": "Mozilla/5.0",
	}

	# scrapes 5 pages to get 50 players each per page, 250 players total
	pages = range(1, 6)

	url_template += tackle_dict[category]

	try:
		for i in pages:
			url = url_template + str(i)
			r = requests.get(url, headers=header)
			print(r)
			df_addition = pd.read_html(r.text)[0]
			print(df_addition)

			# if df is empty then df becomes the first portion to be appended
			if df.empty:
				df = df_addition
			else:
				df = df.append(df_addition)
	except ValueError:
		pass

	# remove default index and re-index to numbers from 1-250
	df = df.reset_index(drop=True)
	print(df)

	df.to_csv("lb_%s.csv" % category)
	return df


def create_histogram_lb(category="TT"):
	tackle_dict = {
		"TT": "TT",
		"TFL": "TTFL"
	}

	df = pd.read_csv("lb_%s.csv" % category)
	print(df)
	dataset = df[tackle_dict[category]]

	# df = pd.read_csv("lb_database.csv")

	# Get dataset for Total Tackles
	median_value = median(dataset)
	plt.axvline(median_value, color='k', linestyle='dashed', linewidth=1)
	median_note = "  median: " + str(median_value)
	plt.annotate(median_note, (median_value, 30))
	print("median: ", median_value)
	print("top 30 percentile: ", percentile(dataset, 70))
	plt.hist(dataset, bins=20)
	plt.title("%s per Player in 2018 NCAA Season" % category)
	plt.xlabel(category)
	plt.ylabel("Count")
	plt.show()
	print(skew(dataset))
	print(skewtest(dataset))


def create_SPARQ_DB():
	df = pd.read_html("https://docs.google.com/spreadsheets/d/e/2PACX-1vRCeTuBWDgrWMV5d5XTNgcgjbT0nN1JQFJcfTFlMW0Qy8yW2WIIZWQGILknZ7UvY0vfFh9N9ABaycNZ/pubhtml/sheet?headers=false&gid=0")[0]
	# df.reset_index(drop=True)
	#df.drop(df.iloc[0],axis=1)
	# df.to_csv("SPARQ_lb.csv")
	# df = pd.read_csv("SPARQ_lb.csv")
	# print(df.columns)
	# df = df.drop(columns=["Unnamed: 0", "Unnamed: 0.1.1"])
	# df.reset_index(drop=True, inplace=True)
	#df.reindex(df["Name"])
	df.to_csv("SPARQ_lb.csv")
	print(df.iloc[0])
	df.drop(df.iloc[0])
	print(df)
	#df.to_csv("SPARQ_lb.csv")


def get_player_stats(player, year="2018"):
	tackles_dict = {
		"Tot": "TT",
		"Solo": "ST",
		"Loss": "TFL"
	}
	# tackles_types = ["Tot", "Solo", "Loss"]

	try:
		searchlink = "https://www.sports-reference.com/cfb/search/search.fcgi?search=%s"
		player_df = pd.read_html((searchlink % player.replace(" ", "+")))[0]

		# Individual player stats will have multi-indexed columns, delete first level
		player_df.columns = player_df.columns.droplevel()
		player_df.set_index("Year", inplace=True)

		# Get only stats from the most recent year i.e. 2018 set to default
		stats_recent = [player_df.loc[x] for x in player_df.index.to_list() if year in x][0]

		# Returns Total Tackles, Solo Tackles, Tackles for Loss in that order
		return [stats_recent["Tot"], stats_recent["Solo"], stats_recent["Loss"], stats_recent["Sk"], stats_recent["Int"], stats_recent["PD"], stats_recent["FR"], stats_recent["FF"]]
		# for tackle_type in tackles_types:
		# 	#df.set_value("Vosean Joseph", tackles_dict[tackle_type],df2[tackle_type])
		# 	df.at[player, tackles_dict[tackle_type]] = stats_recent[tackle_type]
	except (ValueError, IndexError, KeyError) as e:
		print("Invalid player name.")
		pass


def update_database(pos):
	# Update Database with Defensive information from Sports-Reference.com
	df = pd.read_excel("NFL DEF 2019.xlsx", sheetname=pos).set_index("Name")
	players_recent = df.index.to_list()
	production_categories = ["TT%", "ST%", "TFL%", "TFL%", "SK%", "INT%", "PD%", "FR%", "FF%"]
	measurable_categories = ["HT%", "WT%", "AL%", "HS%", "WING%", "40 YD%", "20 YD%", "10 YD%", "Shuttle%", "3-Cone%",
	                         "BP%", "Vert.%", "Broad%"]

	timed_categories = ["40 YD%", "20 YD%", "10 YD%", "Shuttle%", "3-Cone%"]

	# print(get_player_stats("Alex Figueroa"))
	print("Process started.")

	start = time.time()

	for player in players_recent:
		print(player)
		try:
			[TT, ST, TFL, SK, INT, PD, FR, FF] = get_player_stats(player)
			df.at[player, "TT"] = TT
			df.at[player, "ST"] = ST
			df.at[player, "TFL"] = TFL
			df.at[player, "SK"] = SK
			df.at[player, "INT"] = INT
			df.at[player, "PD"] = PD
			df.at[player, "FR"] = FR
			df.at[player, "FF"] = FF

			# for cat in production_categories:
			# 	df.at[player, cat] = percentileofscore(df[cat[:-1]].to_list(), df.at[player, cat[:-1]])

			# for cat in measurable_categories:
			# 	if cat in timed_categories:
			# 		df.at[player, cat] = 100 - percentileofscore(df[cat[:-1]].to_list(), df.at[player, cat[:-1]])
			# 	else:
			# 		df.at[player, cat] = percentileofscore(df[cat[:-1]].to_list(), df.at[player, cat[:-1]])

		except (TypeError, IndexError) as e:
			print("%s does not have a Sports-Reference profile page." % player)
			pass

	for cat in measurable_categories:
		if cat not in df.columns.to_list():
			# df[cat[:-1]] = 0
			df[cat] = NaN

	for cat in production_categories:
		if cat not in df.columns.to_list():
			df[cat] = NaN

	end = time.time()
	time_elapsed = end - start
	print("Time elapsed: %f" % time_elapsed)

	# df.to_excel("Aggregate LB DataBase 2015-2019.xlsx", sheet_name="Agg Data")
	#df.to_excel("NFL DEF 2019.xlsx", sheet_name="LB")
	df.to_excel("NFL DEF 2019 - %s.xlsx" % pos)

def create_player_profile(name, pos):
	try:
		df = pd.read_excel("NFL DEF 2019.xlsx", sheet_name=pos).set_index("Name").drop(columns="NFL%")
		# print(df.index.to_list())
		categories_percentiles = [x for x in df.columns.to_list() if "%" in x]
		#print(categories_percentiles)
		player = df.loc[name]
		position = player["Pos."]
		player_percentiles = player[categories_percentiles]

		# Bar Chart for Production Data, Radar Chart for Measurables Data;
		production_categories = ["TT%", "ST%", "TFL%", "TFL%", "SK%", "INT%", "PD%", "FF%"]
		measurable_categories = ["HT%", "WT%", "AL%", "HS%", "WING%", "40 YD%", "20 YD%", "10 YD%", "Shuttle%", "3-Cone%", "BP%", "Vert.%", "Broad%"]
		measurable_categories = player_percentiles[measurable_categories].dropna().index.to_list()
		N = len(measurable_categories)

		production_values = player_percentiles[production_categories].to_list()
		measurable_values = player_percentiles[measurable_categories].to_list()

		# For Radar Chart, need to repeat first value to close the circular graph
		measurable_categories += measurable_categories[:1]
		measurable_values += measurable_values[:1]

		#print(measurable_categories)
		#print(measurable_values)
		# Radar Chart of Measurables first

		# Compute angles for Radar Chart
		angles = [n / float(N) * 2 * pi for n in range(N)]
		angles += angles[:1]

		#print(len(angles))

		fig = plt.figure()
		fig.suptitle("%s %s" % (position, name))

		# Initialise the spider plot
		ax = plt.subplot(121, polar=True)

		# Draw one axe per variable + add labels labels yet
		plt.xticks(angles[:-1], measurable_categories, color='grey', size=8)

		# Plot data
		ax.plot(angles, measurable_values, linewidth=1, linestyle='solid')

		# Fill area
		ax.fill(angles, measurable_values, 'b', alpha=0.1)
		ax
		plt.title("Measurables")

		#print(player_percentiles)
		#plt.bar(categories_percentiles, player_percentiles.to_list())
		plt.subplot(1,2,2)

		# Create List of Colors for corresponding values
		# If 100, then full GREEN (0, 255, 0); if 50, then full YELLOW (255, 255, 0); if 0, then full RED (255, 0, 0)

		colors_list = []
		production_raw = [category[:-1] for category in production_categories if "% in category"]
		production_values_raw = player[production_raw].to_list()

		for value in production_values:
			if value > 66:
				colors_list.append("green")
			elif value > 33:
				colors_list.append("yellow")
			else:
				colors_list.append("red")

		bars = plt.bar(production_raw, production_values, color=colors_list)
		i = 0
		for bar in bars:
			yval = bar.get_height()
			plt.text(bar.get_x()+.15, yval+1, production_values_raw[i])
			i += 1

		print(production_values)
		plt.title("2018 Defensive Production")
		plt.ylabel("Percentiles")
		plt.xlabel("Production Categories")

		plt.show()
		print(player_percentiles)
		return player
	except KeyError:
		print("Invalid player.")

if __name__ == "__main__":
	# create_database_lb(category="TFL")
	# create_histogram_lb("TFL")
	# normal_set = random.normal(size=1000)
	# print(skew(normal_set))
	# print(skewtest(normal_set))
	# create_SPARQ_DB()


	#Initialize DataFrame of Player database, set name as index
	# df = pd.read_excel("test_folder/LB prospects 2015-2019.xlsm", sheet_name="Agg Data").set_index("Name")
	# df = pd.read_excel("test_folder/NFL Defensive Prospects 2019.xlsx", sheet_name="LB").set_index("Name")
	# # Sampling n number of players
	# #players_recent = df.loc[df["Year"] == 2019].index.to_list()
	# players_recent = df.index.to_list()
	# # print(get_player_stats("Alex Figueroa"))
	# print("Process started.")
	#
	# start = time.time()
	#
	# for player in players_recent:
	# 	print(player)
	# 	try:
	# 		[TT, ST, TFL, SK, INT, PD, FR, FF] = get_player_stats(player)
	# 		df.at[player, "TT"] = TT
	# 		df.at[player, "ST"] = ST
	# 		df.at[player, "TFL"] = TFL
	# 		df.at[player, "SK"] = SK
	# 		df.at[player, "INT"] = INT
	# 		df.at[player, "PD"] = PD
	# 		df.at[player, "FR"] = FR
	# 		df.at[player, "FF"] = FF
	#
	#
	# 	except (TypeError, IndexError) as e:
	# 		print("%s does not have a Sports-Reference profile page." % player)
	# 		pass
	#
	# end = time.time()
	# time_elapsed = end - start
	# print("Time elapsed: %f" % (time_elapsed))
	#
	# # df.to_excel("Aggregate LB DataBase 2015-2019.xlsx", sheet_name="Agg Data")
	# df.to_excel("NFL DEF 2019.xlsx", sheet_name="LB")
	#players_recent = df.
# 	# # Set the Name column as the index
# 	# df.set_index("Name", inplace=True)
# 	# print(df)
	#create_player_profile("PJ Johnson", "DL")
	update_database("EDGE")



