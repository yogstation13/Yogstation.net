from datetime import timedelta, date

import math

from sqlalchemy import and_, func

from yogsite.config import cfg
from yogsite import db
from yogsite.util.xenforo import get_xenforo_users_from_groups, XenforoUser

class AdminActivityAnalytics():
	def __init__(self, start_date, end_date, enabled_groups, included_ckeys):
		enabled_groups = [group_id for group_id in enabled_groups if group_id not in cfg.get("activity_tracker.excluded_groups")]

		self.admins = get_xenforo_users_from_groups(enabled_groups) + [XenforoUser(ckey=ckey) for ckey in included_ckeys]
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
			leaderboard.append({
				"highest_group_name": admin.get_highest_group().name if len(admin.groups) else None,
				"ckey": admin.ckey,
				"playtime": self.admin_playtime(admin.ckey).total_seconds()
			})
		
		return sorted(leaderboard, key=lambda e: e["playtime"], reverse=True)