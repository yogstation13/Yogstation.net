from yogsite import db

from datetime import timedelta, date

from sqlalchemy import and_
from sqlalchemy import func

import math

class AdminActivityAnalytics():
	def __init__(self, start_date, end_date, rank_filter):
		self.admins = db.game_db.query(db.Admin)

		if rank_filter != "All":
			print(rank_filter)
			self.admins = self.admins.filter(db.Admin.rank == rank_filter)
		
		self.admins = self.admins.all()

		print(self.admins)

		self.start_date = start_date
		self.end_date = end_date

		self.connections = db.game_db.query(db.Connection).filter(db.Connection.ckey.in_([admin.ckey for admin in self.admins])).filter(
			and_(
				func.date(db.Connection.datetime) >= self.start_date,
				func.date(db.Connection.datetime) <= self.end_date
			)
		).all()

		print(self.connections)

		self.week = [[0]*24 for i in range(7)]


		self.day_repetitions = [0]*7 # How many times each day appeared in the time frame so we can calculate the average per day

		day_delta = timedelta(days=1) # Let's find what those day repetitions are
		cur_date = self.start_date
		while cur_date <= self.end_date:
			self.day_repetitions[cur_date.weekday()] += 1
			cur_date = cur_date + day_delta
		
		print(self.day_repetitions)


		for connection in self.connections:
			print(connection, connection.duration().total_seconds())

			if (connection.duration().total_seconds() // 60) >= 30: # Magic numbers mean ignore any connection less than ten minutes
				start_hour = connection.datetime.hour
				start_day = connection.datetime.weekday()

				for hour in range(int(math.ceil(connection.duration().total_seconds() // 3600))):
					marking_hour = (start_hour + hour) % 24 # Handle day rollover
					marking_day = start_day + (start_hour+hour) // 24

					if marking_day >= 7: # If it's outside of the week we're looking at, WE DONT CARE HAHAHAH
						break

					self.week[marking_day][marking_hour] += 1
		
		for day in range(7):
			for hour in range(24):
				if self.day_repetitions[day] > 0:
					self.week[day][hour] = int(round(self.week[day][hour] / self.day_repetitions[day], 0))
				else:
					self.week[day][hour] = None