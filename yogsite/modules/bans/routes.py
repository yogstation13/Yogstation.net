from flask import Blueprint
from flask import render_template
from flask import request

import math

from yogsite.config import cfg
from yogsite import db


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

	page_count = math.ceil(bans_query.count() / cfg.items_per_page) # Selecting only the id on a count is faster than selecting the entire row

	displayed_bans = bans_query.limit(cfg.items_per_page).offset((page - 1) * cfg.items_per_page)

	return render_template("bans.html", bans=displayed_bans, page=page, page_count=page_count, search_query=search_query)