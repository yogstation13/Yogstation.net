from flask import abort
from flask import Blueprint
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
from yogsite.util import login_required, perms_required

from .forms import BookEditForm

blueprint = Blueprint("library", __name__)

@blueprint.route("/library")
def page_library():
	page = request.args.get('page', type=int, default=1)

	search_query = request.args.get('query', type=str, default=None)
	
	books_query = db.game_db.query(db.Book)

	if not g.current_user.has_perms("book.delete"):
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

	page_count = math.ceil(books_query.count() / cfg.get("items_per_page")) # Selecting only the id on a count is faster than selecting the entire row

	displayed_books = books_query.limit(cfg.get("items_per_page")).offset((page - 1) * cfg.get("items_per_page"))

	return render_template("library/library.html", books=displayed_books, page=page, page_count=page_count, search_query=search_query)


@blueprint.route("/library/<string:book_id>")
def page_book(book_id):

	book = db.Book.from_id(book_id)

	if not book:
		return abort(404)
	
	return render_template("library/book.html", book=book)


@blueprint.route("/library/<string:book_id>/<string:action>")
@login_required
@perms_required("book.delete")
def page_book_action(book_id, action):

	book = db.Book.from_id(book_id)

	if action == "delete":
		book.set_deleted(True)

	elif action == "restore":
		book.set_deleted(False)

	return redirect(request.referrer)

""" Disabled because not complete and it's not on my todo list atm
@blueprint.route("/library/<int:book_id>/edit", methods=["GET", "POST"])
def page_book_edit(book_id):

	book = db.Book.from_id(book_id)

	form_book_edit = BookEditForm(request.form, prefix="form_book_edit")


	if request.method == "POST":
		print(request.form)
		if form_book_edit.validate():
			book.apply_edit_form(form_book_edit)

			return redirect(url_for("library.page_book", book_id=book.id))

	else:
		# this absolute bs makes it so it only sets default values on the first get, and then every time you update with a post
		# it populates them with the new values from the post
		form_book_edit.title.data = book.title
		form_book_edit.author.data = book.author
		form_book_edit.content.data = book.content
		form_book_edit.category.data = book.category

	return render_template("library/edit.html", book=book, form=form_book_edit)
"""