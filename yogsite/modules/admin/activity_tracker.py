from yogsite import db

class AdminActivityAnalytics():
	def __init__(self, week):
		self.admins = db.game_db.query(db.Admin).all()
		print(self.admins)

		self.connections = db.game_db.query(db.Connection).filter(db.Connection.ckey.in_([admin.ckey for admin in self.admins])).all()

		print(self.connections)

		self.week = [[0]*24 for i in range(7)]


		for connection in self.connections:
			print(connection, connection.duration().total_seconds())

			if (connection.duration().total_seconds() // 60) >= 10: # Magic numbers mean ignore any connection less than ten minutes
				start_hour = connection.datetime.hour
				start_day = connection.datetime.weekday()

				print(start_hour, start_day)

				for hour in range(int(connection.duration().total_seconds() // 3600)):
					marking_hour = (start_hour + hour) % 24 # Handle day rollover
					marking_day = start_day + (start_hour+hour) // 24

					print(hour, marking_hour, marking_day)

					if marking_day >= 7: # If it's outside of the week we're looking at, WE DONT CARE HAHAHAH
						break

					self.week[marking_day][marking_hour] += 1

		print(self.week)
					
				

