import urllib.request as urllib2
from bs4 import BeautifulSoup
import mysql.connector

cnx = mysql.connector.connect(user ='XXXXX', password = 'XXXXX',
	host = 'XXXXX', database = 'XXXXX',
	auth_plugin = 'XXXXX')

cursor = cnx.cursor()

url = "http://www.espn.com/college-football/awards"
url_request = urllib2.urlopen(url)
html = BeautifulSoup(url_request, 'html.parser')

for item in html.find_all("a", {"class":"bi"}):
	url_to_scrape = ("http:" + item['href'])

	soup = BeautifulSoup(urllib2.urlopen(url_to_scrape), 'html.parser')

	try:

		award = soup.find("tr", {"class":"stathead"}).text
		columns = ["YEAR", "PLAYER", "SCHOOL"]

		player_data = []

		for value in soup.find_all("td")[4:]:
			player_data.append(value.text)

		for number in range(0, len(player_data), len(columns)):
			row = [award] + player_data[number:number + len(columns)]
			
			if int(row[1]) in range(2012, 2020):
		
				print(["AWARD"] + columns)
				print(', '.join(["'" + x + "'" for x in row]))

				cursor.execute("""INSERT INTO <YOUR TABLE NAME HERE (%s) VALUES (%s);""" % (', '.join(["AWARD"] + columns), ', '.join(["'" + x + "'" for x in row])))
				cnx.commit()

				print("SUCCESS!")

	except:
		pass
