from datetime import datetime

from dateutil.relativedelta import relativedelta

from flask import abort, Blueprint, render_template, request

import math

import requests

from yogsite.config import cfg
from yogsite import db
from yogsite.util import byondname_to_ckey, login_required, perms_required

from werkzeug.datastructures import ImmutableOrderedMultiDict

blueprint = Blueprint("donate", __name__)

@blueprint.route("/donate")
def page_donate():
	return render_template("donate/donate.html")


@blueprint.route("/admin/donors")
@login_required
@perms_required("transaction_log.access")
def page_admin_donors():
	page = request.args.get('page', type=int, default=1)

	search_query = request.args.get('query', type=str, default=None)

	donations_query = db.game_db.query(db.Donation).order_by(db.Donation.datetime.desc())

	if search_query:
		donations_query = donations_query.filter(db.Donation.ckey.like(search_query))

	page_count = math.ceil(donations_query.count() / cfg.get("items_per_page")) # Selecting only the id on a count is faster than selecting the entire row

	displayed_donations = donations_query.offset((page-1)*cfg.get("items_per_page")).limit(cfg.get("items_per_page"))

	return render_template("donate/donation_log.html", donations=displayed_donations, page=page, page_count=page_count, search_query=search_query)


@blueprint.route("/api/paypal_donate", methods=["POST"])
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

	if verification_request.text == "VERIFIED":
		print("IT WORKED")
		amount = request.form.get("mc_gross", type=float)

		# Get how many months they earn from this donation amount
		months = 0
		for tier in cfg.get("donation.tiers"):
			if amount >= tier["amount"]:
				if tier["months"] > months:
					months = tier["months"]

		donate_time = datetime.utcnow()
		expiration_time = donate_time + relativedelta(months=months)

		ckey = byondname_to_ckey(request.form.get("custom", type=str))

		donation = db.Donation(
			ckey = ckey,
			transaction_id = request.form.get("txn_id", type=str),
			amount = request.form.get("mc_gross", type=float),
			datetime = donate_time,
			expiration_time = expiration_time
		)

		db.game_db.add(donation)
		db.game_db.commit()
		
	else:
		print("it didn't work...")

	print(request.form)
	payment_amount = request.form.get("mc_gross", type=float)
	ckey = request.form.get("custom")

	print(payment_amount, ckey)

	return verification_request.text # Resend them back what they sent us to verify that we understood