from flask import Blueprint, Response, request, render_template
from werkzeug.utils import secure_filename
from io import open
from os import path, remove
from yogsite.extensions import flask_csrf_ext
from yogsite.config import cfg
from yogsite.util import topic_query
from subprocess import run,DEVNULL

blueprint = Blueprint("voice_announce", __name__)

type_extensions = {
	"audio/aac": ".aac",
	"audio/mpeg": ".mp3",
	"audio/ogg": ".ogg",
	"audio/opus": ".opus",
	"audio/wav": ".wav",
	"audio/webm": ".weba"
}

@blueprint.route("/voice_announce/<string:serversqlname>/<string:id>")
def page_voice_announce(serversqlname, id):
	#Test pages
	if serversqlname == "test" and id == "test":
		return render_template("voice_announce/voice_announce.html", enable_robot_voice = 0)
	if serversqlname == "test" and id == "test_ai":
		return render_template("voice_announce/voice_announce.html", enable_robot_voice = 1)
	
	server = None
	for s in cfg.get("servers").values():
		if s["sqlname"] == serversqlname:
			server = s
	if (not server):
		return Response("Server doesn't exist", status=404)
	res = topic_query(server, "", args = {
		"voice_announce_query": id,
		"key": server["comms_key"]
	})
	if (not res) or (not int(res["exists"])):
		return Response("Invalid voice announcement URL", status=404)
	
	return render_template("voice_announce/voice_announce.html", enable_robot_voice = int(res["is_ai"]))

@blueprint.route("/voice_announce/<string:serversqlname>/<string:id>/upload", methods=["POST"])
@flask_csrf_ext.exempt
def voice_announce_upload(serversqlname, id):
	server = None
	for s in cfg.get("servers").values():
		if s["sqlname"] == serversqlname:
			server = s
	if (not server):
		return Response("Server doesn't exist", status=404)
	id = secure_filename(id)
	dir = cfg.get('voice_announce.directory')
	res = topic_query(server, "", args = {
		"voice_announce_query": id,
		"key": server["comms_key"]
	})
	if (not res) or (not int(res["exists"])):
		return Response("Invalid voice announcement URL", status=404)
	
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
	
	topic_query(server, "", args = {
		"voice_announce": id,
		"ogg_file": ogg_filename,
		"uploaded_file": filename,
		"ip": request.remote_addr,
		"duration": duration,
		"key": server["comms_key"]
	})

	return Response(None, status=204)

@blueprint.route("/voice_announce/<string:serversqlname>/<string:id>/cancel", methods=["GET","POST"])
@flask_csrf_ext.exempt
def voice_announce_cancel(serversqlname, id):
	server = None
	for s in cfg.get("servers").values():
		if s["sqlname"] == serversqlname:
			server = s
	if (not server):
		return Response("Server doesn't exist", status=404)

	topic_query(server, "", args = {
		"voice_announce_cancel": id,
		"key": server["comms_key"]
	})

	return Response(None, status=204)
