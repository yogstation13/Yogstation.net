from flask import Blueprint
from flask import render_template

blueprint = Blueprint("bans", __name__)

@blueprint.route("/bans")
def page_bans():
	return render_template("bans.html")