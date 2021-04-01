from flask import abort, Blueprint, flash, g, redirect, render_template, request, url_for

import math

from sqlalchemy import and_, or_

from yogsite.config import cfg
from yogsite import db
from yogsite.extensions import flask_limiter_ext

from .forms import NoteAddForm

blueprint = Blueprint("directory", __name__)

@blueprint.route("/players")
def page_directory():
	page = request.args.get('page', type=int, default=1)

	search_query = request.args.get('query', type=str, default=None)

	players_query = db.game_db.query(db.Player)

	if search_query:
		players_query = players_query.filter(
			or_(
				db.Player.ckey.like(f"%{search_query}%"),
				db.Player.byond_key.like(f"%{search_query}%"),
				db.Player.discord_id.like(search_query)
			)
		)

	players_query = players_query.order_by(db.Player.lastseen.desc())

	page_count = math.ceil(players_query.count() / cfg.get("items_per_page")) # Selecting only the id on a count is faster than selecting the entire row

	displayed_players = players_query.limit(cfg.get("items_per_page")).offset((page - 1) * cfg.get("items_per_page"))

	return render_template("directory/directory.html", players=displayed_players, page=page, page_count=page_count, search_query=search_query)

@blueprint.route("/players/<string:ckey>", methods=["GET", "POST"])
@flask_limiter_ext.limit("10 per minute")
def page_player(ckey):

	player = db.Player.from_ckey(ckey)

	form_note_add = NoteAddForm(request.form, prefix="form_note_add")

	if request.method == "POST":
		if form_note_add.validate_on_submit():
			if g.current_user.has_perms("note.manage"):

				db.Note.add_from_form(form_note_add, ckey)

				db.ActionLog.add(g.current_user.ckey, ckey, f"Added note of type {form_note_add.type.data}: \"{form_note_add.text.data}\"")

				flash("Note Successfully Added", "success")

				return redirect(url_for("directory.page_player", ckey=ckey))

	if not player:
		return abort(404)
	
	return render_template("directory/player.html", player=player, form_note_add=form_note_add)