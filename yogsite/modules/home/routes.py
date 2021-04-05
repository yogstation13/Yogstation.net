from flask import abort, Blueprint, jsonify, redirect, render_template

from yogsite.util import get_primary_server, get_server
from yogsite.util.xenforo import get_frontpage_staff

blueprint = Blueprint("home", __name__)

@blueprint.route("/")
def page_home():
	return render_template("home.html")

@blueprint.route("/join")
def page_join():
	server = get_primary_server()

	if not server:
		abort(501) # We should always have at least one server
	
	return redirect(f"byond://{server['host']}:{server['port']}")

@blueprint.route("/join/<string:server_id>")
def page_join_server_id(server_id):
	server = get_server(server_id)

	if not server:
		abort(404)

	return redirect(f"byond://{server['host']}:{server['port']}")

@blueprint.route("/api/frontpage_staff")
def page_api_frontpage_staff():
	return jsonify(get_frontpage_staff())