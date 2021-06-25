from datetime import datetime

from flask import abort, Blueprint, flash, g, redirect, render_template, request, session, url_for

import math

import requests

from yogsite import db
from yogsite.config import cfg
from yogsite.util import is_safe_redirect, byondname_to_ckey
from yogsite.util.xenforo import validate_xenforo_credentials

from .models import User

blueprint = Blueprint("login", __name__)

@blueprint.route("/login", methods=["GET", "POST"])
def page_login():
	# Intercepting the password to then send it to xenforo is very cringe and often considered a security flaw but big boy xenforo isn't big boy enough to have basic oauth like any reasonable software
	if request.method == "POST":
		uname = request.form.get("username")
		passwd = request.form.get("password")

		auth_request = validate_xenforo_credentials(uname, passwd)
		if auth_request.status_code == 200: # Success AHHH I HATE THIS THIS IS SO INSECUREEE
			user_data = auth_request.json()["user"]

			byond_account = None
			if user_data["linked_accounts"]:
				for acc in user_data["linked_accounts"]:
					if acc["account_type"] == "byond":
						byond_account = acc["account_id"]

			if byond_account:
				# All the stars align, log this boy in
				session["username"] = user_data["username"] # Should in the future be moved somewhere else
				session["permissions"] = user_data["permissions"]
				session["ckey"] = byondname_to_ckey(byond_account) # Just in case the byond names are stored there for some reason

				db.ActionLog.add(session["ckey"], session["ckey"], "Logged in")

				flash("Successfully Logged In", "success")

				redirect_url = request.args.get('next') # Can specify where to go after login on the next arg
				if not is_safe_redirect(redirect_url):
					return abort(400)
			
				return redirect(redirect_url or "/")
			
			else: # No logging in unless you've linked your ckey
				flash("Account Has No Linked Ckey", "error")

		elif auth_request.status_code == 400: # 400, ruh roh, creds must have been wrong
			flash("Received Invalid Credentials", "error")
		
		else: # oh god what happened
			flash("Unknown Error, Please Report", "error")

	return render_template("login/login.html")


@blueprint.route("/logout")
def page_logout():
	db.ActionLog.add(g.current_user.ckey, g.current_user.ckey, "Logged out")
	session.clear()
	flash("Successfully Logged Out", "success")
	return redirect("/")
