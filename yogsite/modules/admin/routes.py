from datetime import datetime

from flask import abort
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from sqlalchemy import or_, and_

import math

from yogsite import db
from yogsite.config import cfg
from yogsite.util import login_required, perms_required

from .forms import SetLOAForm

blueprint = Blueprint("admin", __name__)

@blueprint.route("/admin/admins", methods=["GET", "POST"])
@login_required
def page_manage_admins():

	form_set_loa = SetLOAForm(request.form, prefix="form_set_loa")

	admins = db.game_db.query(db.Admin).order_by(db.Admin.ckey) # Get admins sorted by ckey

	loas = db.game_db.query(db.LOA).filter(
		and_(
			or_(
				db.LOA.revoked == 0,
				db.LOA.revoked == None # don't ask me why it has to be done like this, I, don't know.
			),
			db.LOA.expiry_time > datetime.utcnow()
		)
	).order_by(db.LOA.time) # Get LOAs sorted by start time

	admin_ranks = db.game_db.query(db.AdminRank)

	if request.method == "POST":
		if form_set_loa.validate_on_submit():
			print ("loa works")
			return redirect(url_for("admin.page_manage_admins"))

	return render_template("admin/manage_admins.html", 
		admins=admins, loas=loas, admin_ranks=admin_ranks,
		form_set_loa = form_set_loa
	)


@blueprint.route("/admin/loa/<int:loa_id>/<string:action>")
@login_required
def page_loa_action(loa_id, action):

	loa = db.LOA.from_id(loa_id)

	if action == "revoke":
		loa.set_revoked(True)
	
	return redirect(request.referrer)



@blueprint.route("/admin/activity")
@login_required
@perms_required("activity.access")
def page_activity():
	return render_template("admin/activity_tracker.html")