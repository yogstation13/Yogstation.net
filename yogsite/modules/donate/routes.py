from flask import Blueprint
from flask import render_template

blueprint = Blueprint("donate", __name__)

@blueprint.route("/donate")
def page_donate():
	return render_template("donate.html")