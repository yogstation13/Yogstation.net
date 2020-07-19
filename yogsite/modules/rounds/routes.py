from flask import Blueprint
from flask import render_template
from flask import request

from sqlalchemy import or_

import math

from yogsite.config import cfg
from yogsite import db


blueprint = Blueprint("rounds", __name__)

@blueprint.route("/rounds")
def page_rounds():
	page = request.args.get('page', type=int, default=1)

	search_query = request.args.get('query', type=str, default=None)

	# This way of just shamelessly stringing together queries is probably bad and could be improved
	if search_query:
		# Search for rounds by either matching round id, game mode, or map name
		rounds_query = db.game_db.query(db.Round).filter(
			or_(
				db.Round.id.like(search_query),
				db.Round.game_mode.like(search_query),
				db.Round.map_name.like(search_query)
			)
		).order_by(db.Round.id.desc())
	else:
		rounds_query = db.game_db.query(db.Round).order_by(db.Round.id.desc())

	page_count = math.ceil(rounds_query.count() / cfg.items_per_page) # Selecting only the id on a count is faster than selecting the entire row

	displayed_rounds = rounds_query.limit(cfg.items_per_page).offset((page - 1) * cfg.items_per_page)

	return render_template("rounds.html", rounds=displayed_rounds, page=page, page_count=page_count, search_query=search_query)