from flask import abort, Blueprint, jsonify, redirect, request, session

import math

from yogsite.config import cfg
from yogsite import db
from yogsite.util import query_server_status

blueprint = Blueprint("api", __name__)

@blueprint.route("/api/stats/<string:server_id>")
def page_api_stats_server_id(server_id):
	if server_id not in cfg.get("servers"):
		return jsonify({"error": "server id not found"})

	server_stats = query_server_status(server_id)
	return jsonify(server_stats)
