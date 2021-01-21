import requests

from yogsite.config import cfg
from yogsite.config import XENFORO_HEADERS

from .converters import byondname_to_ckey

def validate_xenforo_credentials(username, password): # AHHH I HATE THIS THIS IS SO INSECUREEE
	url = f"{cfg.get('xenforo.apiurl')}/auth"

	request = requests.post(url,
		data = {"login": username, "password": password},
		headers = XENFORO_HEADERS
	)

	return request

def get_xenforo_groups():
	url = f"{cfg.get('xenforo.apiurl')}/groups"

	request = requests.get(url,
		headers = XENFORO_HEADERS
	)

	assert request.status_code == 200, f"Get xenforo /groups returned {request.status_code}"

	return request.json()["groups"]

def get_xenforo_ckeys_from_groups(groups):
	if not isinstance(groups, list):
		groups = [groups]
	
	if len(groups) == 0: return []
	
	url = f"{cfg.get('xenforo.apiurl')}/group/users?groups={','.join([str(g) for g in groups])}"

	request = requests.get(url,
		headers = XENFORO_HEADERS
	)

	assert request.status_code == 200, f"Get xenforo /group/users returned {request.status_code}"

	return [byondname_to_ckey(bk) for bk in request.json()["users"]]