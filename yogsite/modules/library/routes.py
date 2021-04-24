from flask import abort, Blueprint, g, redirect, render_template, request, url_for

import math

from sqlalchemy import and_, or_

from yogsite.config import cfg
from yogsite import db
from yogsite.util import login_required, perms_required

blueprint = Blueprint("library", __name__)

@blueprint.route("/library")
def page_library():
	page = request.args.get('page', type=int, default=1)

	search_query = request.args.get('query', type=str, default=None)
	
	books_query = db.game_db.query(db.Book)

	if not (g.current_user.has_perms("book.delete") or g.current_user.has_perms("book.deleted")):
		books_query = books_query.filter(db.Book.deleted.is_(None))

	if search_query:
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

	page_count = math.ceil(books_query.count() / cfg.get("items_per_page")) # Selecting only the id on a count is faster than selecting the entire row

	displayed_books = books_query.limit(cfg.get("items_per_page")).offset((page - 1) * cfg.get("items_per_page"))

	return render_template("library/library.html", books=displayed_books, page=page, page_count=page_count, search_query=search_query)


@blueprint.route("/library/<string:book_id>")
def page_book(book_id):

	book = db.Book.from_id(book_id)

	if not book:
		return abort(404)
	
	return render_template("library/book.html", book=book)


@blueprint.route("/library/<string:book_id>/<string:action>", methods=["POST"])
@login_required
@perms_required("book.delete")
def page_book_action(book_id, action):

	book = db.Book.from_id(book_id)

	if action == "delete":
		db.ActionLog.add(g.current_user.ckey, book.ckey, f"Deleted book {book.id}, Title: {book.title}")
		book.set_deleted(True)

	elif action == "restore":
		db.ActionLog.add(g.current_user.ckey, book.ckey, f"Restored book {book.id}, Title: {book.title}")
		book.set_deleted(False)

	return redirect(request.referrer)
