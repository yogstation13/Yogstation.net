from flask import Blueprint
from flask import jsonify
from flask import render_template

from yogsite.util.xenforo import get_frontpage_staff

blueprint = Blueprint("home", __name__)

@blueprint.route("/")
def page_home():
	return render_template("home.html")

@blueprint.route("/api/frontpage_staff")
def page_api_frontpage_staff():
	return jsonify(get_frontpage_staff())