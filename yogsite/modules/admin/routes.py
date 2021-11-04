from datetime import datetime, timedelta, date

from flask import abort, Blueprint, flash, g, jsonify, redirect, render_template, request, session, url_for

import math

from sqlalchemy import or_, and_

from yogsite.config import cfg
from yogsite import db
from yogsite.extensions import flask_limiter_ext
from yogsite.util import login_required, perms_required
from yogsite.util.xenforo import get_xenforo_groups

from .forms import SetLOAForm
from .activity_tracker import AdminActivityAnalytics

blueprint = Blueprint("admin", __name__)

@blueprint.route("/admin/loa", methods=["GET", "POST"])
@login_required
@perms_required("loa.add")
def page_loa():
	form_set_loa = SetLOAForm(request.form, prefix="form_set_loa")

	loas = db.game_db.query(db.LOA).filter(
		db.LOA.expiry_time > datetime.utcnow() - timedelta(days=30)
	).order_by(db.LOA.id.desc()) # Get LOAs sorted by start time

	if not g.current_user.has_perms("loa.others"):
		loas = loas.filter(db.LOA.ckey == g.current_user.ckey)

	if request.method == "POST":
		if form_set_loa.validate_on_submit():

			if g.current_user.has_perms("loa.others"):
				ckey = form_set_loa.ckey.data
			else:
				ckey = g.current_user.ckey	# If they dont have the perm they should never be able to set it to
											# anything else anyway so the only reason this is used is if an
											# admin is tampering with something

			db.LOA.add(admin_ckey=ckey, reason=form_set_loa.reason.data, expiry_time=form_set_loa.expiration_time.data)
			flash("Successfully Set LOA", "success")
			
			return redirect(url_for("admin.page_loa"))
	else:
		form_set_loa.ckey.data = g.current_user.ckey

	return render_template("admin/loa_manager.html", 
		loas = loas, form_set_loa = form_set_loa
	)


@blueprint.route("/admin/loa/<int:loa_id>/<string:action>", methods=["POST"])
@login_required
@perms_required("loa.add")
def page_loa_action(loa_id, action):

	loa = db.LOA.from_id(loa_id)

	if loa.ckey != g.current_user.ckey and not g.current_user.has_perms("loa.others"):
		return abort(401) # Can't revoke other people's LOAs unless we have the perm for that

	if action == "revoke":
		loa.set_revoked(True)
		flash("Successfully Revoked LOA", "success")
	
	return redirect(request.referrer)


@blueprint.route("/admin/activity")
@flask_limiter_ext.limit("10 per minute")
@login_required
@perms_required("activity.access")
def page_activity():
	admin_groups = get_xenforo_groups()
	enabled_groups = [group for group in admin_groups if group.group_id not in cfg.get("activity_tracker.excluded_groups")]

	return render_template("admin/activity_tracker.html", admin_groups=enabled_groups)


@blueprint.route("/api/admin/activity")
@login_required
@perms_required("activity.access")
def page_api_activity():
	start_date = request.args.get("start_date")
	end_date = request.args.get("end_date")
	enabled_groups = request.args.getlist("enabled_ranks[]")
	included_ckeys = request.args.getlist("included_ckeys[]")

	if start_date == None or end_date == None:
		return abort(400)
	
	analytics = AdminActivityAnalytics(datetime.strptime(start_date, "%Y-%m-%d").date(), datetime.strptime(end_date, "%Y-%m-%d").date(), enabled_groups=enabled_groups, included_ckeys=included_ckeys)
	
	return jsonify(analytics.admin_leaderboard())


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
