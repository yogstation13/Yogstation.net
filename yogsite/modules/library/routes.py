from flask import Blueprint
from flask import render_template
from flask import request

import math

from yogsite.config import cfg
from yogsite import db


blueprint = Blueprint("library", __name__)

@blueprint.route("/library")
def page_library():
	page = request.args.get('page', type=int, default=1)

	books = db.game_db.query(db.Book).order_by(db.Book.id.desc()).limit(cfg.items_per_page).offset((page - 1) * cfg.items_per_page)

	page_count = math.ceil(db.game_db.query(db.Book.id).count() / cfg.items_per_page) # Selecting only the id on a count is faster than selecting the entire row

	return render_template("library.html", books=books, page=page, page_count=page_count)