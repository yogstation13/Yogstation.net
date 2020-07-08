from flask import abort
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

	books = db.game_db.query(db.Book).filter(db.Book.deleted.is_(None)).order_by(db.Book.id.desc()).limit(cfg.items_per_page).offset((page - 1) * cfg.items_per_page)

	page_count = math.ceil(db.game_db.query(db.Book.id).filter(db.Book.deleted.is_(None)).count() / cfg.items_per_page) # Selecting only the id on a count is faster than selecting the entire row

	return render_template("library/library.html", books=books, page=page, page_count=page_count)

@blueprint.route("/library/<string:book_id>")
def page_book(book_id):

	book = db.Book.from_id(book_id)

	if not book:
		return abort(404)
	
	return render_template("library/book.html", book=book)