from datetime import datetime, timedelta, date

from flask import abort
from flask import Blueprint
from flask import flash
from flask import g
from flask import jsonify
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
from .activity_tracker import AdminActivityAnalytics

blueprint = Blueprint("admin", __name__)

@blueprint.route("/admin/loa", methods=["GET", "POST"])
@login_required
def page_loa():
	form_set_loa = SetLOAForm(request.form, prefix="form_set_loa")

	loas = db.game_db.query(db.LOA).filter(
		and_(
			or_(
				db.LOA.revoked == 0,
				db.LOA.revoked == None # don't ask me why it has to be done like this, I, don't know.
			),
			db.LOA.expiry_time > datetime.utcnow()
		)
	).order_by(db.LOA.id.desc()) # Get LOAs sorted by start time

	if not g.current_user.has_perms("loa.others"):
		loas = loas.filter(db.LOA.ckey == g.current_user.ckey)

	if request.method == "POST":
		if form_set_loa.validate_on_submit():
			db.LOA.add(g.current_user.ckey, reason=form_set_loa.reason.data, expiry_time=form_set_loa.expiration_time.data)
			flash("Successfully Set LOA", "success")
			
			return redirect(url_for("admin.page_loa"))

	return render_template("admin/loa_manager.html", 
		loas = loas, form_set_loa = form_set_loa
	)


@blueprint.route("/admin/loa/<int:loa_id>/<string:action>")
@login_required
def page_loa_action(loa_id, action):

	loa = db.LOA.from_id(loa_id)

	if action == "revoke":
		loa.set_revoked(True)
		flash("Successfully Revoked LOA", "success")
	
	return redirect(request.referrer)


@blueprint.route("/admin/activity")
@login_required
@perms_required("activity.access")
def page_activity():
	admin_ranks = db.game_db.query(db.AdminRank).all()

	return render_template("admin/activity_tracker.html", admin_ranks=admin_ranks)

@blueprint.route("/api/admin/activity")
@login_required
@perms_required("activity.access")
def page_api_activity():
	start_date = request.args.get("start_date")
	end_date = request.args.get("end_date")
	rank_filter = request.args.get("rank_filter")

	if not start_date or not end_date or not rank_filter:
		return abort(400)
	
	analytics = AdminActivityAnalytics(datetime.strptime(start_date, "%Y-%m-%d").date(), datetime.strptime(end_date, "%Y-%m-%d").date(), rank_filter=rank_filter)
	return jsonify(analytics.week)

@blueprint.route("/admin/action_log")
@login_required
@perms_required("action_log.access")
def page_action_log():
	page = request.args.get('page', type=int, default=1)

	search_query = request.args.get('query', type=str, default=None)

	if search_query:
		action_log_query = db.game_db.query(db.ActionLog).filter(
			or_(
				db.ActionLog.adminid.like(search_query),
				db.ActionLog.target.like(search_query),
				db.ActionLog.description.like(f"%{search_query}%")
			)
		).order_by(db.ActionLog.id.desc())
	else:
		action_log_query = db.game_db.query(db.ActionLog).order_by(db.ActionLog.timestamp.desc())

	page_count = math.ceil(action_log_query.count() / cfg.get("items_per_page")) # Selecting only the id on a count is faster than selecting the entire row

	displayed_logs = action_log_query.limit(cfg.get("items_per_page")).offset((page - 1) * cfg.get("items_per_page"))

	return render_template("admin/action_log.html", action_log=displayed_logs, page=page, page_count=page_count, search_query=search_query)

