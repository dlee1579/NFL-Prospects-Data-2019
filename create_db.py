from test_folder import *
# import requests
# import matplotlib.pyplot as plt
# from numpy import *
from scipy.stats import skew, skewtest


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


if __name__ == "__main__":
	# create_database_lb(category="TFL")
	# create_histogram_lb("TFL")
	# normal_set = random.normal(size=1000)
	# print(skew(normal_set))
	# print(skewtest(normal_set))
	# create_SPARQ_DB()
	df = pd.read_excel("test_folder/LB prospects 2015-2019.xlsm", sheet_name="Agg Data")

	# Set the Name column as the index
	df.set_index("Name", inplace=True)
	print(df)

	# Set player to update tackles information for; example: Vosean Joseph
	player = "Vosean Joseph".replace(" ", "+")
	searchlink = "https://www.sports-reference.com/cfb/search/search.fcgi?search=%s"
	df2 = pd.read_html((searchlink % player))[0]

	# Individual player stats will have multi-indexed columns, delete first level
	df2.columns = df2.columns.droplevel()
	df2.set_index("Year")
	print(df2)


