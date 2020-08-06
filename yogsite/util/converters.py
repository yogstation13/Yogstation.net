def byondname_to_ckey(byond_name):
	byond_name = byond_name.lower()
	byond_name = byond_name.replace(" ", "")
	byond_name = byond_name.replace("_", "")
	return byond_name