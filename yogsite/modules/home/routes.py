from flask import Blueprint
from flask import render_template

blueprint = Blueprint("home", __name__)

@blueprint.route("/")
def page_home():
	return render_template("home.html")