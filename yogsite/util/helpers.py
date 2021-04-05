from yogsite.config import cfg

def get_primary_server():
	for server in cfg.get("servers").values():
		if server["primary"]:
			return server
	
	return None

def get_server(server_id):
	return cfg.get("servers").get(server_id)