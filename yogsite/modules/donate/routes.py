from flask import abort
from flask import Blueprint
from flask import render_template
from flask import request

from yogsite.config import cfg
from yogsite import db

from werkzeug.datastructures import ImmutableOrderedMultiDict

import requests
import math

blueprint = Blueprint("donate", __name__)

@blueprint.route("/donate")
def page_donate():
	return render_template("donate/donate.html")

@blueprint.route("/admin/donors")
def page_admin_donors():
	page = request.args.get('page', type=int, default=1)

	search_query = request.args.get('query', type=str, default=None)

	donations_query = db.game_db.query(db.Donation).order_by(db.Donation.datetime.desc())

	if search_query:
		donations_query = donations_query.filter(db.Donation.ckey.like(search_query))

	page_count = math.ceil(donations_query.count() / cfg.get("items_per_page")) # Selecting only the id on a count is faster than selecting the entire row

	displayed_donations = donations_query.offset((page-1)*cfg.get("items_per_page")).limit(cfg.get("items_per_page"))

	return render_template("donate/donation_log.html", donations=displayed_donations, page=page, page_count=page_count, search_query=search_query)

@blueprint.route("/api/paypal_donate", methods=["GET", "POST"])
def page_api_paypal_donate():
	print(request.full_path, request.path)

	args_string = ""
	request.parameter_storage_class = ImmutableOrderedMultiDict # so it retains order, because paypal needs that for some reason
	for x, y in request.form.items():
		args_string += f"&{x}={y}"

	print(args_string)

	response_request_url = f"{cfg.get('paypal.ipn_url')}?cmd=_notify-validate{args_string}"

	print("Response Request Url:", response_request_url)

	verification_request = requests.get(response_request_url, headers={"User-Agent": "IPN-VerificationScript"})

	print(verification_request.content, verification_request)

	if r.text == "VERIFIED":
		print("IT WORKED")
	else:
		print("it didn't work...")

	print(request.args, request.form)
	payment_amount = request.args.get("mc_gross", type=float)
	ckey = request.args.get("custom")

	print(payment_amount, ckey)

	return ""
