from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
import mysql.connector
import utility
import urllib
import re

# Selenium & MySQL essentials
driver = webdriver.Chrome("<INSERT YOUR DRIVER PATH HERE")
cnx = mysql.connector.connect(user ='XXXXX', password = 'XXXXX',
	host = 'XXXXX', database = 'XXXXX', auth_plugin = 'XXXXX')
cursor = cnx.cursor()

# Lise to hold failed player rows
failed_players = []
failed_urls = []

# Builds all URLs for scraping
def build_urls():
	urls = []

	for year in range(2012, 2021):
		for team in utility.rivals_teams:
			url = "https://" + team + ".rivals.com/commitments/football/" + str(year)
			urls.append(url)

	return(urls)

# Open and scrape URL
def scrape(url):
	driver.get(url)
	driver.implicitly_wait(5)
	class_data = driver.find_element_by_xpath('//*[@id="articles"]/rv-commitments').text.splitlines()
	indexer = url.find(".")
	team = url[8:indexer]
	year = url[-4:]

	return(year, team, class_data)

# Parse scraped data, prep for database committing
def compiler(year, team, class_data):
	players = ""
	pre_data = []
	player_data = []

	for key, val in utility.teams_dict.items():
		if team == key:
			team_name = val

	for item in class_data[1:]:
		item.replace("'", "")
		if item.strip() == "SIGNED" or item.strip() == "VERBAL" or item.strip() == "SOFT":
			players = players + item.strip() + "|"
			players = players + "|||" + "|"

		else:
			players = players + item.strip() + "|"

	columns = ["YEAR", "TEAM"] + class_data[0].split() + ["STATUS"]

	for item in players.split("|||"):
		pre_data.append(item.split("|"))

	for item in pre_data:
		stars = 0
		for val in item:
			if val == '':
				item.remove(val)

		for val in item:
			if val == '':
				item.remove(val)

		if item:
			for val in item:
				if '"' in val:
					index = item.index(val)
					h, i = val.split("'")
					item[index] = ((int(h) * 12) + int(i[:-1]))

			rating = float(item[-3])
					
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

			item.insert(-3, stars)
			item = [year, team_name] + item
			
			if len(item) == len(columns):
				player_data.append(item)
			else:
				failed_players.append(item)
				print("Player row failed")

	return(columns, player_data)

# Commit scraped data to database
def commit(columns, player_data):
	for item in player_data:
		column = ', '.join(columns)
		player = ', '.join(["'" + str(x).replace("'", "") + "'" for x in item])

		try:
			cursor.execute("""INSERT INTO <YOUR TABLE NAME HERE> (%s) VALUES (%s);""" % (column, player))
			cnx.commit()

		except Exception as e:
			print(player, e, "UNSUCCESSFUL IN COMMITTING TO DATABASE.")

urls = build_urls()

for url in urls:
	try:
		scraper = scrape(url)
		data = compiler(scraper[0], scraper[1], scraper[2])
		committed = commit(data[0], data[1])
		print("URL succesfully scraped " + url)

	except Exception as e:
		print("URL scrape unsuccessful " + url, e)
		failed_urls.append(url)

print(failed_players)
print(failed_urls)

