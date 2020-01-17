import urllib.request as urllib2
from bs4 import BeautifulSoup
import mysql.connector

# MySQL essentials
cnx = mysql.connector.connect(user ='XXXXX', password = 'XXXXX',
	host = 'XXXXX', database = 'XXXXX', auth_plugin = 'XXXXX')
cursor = cnx.cursor()

# Class for prepping data for scraping
class Utility(object):
	def __init__(self):
		pass
  
  # Constructs NFL draft data URLs from 2013 - 2019
	def construct_urls(self):
		base_url = "http://www.nfl.com/draft/history/fulldraft?season="
		urls = []

		for year in range(2013, 2020):
			urls.append(base_url + str(year))

		return(urls)

  # Creates HTML object of each NFL draft data URL
	def extract_html(self, url):
		url_request = urllib2.urlopen(url)
		html = BeautifulSoup(url_request, 'html.parser')
		year = url[-4:]

		return(year, html)

# Class for HTML scraping methods
class Scraper(object):
	def __init__(self):
		pass

  # Scrapes, parses, and structures data for database
	def scrape_draft_data(self, year, html):
		ignore = ["SEL #", "TEAM", "PLAYER", "POSITION", "SCHOOL"]
		columns = ["Pick", "Team", "Player", "Position", "College"]
		
		raw_data = []
		draft_data = []

		for item in html.find_all("td"):
			value = item.text.strip()

			if value in ignore:
				pass

			elif "- Round" in value:
				pass

			else:
				raw_data.append(value)

		for number in range(0, len(raw_data), len(columns)):
			draft_data.append([year] + raw_data[number:number + len(columns)])

		columns = ["Year"] + columns

		return(columns, draft_data)

	# Commit values to database
	def commit(self, columns, draft_data):
		for item in draft_data:
			column = ', '.join(columns)
			player = ', '.join(["'" + str(x).replace("'", "") + "'" for x in item])

			print(column)
			print(player)

			try:
				cursor.execute("""INSERT INTO <YOUR TABLE NAME HERE> (%s) VALUES (%s);""" % (column, player))
				cnx.commit()

			except Exception as e:
				print(player, e, "UNSUCCESSFUL IN COMMITTING TO DATABASE.")

