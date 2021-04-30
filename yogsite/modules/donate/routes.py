from flask import abort, Blueprint, render_template, request

import math

import requests

from sqlalchemy import or_

from yogsite.config import cfg
from yogsite import db
from yogsite.extensions import flask_csrf_ext
from yogsite.util import byondname_to_ckey, login_required, perms_required

from werkzeug.datastructures import ImmutableOrderedMultiDict

from .transaction_processing import process_ipn_notification

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
		donations_query = donations_query.filter(
			or_(
				db.Donation.ckey.like(search_query),
				db.Donation.payer_email.like(search_query)
			)
		)

	page_count = math.ceil(donations_query.count() / cfg.get("items_per_page")) # Selecting only the id on a count is faster than selecting the entire row

	displayed_donations = donations_query.offset((page-1)*cfg.get("items_per_page")).limit(cfg.get("items_per_page"))

	return render_template("donate/donation_log.html", donations=displayed_donations, page=page, page_count=page_count, search_query=search_query)


@blueprint.route("/api/paypal_donate", methods=["POST"])
@flask_csrf_ext.exempt
def page_api_paypal_donate():
	args_string = ""
	request.parameter_storage_class = ImmutableOrderedMultiDict # so it retains order, because paypal needs that for some reason
	for x, y in request.form.items():
		args_string += f"&{x}={y}"

	response_request_url = f"{cfg.get('paypal.ipn_url')}?cmd=_notify-validate{args_string}"

	verification_request = requests.get(response_request_url, headers={"User-Agent": "IPN-VerificationScript"})

	if verification_request.text == "VERIFIED":
		process_ipn_notification(request.form)		

	return verification_request.text # Resend them back what they sent us to verify that we understood