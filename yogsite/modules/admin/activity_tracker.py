from yogsite import db
from yogsite.util.xenforo import get_xenforo_ckeys_from_groups

from datetime import timedelta, date

from sqlalchemy import and_
from sqlalchemy import func

import math

class AdminActivityAnalytics():
	def __init__(self, start_date, end_date, enabled_ranks):
		admin_ckeys = get_xenforo_ckeys_from_groups(enabled_ranks)

		self.admins = db.game_db.query(db.Admin).filter(db.Admin.ckey.in_(admin_ckeys)).all()

		self.start_date = start_date
		self.end_date = end_date

		self.connections = db.game_db.query(db.Connection).filter(db.Connection.ckey.in_([admin.ckey for admin in self.admins])).filter(
			and_(
				func.date(db.Connection.datetime) >= self.start_date,
				func.date(db.Connection.datetime) <= self.end_date
			)
		).all()

	def admin_playtime(self, admin_ckey):
		total_playtime = timedelta(0)

		for connection in self.connections:
			if connection.ckey == admin_ckey:
				total_playtime += connection.duration()
		
		return total_playtime
	
	def admin_leaderboard(self):
		leaderboard = []
		
		for admin in self.admins:
			leaderboard.append({"rank": admin.rank,"ckey": admin.ckey, "playtime": self.admin_playtime(admin.ckey).total_seconds()})
		
		return sorted(leaderboard, key=lambda e: e["playtime"], reverse=True)