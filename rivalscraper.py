from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
import mysql.connector
import utility
import urllib
import re

# Class for methods that open URLs and access data
class Utility(object):
	def __init__(self):
		pass

	# Using utility.py to build all necessary URLs to scrape
	def build_urls(self):
		urls = []

		for year in range(2012, 2021):
			for team in utility.rivals_teams:
				url = "https://" + team + ".rivals.com/commitments/football/" + str(year)
			
				urls.append(url)

		return(urls)

	# Open URL, focus on proper elements on page
	def access_url(self, url):
		try:
			driver = webdriver.Chrome("<INSERT YOUR DRIVER PATH HERE")
			driver.get(url)
			driver.implicitly_wait(5)
			team_player_data = driver.find_element_by_xpath('//*[@id="articles"]/rv-commitments').text

			indexer = url.find(".")
			team = url[8:indexer]
			year = url[-4:]

			for key, val in utility.teams_dict.items():
				if team == key:
					team_name = val

			driver.close()

			return(year, team_name, team_player_data)

		except Exception as e:
			print(e, "access_url()")

	# Committing web scrape to database
	def db_commit(self, columns, players):
		cnx = mysql.connector.connect(user ='XXXX', password = 'XXXXX',
			host = 'XXXXX', database = 'XXXXX',
			auth_plugin = 'XXXXX')

		cursor = cnx.cursor()

		for item in players:
			column = ', '.join(columns)
			player = ', '.join(["'" + str(x) + "'" for x in item])

			try:

				cursor.execute("""INSERT INTO <TABLE_NAME_HERE> (%s) VALUES (%s);""" % (column, player))
				cnx.commit()

				print(player, "Successfully committed to database.")

			except Exception as e:
				print(player, e, "UNSUCCESSFUL IN COMMITTING TO DATABASE.")

# Class with methods to take mold scraped data
class Scraper(object):
	def __init__(self):
		pass

	def scrape_url(self, year, team_name, team_player_data):
		raw_data = []
		players = []

		# Converting height into feet, inches
		for item in team_player_data.splitlines():
			if '"' in item:
				raw_height = item.split("'")
				feet = int(raw_height[0])
				inches = int(re.findall(r'\d+', raw_height[1])[0])
				height = str((feet * 12) + inches)
				raw_data.append(height)

			else:
				raw_data.append(item.replace("'", ""))

		try:
			columns = raw_data[0].split()
			player_data = raw_data[1:]

		except Exception as e:
			print(e, year, team_name)

		# Building initial player rows
		try:
			for number in range(0, len(player_data), len(columns)):
				player = player_data[number:number + len(columns)]

				# Accounting for pages (2012 Oregon) with no for weight value
				try:
					rating = float(player[5])

				except:
					player.insert(4, 200)
					rating = float(player[5])

				stars = 0

				# Generating # of stars based on Rivals rating
				if rating == 6.1:
					stars = 5
				elif rating <= 6 and rating >= 5.8:
					stars = 4
				elif rating < 5.8 and rating > 5.4:
					stars = 3
				elif rating <=5.4 and rating >= 5.2:
					stars = 2
				else:
					stars = 0

				player.insert(5, stars)
				player = player[:-1]
				# Adding in the year, team_name values
				player = [year, team_name] +  player
				players.append(player)
			
			# Adding in the year, college team columns
			columns = ["YEAR", "TEAM"] + columns

			return(columns, players)

		except Exception as e:
			print(e, year, team_name)
			pass
      
