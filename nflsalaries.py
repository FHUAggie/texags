import urllib.request as urllib2
from bs4 import BeautifulSoup
import mysql.connector

cnx = mysql.connector.connect(user ='XXXXX', password = 'XXXXX',
	host = 'XXXXX', database = 'XXXXX',
	auth_plugin = 'mysql_native_password')

cursor = cnx.cursor()

cursor.execute("""select * from rivals_rankings2;""")
results = cursor.fetchall()

url = "https://www.pro-football-reference.com/players/salary.htm"
url_request = urllib2.urlopen(url)

columns = ["Player", "Pos", "Team", "Salary"]
html = BeautifulSoup(url_request, 'html.parser')

player_data = []

for line in html.find_all("td"):
	player_data.append(line.text.replace("'", ""))

for number in range(0, len(player_data), len(columns)):
	player = player_data[number:number + len(columns)]

	for item in results:
		if item[3] == player[0]:
			pid = item[0]
			salary = player[3][1:].replace(",", "")

			cursor.execute("""UPDATE <YOUR TABLE NAME HERE> SET current_salary = '%s' WHERE player_id = '%s';""" % (salary, pid))
			cnx.commit()

			print("SALARY SUCCESSFULLY ADDED: ", item)
      
      
