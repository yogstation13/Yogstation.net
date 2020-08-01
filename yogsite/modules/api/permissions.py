from yogsite.const import *

class Permissions():
	def __init__(self, flags):
		self.flags = flags

	def can_manage_admins(self):
		return self.flags & PERM_DBRANKS

	def can_manage_bans(self):
		return self.flags & PERM_BAN

	def can_manage_books(self):
		return self.flags & PERM_ADMIN
	
	def can_manage_donors(self):
		return self.flags & PERM_SERVER and self.flags & PERM_PERMISSIONS

	def can_manage_mentors(self):
		return self.flags & PERM_PERMISSIONS

	def can_manage_notes(self):
		return self.flags & PERM_ADMIN
	
	def can_view_deleted(self):
		return self.flags & (PERM_ADMIN | PERM_SERVER | PERM_DEBUG)

	def can_view_logs(self):
		return self.flags & (PERM_ADMIN | PERM_SERVER | PERM_DEBUG)
	
	def can_view_player_stats(self):
		return self.flags & (PERM_ADMIN | PERM_SERVER)
	
	def can_view_activity_log(self):
		return self.flags & (PERM_ADMIN)