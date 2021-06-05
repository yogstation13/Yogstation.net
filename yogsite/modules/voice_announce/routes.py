from flask import Blueprint, Response, request, render_template
from werkzeug.utils import secure_filename
from io import open
from os import path, stat, remove
from yogsite.extensions import flask_csrf_ext
from yogsite.config import cfg
from yogsite.util import topic_query
from subprocess import run,DEVNULL
from datetime import datetime, timedelta, timezone
import json

blueprint = Blueprint("voice_announce", __name__)

type_extensions = {
	"audio/aac": ".aac",
	"audio/mpeg": ".mp3",
	"audio/ogg": ".ogg",
	"audio/opus": ".opus",
	"audio/wav": ".wav",
	"audio/webm": ".weba"
}

@blueprint.route("/voice_announce/<string:id>")
def page_voice_announce(id):
	id = secure_filename(id)
	dir = cfg.get('voice_announce.directory')
	if not path.exists(path.join(dir, id + ".json")):
		return Response("Invalid voice announcement URL", status=404)
	with open(path.join(dir, id + ".json")) as f:
		data = json.load(f)
	created_date = datetime.fromisoformat(data["created"])
	print(created_date)
	time_since_created = datetime.utcnow().replace(tzinfo=timezone.utc) - created_date
	if time_since_created > timedelta(seconds = 15):
		return Response("Voice announcement URL expired", status=404)

	return render_template("voice_announce/voice_announce.html", enable_robot_voice = data["is_ai"])

@blueprint.route("/voice_announce/<string:id>/upload", methods=["POST"])
@flask_csrf_ext.exempt
def voice_announce_upload(id):
	id = secure_filename(id)
	dir = cfg.get('voice_announce.directory')
	if not path.exists(path.join(dir, id + ".json")):
		return Response("Invalid voice announcement upload URL", status=404)
	with open(path.join(dir, id + ".json")) as f:
		data = json.load(f)
	created_date = datetime.fromisoformat(data["created"])
	print(created_date)
	time_since_created = datetime.utcnow().replace(tzinfo=timezone.utc) - created_date
	if time_since_created > timedelta(minutes = 5):
		remove(path.join(dir, id + ".json"))
		return Response("Voice announcement URL expired", status=404)
	if request.content_length > 120000:
		return Response("File too large", status=400)
	ct = request.content_type
	semicolon_loc = ct.find(";")
	if semicolon_loc != -1:
		ct = ct[:semicolon_loc]
	if type_extensions[ct] == None:
		return Response("Invalid file type", status=400)
	filename_base = id
	filename = filename_base + "_base" + type_extensions[ct]
	ogg_filename = filename_base + "_converted.ogg"

	#if path.exists(path.join(dir, ogg_filename)):
	#	return Response("URL already used", status=400)

	with open(path.join(dir,filename), "wb") as file:
		file.write(request.get_data())

	result = run(["ffmpeg", "-i", path.join(dir,filename), "-c:a", "libvorbis", "-y", path.join(dir,ogg_filename)], stdin=DEVNULL,stdout=DEVNULL,stderr=DEVNULL)
	if result.returncode != 0:
		remove(path.join(dir, filename))
		return Response("Conversion failed", status=500)
	probe_result = run(["ffprobe", "-i", path.join(dir, ogg_filename), "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"], capture_output=True)
	if probe_result.returncode != 0:
		remove(path.join(dir, filename))
		remove(path.join(dir, ogg_filename))
		return Response("ffprobe failed: " + probe_result.stderr.decode("utf-8"), status=500)
	duration = float(probe_result.stdout)
	if duration > 35:
		remove(path.join(dir, filename))
		remove(path.join(dir, ogg_filename))
		return Response("Duration too long!", status=400)
	
	for s in cfg.get("servers").values():
		if s["sqlname"]:
			server = s

	topic_query(server, "", args = {
		"voice_announce": id,
		"voice_announce_token": data["topic_token"],
		"ogg_file": ogg_filename,
		"uploaded_file": filename,
		"ip": request.remote_addr,
		"duration": duration
	})

	remove(path.join(dir, id + ".json"))

	return Response(None, status=204)

@blueprint.route("/voice_announce/<string:id>/cancel", methods=["GET","POST"])
@flask_csrf_ext.exempt
def voice_announce_cancel(id):
	id = secure_filename(id)
	dir = cfg.get('voice_announce.directory')
	if not path.exists(path.join(dir, id + ".json")):
		return Response("Invalid voice announcement upload URL", status=404)

	remove(path.join(dir, id + ".json"))

	return Response(None, status=204)
