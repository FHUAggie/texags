import urllib.request as urllib2
from bs4 import BeautifulSoup
import mysql.connector
import requests

cnx = mysql.connector.connect(user ='XXXXX', password = 'XXXXX',
	host = 'XXXXX', database = 'XXXXX',
	auth_plugin = 'XXXXX')

cursor = cnx.cursor()

base_url = "https://api.collegefootballdata.com/recruiting/players?year="

for year in range(2012, 2021):
	url = base_url + str(year)

	r = requests.get(url)

	for item in r.json():
		recruit_type = item['recruitType']
		year = item['year']
		ranking = item['ranking']
		name = item['name']
		high_school = item['school']
		committed_to = item['committedTo']
		position = item['position']
		height = item['height']
		weight = item['weight']
		stars = item['stars']
		rating = item['rating']
		city = item['city']
		state = item['stateProvince']

		if ranking:
			pass
		else:
			ranking = "0"

		columns = ', '.join(["recruit_type", "year", "ranking", "name", "high_school", "committed_to", "position", "height", "weight", "stars", "rating", "city", "state"])
		player = [recruit_type, year, ranking, name, high_school, committed_to, position, height, weight, stars, rating, city, state]

		player = ', '.join(['"' + str(x) + '"' for x in player])

		try:

			cursor.execute("""INSERT INTO hs_247_rankings (%s) VALUES (%s);""" % (columns, player))
			cnx.commit()

			print(player, "SUCCESS!")

		except Exception as e:
			print("FAIL!!!", player, e)
