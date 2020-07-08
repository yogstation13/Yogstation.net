from flask import Blueprint
from flask import render_template
from flask import request

import math

from yogsite.config import cfg
from yogsite import db


blueprint = Blueprint("rounds", __name__)

@blueprint.route("/rounds")
def page_rounds():
	page = request.args.get('page', type=int, default=1)

	rounds = db.game_db.query(db.Round).order_by(db.Round.id.desc()).limit(cfg.items_per_page).offset((page - 1) * cfg.items_per_page)

	page_count = math.ceil(db.game_db.query(db.Round.id).count() / cfg.items_per_page) # Selecting only the id on a count is faster than selecting the entire row

	return render_template("rounds.html", rounds=rounds, page=page, page_count=page_count)