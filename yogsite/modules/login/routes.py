from datetime import datetime

from flask import abort
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

import math

import requests

from yogsite import db
from yogsite.config import cfg
from yogsite.config import XENFORO_HEADERS
from yogsite.util import is_safe_redirect
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

			if user_data["linked_accounts"] and ("byond" in user_data["linked_accounts"]):
				# All the stars align, log this boy in

				session["username"] = user_data["username"] # Should in the future be moved somewhere else
				session["permissions"] = user_data["permissions"]
				session["ckey"] = user_data["linked_accounts"]["byond"]

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
	session.clear()
	flash("Successfully Logged Out", "success")
	return redirect("/")