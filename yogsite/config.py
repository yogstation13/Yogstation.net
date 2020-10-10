from envyaml import EnvYAML

cfg = EnvYAML("config.yml")

XENFORO_HEADERS = {"XF-Api-Key": cfg.get("xenforo_key")}