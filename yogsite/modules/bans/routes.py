from flask import Blueprint
from flask import g # what a terrible name
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

import math

from yogsite.config import cfg
from yogsite import db
from yogsite import util

from .forms import BanEditForm

blueprint = Blueprint("bans", __name__)

@blueprint.route("/bans")
def page_bans():
	page = request.args.get('page', type=int, default=1)

	search_query = request.args.get('query', type=str, default=None)

	if search_query:
		bans_query = db.game_db.query(db.Ban).filter(
			db.Ban.ckey.like(f"{search_query}")
		).order_by(db.Ban.id.desc())
	else:
		bans_query = db.game_db.query(db.Ban).order_by(db.Ban.id.desc())

	page_count = math.ceil(bans_query.count() / cfg.get("items_per_page")) # Selecting only the id on a count is faster than selecting the entire row

	displayed_bans = bans_query.limit(cfg.get("items_per_page")).offset((page - 1) * cfg.get("items_per_page"))

	return render_template("bans/bans.html", bans=displayed_bans, page=page, page_count=page_count, search_query=search_query)


@blueprint.route("/bans/<int:ban_id>/edit", methods=["GET", "POST"])
def page_ban_edit(ban_id):

	ban = db.Ban.from_id(ban_id)

	form_ban_edit = BanEditForm(request.form, prefix="form_ban_edit")


	if request.method == "POST":
		print(request.form)
		if form_ban_edit.validate():
			print("VALID", request.form, form_ban_edit)
			ban.apply_edit_form(form_ban_edit)

			return redirect(url_for("bans.page_ban_edit", ban_id=ban.id))

	else:
		# this absolute bs makes it so it only sets default values on the first get, and then every time you update with a post
		# it populates them with the new values from the post
		form_ban_edit.ckey.data = ban.ckey
		form_ban_edit.reason.data = ban.reason
		form_ban_edit.role.data = ban.role
		form_ban_edit.expiration_time.data = ban.expiration_time
		form_ban_edit.ip.data = util.IPAddress(ban.ip)
		form_ban_edit.computerid.data = ban.computerid

	return render_template("bans/edit.html", ban=ban, form=form_ban_edit)

@blueprint.route("/bans/<int:ban_id>/<string:action>")
def page_ban_action(ban_id, action):

	ban = db.Ban.from_id(ban_id)

	if action == "revoke":
		ban.revoke(g.current_user.username)
	
	elif action == "reinstate":
		ban.reinstate()
	
	return redirect(request.referrer)