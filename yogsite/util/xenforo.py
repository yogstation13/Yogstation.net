import requests

from cachetools import cached
from cachetools import TTLCache

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

class XenforoGroup():
	name: str
	group_id: int
	priority: int

	def __init__(self, name=None, group_id=None, priority=None):
		self.name = name
		self.group_id = group_id
		self.priority = priority

class XenforoUser():
	groups: list
	ckey: str

	def __init__(self, ckey=None, groups=None):
		self.ckey = ckey
		self.groups = groups
	
	def has_group(self, group_id):
		for group in self.groups:
			if group.group_id == group_id:
				return True
		
		return False
	
	def get_highest_group(self):
		if not len(self.groups):
			return None
		
		return sorted(self.groups, key=lambda g: g.priority, reverse=True)[0]

def get_xenforo_groups():
	url = f"{cfg.get('xenforo.apiurl')}/groups"

	request = requests.get(url,
		headers = XENFORO_HEADERS
	)

	assert request.status_code == 200, f"Get xenforo /groups returned {request.status_code}"

	groups = []

	for group_dict in request.json()["groups"]:
		groups.append(XenforoGroup(name=group_dict["title"], group_id=group_dict["user_group_id"], priority=group_dict["display_priority"]))
	
	return groups

def get_xenforo_users_from_groups(group_ids):
	if not isinstance(group_ids, list):
		group_ids = [group_ids]
	
	if len(group_ids) == 0: return []
	
	url = f"{cfg.get('xenforo.apiurl')}/group/users?groups={','.join([str(g) for g in group_ids])}"

	request = requests.get(url,
		headers = XENFORO_HEADERS
	)

	assert request.status_code == 200, f"Get xenforo /group/users returned {request.status_code}"

	xenforo_users = {}

	print(request.json())

	for group_dict in request.json()["groups"]:
		group = XenforoGroup(name=group_dict["name"], group_id=int(group_dict["user_group_id"]), priority=group_dict["priority"])

		for byondname in group_dict["users"]:
			ckey = byondname_to_ckey(byondname)

			if ckey in xenforo_users:
				xenforo_users[ckey].groups.append(group)
			else:
				xenforo_users[ckey] = XenforoUser(ckey=ckey, groups=[group])

	return xenforo_users.values()

@cached(cache=TTLCache(ttl=36000, maxsize=1)) # 10 hour cache because screw doing a ton of http requests a ton of times
def get_frontpage_staff():
	frontpage_staff = get_xenforo_users_from_groups([cfg.get("xenforo.group_ids.host"), cfg.get("xenforo.group_ids.council"), cfg.get("xenforo.group_ids.headcoder")])

	sorted_frontpage_staff = {}

	sorted_frontpage_staff["host"] = [user.ckey for user in frontpage_staff if user.has_group(cfg.get("xenforo.group_ids.host"))]
	sorted_frontpage_staff["council"] = [user.ckey for user in frontpage_staff if user.has_group(cfg.get("xenforo.group_ids.council"))]
	sorted_frontpage_staff["headcoder"] = [user.ckey for user in frontpage_staff if user.has_group(cfg.get("xenforo.group_ids.headcoder"))]

	return sorted_frontpage_staff