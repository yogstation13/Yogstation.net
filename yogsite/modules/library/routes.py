from flask import abort
from flask import Blueprint
from flask import g
from flask import render_template
from flask import request

from sqlalchemy import and_
from sqlalchemy import or_

import math

from yogsite.config import cfg
from yogsite import db


blueprint = Blueprint("library", __name__)

@blueprint.route("/library")
def page_library():
	page = request.args.get('page', type=int, default=1)

	search_query = request.args.get('query', type=str, default=None)
	
	books_query = db.game_db.query(db.Book)

	if not g.admin_perms.can_manage_books():
		books_query = books_query.filter(db.Book.deleted.is_(None))

	if search_query: # TODO: put this somewhere else
		books_query = books_query.filter(
			or_(
				db.Book.title.like(f"%{search_query}%"),
				db.Book.content.like(f"%{search_query}%"),
				db.Book.author.like(f"%{search_query}%"),
				db.Book.ckey.like(f"{search_query}"),
				db.Book.category.like(f"{search_query}")
			)
		)

	books_query = books_query.order_by(db.Book.id.desc())

	page_count = math.ceil(books_query.count() / cfg.items_per_page) # Selecting only the id on a count is faster than selecting the entire row

	displayed_books = books_query.limit(cfg.items_per_page).offset((page - 1) * cfg.items_per_page)

	return render_template("library/library.html", books=displayed_books, page=page, page_count=page_count, search_query=search_query)

@blueprint.route("/library/<string:book_id>")
def page_book(book_id):

	book = db.Book.from_id(book_id)

	if not book:
		return abort(404)
	
	return render_template("library/book.html", book=book)