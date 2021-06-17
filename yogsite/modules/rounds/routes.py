from os import path
from flask import abort, Blueprint, g, jsonify, render_template, request, Response, send_file

import math

from sqlalchemy import or_
from werkzeug.utils import secure_filename

from yogsite.config import cfg
from yogsite import db
from yogsite.util import login_required, perms_required

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

@blueprint.route("/rounds/<int:round_id>/sounds")
def page_round_sounds(round_id):
	round = db.Round.from_id(round_id)

	if not round:
		return Response("Round does not exist", status=404)

	if round.in_progress() and not g.current_user.has_perms("round.logs"):
		return Response("Round in progress, unauthorized", status=401)

	logs = RoundLogs(round_id)

	return render_template("rounds/log_viewer/sounds.html", round=round, sounds=logs.get_sounds())

public_extensions = [
	".aac",
	".mp3",
	".ogg",
	".opus",
	".wav",
	".weba"
]

@blueprint.route("/rounds/<int:round_id>/logs/<string:filename>")
def page_round_log_file(round_id, filename):
	filename = secure_filename(filename)

	round = db.Round.from_id(round_id)

	if not round:
		return Response("Round does not exist", status=404)

	if round.in_progress() and not g.current_user.has_perms("round.logs"):
		return Response("Round in progress, unauthorized", status=401)
	
	extension = path.splitext(filename)[1]
	
	if not (extension in public_extensions) and not g.current_user.has_perms("round.logs"):
		return Response("Access to this file is unauthorized", status=401)

	logs = RoundLogs(round_id)
	file = logs.find_log_file(filename)
	if not file:
		return Response("File not found", status=404)
	
	response = send_file(file,
		cache_timeout=-1 # Don't cache the file by default
	)

	return response

@blueprint.route("/rounds/<int:round_id>/replay")
def page_round_replay(round_id):
	headers = {}

	origin = request.environ.get("HTTP_ORIGIN")
	if origin == cfg.get("replay_viewer.origin"):
		headers["Access-Control-Allow-Credentials"] = "true"
	headers["Access-Control-Expose-Headers"] = "X-Allow-SS13-Replay-Streaming"
	headers["Access-Control-Allow-Origin"] = origin if origin else "*"

	round = db.Round.from_id(round_id)

	if not round:
		return Response("Round does not exist", status=404, headers=headers)

	if round.in_progress() and not g.current_user.has_perms("round.logs"):
		return Response("Round in progress, unauthorized", status=401, headers=headers)

	logs = RoundLogs(round_id)
	demo_file = logs.find_demo_file()

	if not demo_file: # There is no replay for this one
		return Response("No replay file found", status=404, headers=headers)

	response = send_file(demo_file,
		conditional=True, # Allow the file to be streamed with ranges
		cache_timeout=-1 # Don't cache the file by default
	)
	
	response.headers.update(headers)

	if demo_file.endswith(".gz"):
		response.headers.add("Content-Encoding", "gzip")
	else:
		response.headers.add("X-Allow-SS13-Replay-Streaming", "true")
	
	if not round.in_progress():
		response.headers.add("Cache-Control", f"public,max-age={cfg.get('replay_viewer.max_cache_age')},immutable")
	else:
		response.headers.remove("Cache-Control")

	return response


@blueprint.route("/api/rounds/<int:round_id>/logs")
@perms_required("round.logs")
def page_round_logs_api(round_id):
	logs = RoundLogs(round_id)
	entries = logs.load_entries()

	db.ActionLog.add(g.current_user.ckey, g.current_user.ckey, f"Looked at logs for round {round_id}")

	return jsonify([entry.to_dict() for entry in entries])