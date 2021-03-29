from yogsite.config import cfg

from functools import wraps
from flask import abort, g, redirect, request, url_for

def login_required(view_function):
	"""
	This decorator ensures a user is logged in before they may view a page.
	If not, it redirects them to the login screen, and brings them back after they log in
	"""
	@wraps(view_function)

	def decorated_function(*args, **kwargs):
		if not g.current_user:
			return redirect(url_for("login.page_login", next=request.url))
		
		return view_function(*args, **kwargs)
	
	return decorated_function

def perms_required(*perms):
	"""
	This decorator only lets a request go through if the requesting user has all of the permissions specified
	"""
	def wrapper(view_function):

		@wraps(view_function)
		
		def decorated_function(*args, **kwargs):
			if g.current_user.has_perms(*perms):
				return view_function(*args, **kwargs)
			
			return abort(401) # User doesn't have perms, get out of here

		return decorated_function

	return wrapper