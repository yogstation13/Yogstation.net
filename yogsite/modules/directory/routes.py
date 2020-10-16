from flask import abort
from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from sqlalchemy import and_
from sqlalchemy import or_

import math

from yogsite.config import cfg
from yogsite import db

from .forms import NoteAddForm

blueprint = Blueprint("directory", __name__)

@blueprint.route("/players")
def page_directory():
	page = request.args.get('page', type=int, default=1)

	search_query = request.args.get('query', type=str, default=None)

	players_query = db.game_db.query(db.Player)

	if search_query: # TODO: put this somewhere else
		players_query = players_query.filter(
			or_(
				db.Player.ckey.like(f"%{search_query}%"),
				db.Player.byond_key.like(f"%{search_query}%"),
				db.Player.discord_id.like(search_query)
			)
		)

	players_query = players_query.order_by(db.Player.ckey.asc())

	page_count = math.ceil(players_query.count() / cfg.get("items_per_page")) # Selecting only the id on a count is faster than selecting the entire row

	displayed_players = players_query.limit(cfg.get("items_per_page")).offset((page - 1) * cfg.get("items_per_page"))

	return render_template("directory/directory.html", players=displayed_players, page=page, page_count=page_count, search_query=search_query)


@blueprint.route("/players/<string:ckey>", methods=["GET", "POST"])
def page_player(ckey):

	player = db.Player.from_ckey(ckey)

	form_note_add = NoteAddForm(request.form, prefix="form_note_add")

	if request.method == "POST":
		if form_note_add.validate_on_submit():
			if g.current_user.has_perms("note.manage"):

				db.Note.add(ckey=ckey, admin=g.current_user.ckey, description=form_note_add.description.data)

				db.ActionLog.add(g.current_user.ckey, ckey, f"Added note \"{form_note_add.description.data}\"")

				flash("Note Successfully Added", "success")

				return redirect(url_for("directory.page_player", ckey=ckey))

	if not player:
		return abort(404)
	
	return render_template("directory/player.html", player=player, form_note_add=form_note_add)