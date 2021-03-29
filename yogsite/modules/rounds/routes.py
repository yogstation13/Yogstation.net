from flask import abort
from flask import Blueprint
from flask import g
from flask import jsonify
from flask import render_template
from flask import request
from flask import Response
from flask import stream_with_context

from sqlalchemy import or_

import math

from yogsite.config import cfg
from yogsite import db
from yogsite.util import login_required, perms_required, yield_file_chunks

from .log_parsing import RoundLogs


blueprint = Blueprint("rounds", __name__)

@blueprint.route("/rounds")
def page_rounds():
	page = request.args.get('page', type=int, default=1)

	search_query = request.args.get('query', type=str, default=None)

	# This way of just shamelessly stringing together queries is probably bad and could be improved

	rounds_query = db.game_db.query(db.Round)

	if not g.current_user.has_perms("round.active"):
		rounds_query = rounds_query.filter(db.Round.shutdown_datetime.isnot(None))

	if search_query:
		# Search for rounds by either matching round id, game mode, or map name
		rounds_query = rounds_query.filter(
			or_(
				db.Round.id.like(search_query),
				db.Round.game_mode.like(search_query),
				db.Round.map_name.like(search_query)
			)
		)
	
	rounds_query = rounds_query.order_by(db.Round.id.desc())

	page_count = math.ceil(rounds_query.count() / cfg.get("items_per_page")) # Selecting only the id on a count is faster than selecting the entire row

	displayed_rounds = rounds_query.limit(cfg.get("items_per_page")).offset((page - 1) * cfg.get("items_per_page"))

	return render_template("rounds/rounds.html", rounds=displayed_rounds, page=page, page_count=page_count, search_query=search_query)

@blueprint.route("/rounds/<int:round_id>/logs")
@login_required
@perms_required("round.logs")
def page_round_logs(round_id):
	round = db.Round.from_id(round_id)

	if not round:
		return abort(404)

	return render_template("rounds/log_viewer/log_viewer.html", round=round)

@blueprint.route("/rounds/<int:round_id>/replay")
def page_round_replay(round_id):
	round = db.Round.from_id(round_id)

	if not round:
		return abort(404)
	
	if round.in_progress():
		if not g.current_user.has_perms("round.logs"):
			return abort(401) # The round is ongoing and the user doesn't have access to live round logs, unauthorized
	
	logs = RoundLogs(round_id)

	demo_file = logs.find_demo_file()

	if not demo_file: # There is no replay for this one
		abort(404)

	return Response(
		stream_with_context(yield_file_chunks(demo_file)),
		mimetype='text/plain'
	)

@blueprint.route("/api/rounds/<int:round_id>/logs")
@perms_required("round.logs")
def page_round_logs_api(round_id):
	logs = RoundLogs(round_id)
	entries = logs.load_entries()

	return jsonify([entry.to_dict() for entry in entries])