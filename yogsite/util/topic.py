"""
This file is for stuff that will talk to the game servers via topic requests
"""
from yogsite.config import cfg

from cachetools import cached
from cachetools import TTLCache

import socket
import struct

import urllib.parse

def topic_query(server, query, args=None):
	"""
	For sending a topic query to a server

	args should be a dict if passed
	"""

	full_query = f"?{query}"

	if args:
		full_query = f"{full_query}&{urllib.parse.urlencode(args)}"
	
	packed_query = b"\x00\x83" + struct.pack('>H', len(full_query) + 6) + b"\x00\x00\x00\x00\x00" + full_query.encode() + b"\x00"
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.settimeout(3)
	sock.connect((server["host"], server["port"]))

	sock.sendall(packed_query)

	data = sock.recv(4096)

	parsed_data = urllib.parse.parse_qs(data[5:-1].decode())

	return {i:parsed_data[i][0] for i in parsed_data.keys()}


@cached(cache=TTLCache(ttl=10, maxsize=10))
def query_server_status(server_id):
	server = cfg.get("servers")[server_id]
	status = topic_query(server, "status")

	if not status:
		return status
	
	# Set everything to it's actual datatype because for some reason it's not
	# sent over in a form which gives us the ability to recognize it automatically
	
	# god I hate this
	status["respawn"]					= bool(status["respawn"])
	status["enter"]						= bool(status["enter"])
	status["vote"]						= bool(status["vote"])
	status["ai"]						= bool(status["ai"])
	status["round_id"]					= int(status["round_id"])
	status["players"]					= int(status["players"])
	status["admins"]					= int(status["admins"])
	status["gamestate"]					= int(status["gamestate"])
	status["round_duration"]			= int(status["round_duration"]) # seconds
	status["time_dilation_current"]		= float(status["time_dilation_current"])
	status["time_dilation_avg"]			= float(status["time_dilation_avg"])
	status["time_dilation_avg_slow"]	= float(status["time_dilation_avg_slow"])
	status["time_dilation_avg_fast"]	= float(status["time_dilation_avg_fast"])
	status["soft_popcap"]				= int(status["soft_popcap"])
	status["hard_popcap"]				= int(status["hard_popcap"])
	status["extreme_popcap"]			= int(status["extreme_popcap"])
	status["popcap"]					= int(status["popcap"])
	status["shuttle_timer"] 			= int(status["shuttle_timer"])

	return status


