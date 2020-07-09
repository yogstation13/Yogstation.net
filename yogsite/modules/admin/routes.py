from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import session

from sqlalchemy import or_

import math

from yogsite.config import cfg
from yogsite import db
from yogsite.util import login_required

blueprint = Blueprint("admin", __name__)

@blueprint.route("/login", methods=["GET", "POST"])
def page_login():
	if request.method == "POST":
		login_ckey = request.form.get("ckey")
		login_pass = request.form.get("password")

		admin_account = db.Admin.from_ckey(login_ckey)

		if admin_account and admin_account.check_password(login_pass):
			session["ckey"] = admin_account.ckey
			session["rank"] = admin_account.rank

			return redirect("/")
		else:
			return redirect("/login?failure=1")

	return render_template("admin/login.html")

@blueprint.route("/logout")
def page_logout():
	session.clear()

	return redirect("/")