from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from sqlalchemy import or_

import math

from yogsite.config import cfg
from yogsite import db
from yogsite.util import login_required

from .forms import SetLOAForm

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


@blueprint.route("/admin/admins", methods=["GET", "POST"])
def page_manage_admins():

	form_set_loa = SetLOAForm(request.form, prefix="form_set_loa")

	admins = db.game_db.query(db.Admin).order_by(db.Admin.ckey) # Get admins sorted by ckey

	loas = db.game_db.query(db.LOA).order_by(db.LOA.time) # Get LOAs sorted by start time

	admin_ranks = db.game_db.query(db.AdminRank)

	if request.method == "POST":
		if form_set_loa.validate_on_submit():
			print ("loa works")
			return redirect(url_for("admin.page_manage_admins"))

	return render_template("admin/manage_admins.html", 
		admins=admins, loas=loas, admin_ranks=admin_ranks,
		form_set_loa = form_set_loa
	)