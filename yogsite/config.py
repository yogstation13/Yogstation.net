from yogsite.util import Struct

import yaml

with open("config.yml") as config_file:
	config_dict = yaml.full_load(config_file)

cfg = Struct(config_dict)