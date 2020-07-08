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

	bans = db.game_db.query(db.Ban).order_by(db.Ban.id.desc()).limit(cfg.items_per_page).offset((page - 1) * cfg.items_per_page)

	page_count = math.ceil(db.game_db.query(db.Ban.id).count() / cfg.items_per_page) # Selecting only the id on a count is faster than selecting the entire row

	return render_template("bans.html", bans=bans, page=page, page_count=page_count)