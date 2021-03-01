from flask import abort
from flask import Blueprint
from flask import render_template
from flask import request

blueprint = Blueprint("donate", __name__)

@blueprint.route("/donate")
def page_donate():
	return render_template("donate.html")

@blueprint.route("/api/paypal_donate", methods=["GET", "POST"])
def page_api_paypal_donate():
	print(request.args, request.form, request.url)
	return ""