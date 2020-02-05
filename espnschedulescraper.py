import urllib.request as urllib2
from bs4 import BeautifulSoup
import mysql.connector
import utility

cnx = mysql.connector.connect(user ='XXXXX', password = 'XXXXX',
	host = 'XXXXX', XXXXX = 'XXXXX',
	auth_plugin = 'XXXXX')

cursor = cnx.cursor()

fails = []

for year in range(2012, 2020):
	for value in utility.espn_list:
		team = value[0].replace("'", "")
		number = value[1][0]

		pre = "https://www.espn.com/college-football/team/schedule/_/id/"
		post = "/season/"

		url = pre + str(number) + post + str(year)

		vals = []
		final = []

		print("Scraping URL: " + url + " | "  + team)

		url_request = urllib2.urlopen(url)
		html = BeautifulSoup(url_request, 'html.parser')

		for item in html.find_all("tr"):
			for value in item.find_all("td"):
				if "," in value.text:
					vals.append("| " + value.text.strip())

				else:
					vals.append(value.text.strip())

		for item in vals[8:]:
			final.append(item.split("|"))

		flat_list = [item for sublist in final for item in sublist]

		index = 0

		try:
			for number in range(0, len(flat_list)):
				if len(flat_list[number]) < 1:
					game = flat_list[number + 1:number + 4]

					day = game[0].split(",")[0][1:]
					date = game[0].split(",")[1][1:]

					if "@" in game[1]:
						if game[1][1] == " ":
							pre_game = game[1]

						else:
							pre_game = game[1].replace(game[1][:1], game[1][:1] + " ")

						location = "Away"
						pre_opponent = pre_game.split("@ ")[1]
						
					elif "*" in game[1]:
						if game[1][2] == " ":
							pre_game = game[1]

						else:
							pre_game = game[1].replace(game[1][:2], game[1][:2] + " ")

						location = "Neutral Site"
						pre_opponent = pre_game.split("vs ")[1][:-2]
						
					elif "vs" in game[1]:
						if game[1][2] == " ":
							pre_game = game[1]

						else:
							pre_game = game[1].replace(game[1][:2], game[1][:2] + " ")

						location = "Home"
						pre_opponent = pre_game.split("vs ")[1]

					if pre_opponent[0].isalpha() == False:
						opponent = " ".join(pre_opponent.split(" ")[1:]).replace("'", "")
						opponent_rank = pre_opponent.split(" ")[0]

					else:
						opponent = pre_opponent.replace("'", "")
						opponent_rank = 0


					if "L" in game[2] and "OT" not in game[2]:
						result = "L"
						score = game[2].split("L")[1]
						points = [int(x) for x in score.split("-")]
						points_for = min(points)
						points_against = max(points)
						overtime = "-"

					elif "W" in game[2] and "OT" not in game[2]:
						result = "W"
						score = game[2].split("W")[1]
						points = [int(x) for x in score.split("-")]
						points_for = max(points)
						points_against = min(points)
						overtime = "-"

					elif "L" in game[2] and "OT" in game[2]:
						result = "L"
						pre_score = game[2].split("L")[1]
						score = pre_score.split(" ")[0]
						pre_points = [x for x in score.split("-")]
						points = [int(pre_points[0]), int(pre_points[1].split(" ")[0])]
						points_for = min(points)
						points_against = max(points)
						overtime = pre_score.split(" ")[1]

					elif "W" in game[2] and "OT" in game[2]:
						result = "W"
						pre_score = game[2].split("W")[1]
						score = pre_score.split(" ")[0]
						pre_points = [x for x in score.split("-")]
						points = [int(pre_points[0]), int(pre_points[1].split(" ")[0])]
						points_for = max(points)
						points_against = min(points)
						overtime = pre_score.split(" ")[1]

					else:
						pass

					columns = ', '.join(["year", "team", "day", "date", "opponent", "opponent_rank", "home_away", "win_loss", "score", "points_for", "points_against", "overtime"])
					week = [year, team, day, date, opponent, opponent_rank, location, result, score, points_for, points_against, overtime]
					week = ', '.join(["'" + str(x) + "'" for x in week])

					cursor.execute("""INSERT INTO <YOUR TABLE NAME HERE> (%s) VALUES (%s);""" % (columns, week))
					cnx.commit()

					print(week, "Successfully committed to database.")

		except Exception as e:
			print(e)
			fails.append((team, url, e))
			pass

print(fails)
