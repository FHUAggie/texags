import urllib.request as urllib2
from bs4 import BeautifulSoup
import mysql.connector
import utility
import re

cnx = mysql.connector.connect(user ='xxxxx', password = 'xxxxx',
	host = 'xxxxx', database = 'xxxxx',
	auth_plugin = 'xxxxx')

cursor = cnx.cursor()

# Utility object methods are used for building essential data sets
class Utility(object):
	def __init__(self):
		pass

	# Extract HTML from a given URL
	def get_html(self, url_to_scrape):
		url_request = urllib2.urlopen(url_to_scrape)
		html = BeautifulSoup(url_request, 'html.parser')

		return(url_to_scrape, html)

	# Contruct list of all team URLs from cfbstats.com for extracting data
	def get_cfb_urls(self):
		url_prefix = "http://www.cfbstats.com/2019/team/"
		url_suffix = "/index.html"

		urls = []

		for number in range(0, 1000):
			url = url_prefix + str(number) + url_suffix

			if requests.get(url).status_code == 200:
				urls.append(url)
				print(url)

		return(urls)

	# Construct dict for team name/team ID from cfbstats.com
	def team_id_builder(self):
		team_id_dict = {}

		for url in utility.cfbstats_urls:
			data = self.get_html(url)
			team_name = data[1].title.string[20:]
			team_number = re.findall(r'\d+', url[28:])[0]
			team_id_dict[team_number] = team_name

			print(team_name + " mapped to " + team_number)

		return(team_id_dict)

	# Extract all URL suffixes for individual team pages to be scraped
	def construct_page_urls(self, url_to_scrape):
		#Always use this URL: http://www.cfbstats.com/2019/team/697/index.html
		data = self.get_html(url_to_scrape)
		div = data[1].find("div", {"class" : "section"})

		urls = []

		for link in div.find_all("a", href=True):
			urls.append(link['href'][14:])

		return(urls)

# Web scraper object to extract data from URLs
class Scraper(object):
	def __init__(self):
		pass

	# Get team name, year based on URL
	def get_team_info(self, url):
		year = url[24:28]
		team_number = re.findall(r'\d+', url[28:])[0]
		team = utility.cfbstats_dict[team_number]

		return(year, team)

	# Scrape cfbstats.com `/roster` pages
	def scrape_roster(self, html):
		team_info = self.get_team_info(html[0])
		team_name = team_info[1]
		year = team_info[0]

		raw_columns = html[1].find_all('th')
		raw_data = html[1].find_all('td')

		columns = []
		player_data = []

		final_data = []

		for column in raw_columns:
			columns.append(column.text.strip())

		for item in raw_data:
			player_data.append(item.text)

		for number in range(0, len(player_data), len(columns)):
			player = [year, team_name] + player_data[number:number + len(columns)]
			column = ["Year", "Team"] + columns
			column = [x.replace(" ", "_") for x in column]

			if player[6] == "-" or player[7] == "-":
				player[6] = 0
				player[7] = 0

			else:
				feet, inches = player[6].split("-")
				height = (int(feet.strip()) * 12) + int(inches.strip())
				player[6] = height

			final_data.append(player)

		return(column, final_data)

	# Scrape cfbstats.com `/index` pages
	def scrape_index(self, html):
		team_info = self.get_team_info(html[0])
		team_name = team_info[1]
		year = team_info[0]

		raw_columns = html[1].find_all('th')
		raw_data = html[1].find_all('td')

		columns = ["Team_Rk"]
		player_data = []

		final_data = []

		for column in raw_columns:
			if column.text != "":
				columns.append(column.text.strip())

		for item in raw_data:
			player_data.append(item.text)

		for number in range(0, len(player_data), len(columns)):
			column = ["Year", "Team"] + columns
			column = [x.replace("/", "") for x in column]
			column = [x.replace(".", "") for x in column]
			column = [x.replace("%", "Per") for x in column]
			column = [x.replace(" ", "_") for x in column]
			column = [x.replace("Int", "Ints") for x in column]
			column = [x.replace("-", "_") for x in column]

			player = [year, team_name] + player_data[number:number + len(columns)]
			player = [x.replace("'", "") for x in player]

			if player[3].strip() == "Total" or player[3].strip() == "Team" or player[3].strip() == "Opponents":
				pass
			else:

				final_data.append(player)

		return(column, final_data)

	# Scrape cfbstats.com `/split` pages
	def scrape_split(self, html):
		team_info = self.get_team_info(html[0])
		team_name = team_info[1]
		year = team_info[0]

util = Utility()
scrape = Scraper()

failed_urls = []

# html = util.get_html("http://www.cfbstats.com/2012/team/697/rushing/index.html")
# scrape.scrape_index(html)

failed_players = []

for key, value in utility.cfbstats_dict.items():
	prefix = "http://www.cfbstats.com/"
	team_number = key

	for number in range(2012, 2020):
		root = prefix + str(number) + "/team/" + team_number

		for base in utility.page_url_suffixes:
			url = root + base

			print("Commiting URL: " + url)

			try:
				html = util.get_html(url)

				if "roster.html" in url:
					column = ', '.join(scrape.scrape_roster(html)[0])
					players = scrape.scrape_roster(html)[1]

					for player in players:
						try:
							cursor.execute("""INSERT INTO ncaa_rosters (%s) VALUES (%s);""" % (column, ', '.join("'" + str(x).replace("'", "") + "'" for x in player)))
							cnx.commit()

						except Exception as e:
							print(e)
							failed_players.append((url, player))

				elif "index.html" in url:
					column = ', '.join(scrape.scrape_index(html)[0]) 
					players = scrape.scrape_index(html)[1]
					table = ""

					for player in players:
						if '/rushing/index.html' in url:
							table = "ncaa_rushing"
						if '/passing/index.html' in url:
							table = "ncaa_passing"
						if '/receiving/index.html' in url:
							table = "ncaa_receiving"
						if '/puntreturn/index.html' in url:
							table = "ncaa_punt_returns"
						if '/kickreturn/index.html' in url:
							table = "ncaa_kick_return"
						if '/punting/index.html' in url: 
							table = "ncaa_punting"
						if '/kickoff/index.html' in url:
							table = "ncaa_kickoff"
						if '/scoring/index.html' in url:
							table = "ncaa_scoring"
						if '/total/index.html' in url: 
							table = "ncaa_total_offense"
						if '/allpurpose/index.html' in url:
							table = "ncaa_all_purpose"
						if '/interception/index.html' in url:
							table = "ncaa_interceptions"
						if '/fumblereturn/index.html' in url:
							table = "ncaa_fumble_returns"
						if '/tackle/index.html' in url:
							table = "ncaa_tackles"
						if '/tackleforloss/index.html' in url:
							table = "ncaa_tackles_for_loss"
						if '/sack/index.html' in url:
							table = "ncaa_sacks"
						if '/miscdefense/index.html' in url:
							table = "ncaa_misc_defense"

						try:
							cursor.execute("""INSERT INTO %s (%s) VALUES (%s);""" % (table, column, ', '.join("'" + str(x).replace("'", "") + "'" for x in player)))
							cnx.commit()

						except Exception as e:
							print(url, e)
							failed_players.append((url, player))

				elif "split.html" in url:
					pass

				else:
					print("INVALID URL: ", url)

			except Exception as e:
				print(e, url)
				failed_urls.append(url)
				pass

print(failed_urls)
print(failed_players)
