from flask import abort
from flask import Blueprint
from flask import render_template
from flask import request

from yogsite.config import cfg

import requests

blueprint = Blueprint("donate", __name__)

@blueprint.route("/donate")
def page_donate():
	return render_template("donate.html")

@blueprint.route("/api/paypal_donate", methods=["GET", "POST"])
def page_api_paypal_donate():
	args_string = request.full_path.replace(request.path, "").lstrip("?") # Get just the arguments portion of the url
	
	response_request_url = f"{cfg.get('paypal.ipn_url')}?cmd=_notify-validate&{args_string}"

	print("Response Request Url:", response_request_url)

	verification_request = requests.get(response_request_url, headers={"User-Agent": "IPN-VerificationScript"})

	print(verification_request.content, verification_request)

	print(request.args)
	payment_amount = request.args.get("mc_gross", type=float)
	ckey = request.args.get("custom")

	print(payment_amount, ckey)

	return ""
