from flask import abort, Blueprint, flash, g, jsonify, redirect, render_template, request, url_for

import math

from yogsite.config import cfg
from yogsite import db
from yogsite.extensions import flask_limiter_ext
from yogsite.util import byondname_to_ckey, login_required, perms_required, IPAddress

from .forms import BanEditForm

blueprint = Blueprint("bans", __name__)

@blueprint.route("/bans")
@flask_limiter_ext.limit("60 per minute")
def page_bans():
	page = request.args.get('page', type=int, default=1)

	search_query = request.args.get('query', type=str, default=None)

	bans_query = db.query_grouped_bans(search_query=search_query)

	if not g.current_user.has_perms("ban.manage"):
		current_round = db.Round.get_latest()

		bans_query = bans_query.filter(db.Ban.round_id != current_round.id) # Don't let normal users see bans from the current round

	page_length = cfg.get("items_per_page")

	json_format = bool(request.args.get("json"))
	if json_format:
		page_length = max(1, min(request.args.get("amount", type=int, default=page_length), 1000))

	page_count = math.ceil(bans_query.count() / page_length) # Selecting only the id on a count is faster than selecting the entire row

	bans_query = bans_query.offset((page-1)*page_length).limit(page_length)

	if json_format:
		bans_json = [{
			"id": ban.id,
			"bantime": str(ban.bantime),
			"round_id": ban.round_id,
			"expiration_time": str(ban.expiration_time) if ban.expiration_time else None,
			"reason": ban.reason,
			"ckey": ban.ckey,
			"a_ckey": ban.a_ckey,
			"unbanned_datetime": str(ban.unbanned_datetime) if ban.unbanned_datetime else None,
			"unbanned_ckey": ban.unbanned_ckey,
			"roles": ban.roles.split(",")
		} for ban in bans_query]

		return jsonify(bans_json)

	return render_template("bans/bans.html", bans=bans_query, page=page, page_count=page_count, search_query=search_query)


@blueprint.route("/api/last_ip_cid")
@perms_required("ban.manage") # Hopefully the permissions system is secure or else rip everyone's ip and cid
def page_api_last_ip_cid():
	ckey = byondname_to_ckey(request.args.get("ckey", type=str))

	if not ckey:
		return jsonify({"success": False, "error": "You must specify a ckey"}), 400
	
	last_connection = db.game_db.query(db.Connection).filter(db.Connection.ckey == ckey).order_by(db.Connection.datetime.desc()).first()

	if not last_connection:
		return jsonify({"success": False, "error": "No connections found for this ckey"}), 404
	
	return jsonify({"success": True, "data": {	# considering were just sending over ip and cid, we should probably
		"ip": last_connection.ip,				# make sure that this is a good deal secure, wouldn't you think?
		"computerid": last_connection.computerid
	}})


@blueprint.route("/bans/<int:ban_id>/edit", methods=["GET", "POST"])
@login_required
@perms_required("ban.manage")
def page_ban_edit(ban_id):

	grouped_ban = db.Ban.grouped_from_id(ban_id)

	form_ban_edit = BanEditForm(request.form, prefix="form_ban_edit")

	if request.method == "POST":
		if form_ban_edit.validate():
			single_ban = db.Ban.from_id(ban_id) # Can't apply stuff to the grouped result
			new_single_ban = single_ban.apply_edit_form(form_ban_edit)

			db.ActionLog.add(g.current_user.ckey, new_single_ban.ckey,
				f"Edited ban {new_single_ban.id}: " +
				f"roles={','.join(form_ban_edit.roles.data)} " +
				f"reason={form_ban_edit.reason.data} " +
				f"expiration_time={form_ban_edit.expiration_time.data} " +
				f"ip={form_ban_edit.ip.data} " +
				f"computerid={form_ban_edit.computerid.data}"
			)

			flash("Ban Successfully Edited", "success")

			return redirect(url_for("bans.page_ban_edit", ban_id=new_single_ban.id))

	else:
		# this absolute bs makes it so it only sets default values on the first get, and then every time you update with a post
		# it populates them with the new values from the post
		form_ban_edit.ckey.data = grouped_ban.ckey
		form_ban_edit.reason.data = grouped_ban.reason
		form_ban_edit.roles.data = [role for role in grouped_ban.roles.split(",")]
		form_ban_edit.expiration_time.data = grouped_ban.expiration_time
		form_ban_edit.ip.data = IPAddress(grouped_ban.ip) if grouped_ban.ip else None
		form_ban_edit.computerid.data = grouped_ban.computerid

	return render_template("bans/edit.html", ban=grouped_ban, form=form_ban_edit)


@blueprint.route("/bans/add", methods=["GET", "POST"])
@login_required
@perms_required("ban.add")
def page_ban_add():

	form_ban_edit = BanEditForm(request.form, prefix="form_ban_edit") # We can use the same form as editing since it has the same fields

	if request.method == "POST":
		if form_ban_edit.validate():
			db.Ban.add_from_form(form_ban_edit)

			flash("Ban Successfully Added", "success")

			return redirect(url_for("bans.page_ban_add"))

	else:
		if request.args.get("ckey"):
			form_ban_edit.ckey.data = request.args.get("ckey")
		form_ban_edit.roles.data = ["Server"] # Default to a server ban, not a job ban
	
	return render_template("bans/edit.html", form=form_ban_edit)


@blueprint.route("/bans/<int:ban_id>/<string:action>", methods=["POST"])
@login_required
@perms_required("ban.manage")
def page_ban_action(ban_id, action):

	ban = db.Ban.from_id(ban_id)

	if action == "revoke":
		db.ActionLog.add(g.current_user.ckey, ban.ckey, f"Revoked ban {ban.id}")
		ban.revoke(g.current_user.ckey)
		flash("Ban Successfully Revoked", "success")
	
	elif action == "reinstate":
		db.ActionLog.add(g.current_user.ckey, ban.ckey, f"Reinstated ban {ban.id}")
		ban.reinstate()
		flash("Ban Successfully Reinstated", "success")
	
	return redirect(request.referrer)


@blueprint.route("/notes/<int:note_id>/<string:action>", methods=["POST"])
@login_required
@perms_required("note.manage")
def page_note_action(note_id, action):

	note = db.Note.from_id(note_id)

	if action == "delete":
		db.ActionLog.add(g.current_user.ckey, note.targetckey, f"Deleted note {note.id}")
		note.set_deleted(True)
		flash("Note Successfully Deleted", "success")
	
	return redirect(request.referrer)