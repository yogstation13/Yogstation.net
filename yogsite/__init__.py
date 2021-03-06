from datetime import datetime

from flask import Flask
from flask import g
from flask import session
from flask import send_from_directory

from yogsite.config import cfg
from yogsite import util
import yogsite.db

from yogsite.extensions import flask_db_ext

from yogsite.modules.login import User

import os
import time
import uuid

def register_extensions(app):
	flask_db_ext.init_app(app)

def create_app():
	app = Flask(__name__)

	app.url_map.strict_slashes = False

	app.secret_key = cfg.get("secret_key") # Used for signing sessions

	app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://{username}:{password}@{host}:{port}/{db}".format(
		username	= cfg.get("db.game.user"),
		password	= cfg.get("db.game.pass"),
		host		= cfg.get("db.game.host"),
		port		= cfg.get("db.game.port"),
		db			= cfg.get("db.game.name")
	)

	register_extensions(app)

	return app

app = create_app()

@app.before_request
def before_request():
	request_start_time = time.time()
	g.request_duration = lambda: (time.time() - request_start_time)

	g.current_user = User.from_session(session)

@app.route("/ses")
def debug_ses():
	return str(dict(session))+" "+str(g.current_user.__dict__)

@app.context_processor
def context_processor():
	return dict(datetime=datetime, cfg=cfg, db=db, util=util)

from yogsite.modules.admin import blueprint as bp_admin
from yogsite.modules.api import blueprint as bp_api
from yogsite.modules.bans import blueprint as bp_bans
from yogsite.modules.directory import blueprint as bp_directory
from yogsite.modules.donate import blueprint as bp_donate
from yogsite.modules.library import blueprint as bp_library
from yogsite.modules.login import blueprint as bp_login
from yogsite.modules.home import blueprint as bp_home
from yogsite.modules.rounds import blueprint as bp_rounds

app.register_blueprint(bp_admin)
app.register_blueprint(bp_api)
app.register_blueprint(bp_bans)
app.register_blueprint(bp_directory)
app.register_blueprint(bp_donate)
app.register_blueprint(bp_home)
app.register_blueprint(bp_library)
app.register_blueprint(bp_login)
app.register_blueprint(bp_rounds)