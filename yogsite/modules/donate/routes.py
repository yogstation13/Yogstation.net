from flask import abort
from flask import Blueprint
from flask import render_template
from flask import request

from yogsite.config import cfg

from werkzeug.datastructures import ImmutableOrderedMultiDict

import requests

blueprint = Blueprint("donate", __name__)

@blueprint.route("/donate")
def page_donate():
	return render_template("donate.html")

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
