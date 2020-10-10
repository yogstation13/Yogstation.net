# Dear future dev who comes across this file and thinks "is this some dumb magic?"

# Yes. Yes it is.

class User():
	username = None
	permissions = []
	
	@classmethod
	def from_session(cls, session):
		user = cls()

		if not "username" in session:
			return

		user.username = session["username"]
		user.permissions = session["permissions"] if "permissions" in session else []
		
		return user
	
	def has_permission(self, perm):
		return perm in self.permissions