from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import request
from flask import session

import math

from yogsite.config import cfg
from yogsite import db
from yogsite.util import query_server_status

blueprint = Blueprint("api", __name__)


@blueprint.route("/api/stats")
def page_api_stats():
	server_stats_list = []

	for server in cfg.get("servers"):
		server_stats = query_server_status(server)
		server_stats["server"] = server.__dict__

		server_stats_list.append(server_stats)
	
	return jsonify(server_stats_list)