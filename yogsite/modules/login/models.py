from yogsite.config import cfg

# Dear future dev who comes across this file and thinks "is this some dumb magic?"

# Yes. Yes it is.

class User():
	username = None
	ckey = None
	permissions = [] # Husk of a user will have no perms
	
	@classmethod
	def from_session(cls, session):
		user = cls()

		if not "username" in session:
			return user # Return an empty user

		user.username = session["username"]
		user.ckey = session["ckey"]
		user.permissions = session["permissions"] if "permissions" in session else []
		
		return user
	
	def has_perms(self, *perms):
		for perm in perms:
			if perm not in self.permissions:
				return False
		
		return True
	
	def __bool__(self):
		return self.username is not None # If we are loggedin, we are truthy, otherwise falsey