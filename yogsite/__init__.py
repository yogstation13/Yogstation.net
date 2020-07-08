from datetime import datetime

from flask import Flask
from flask import session
from flask import send_from_directory

from yogsite.config import cfg
from yogsite import util
import yogsite.db


app = Flask(__name__)

app.url_map.strict_slashes = False

app.secret_key = cfg.secret_key # Used for signing sessions

@app.context_processor
def context_processor():
	return dict(datetime=datetime, cfg=cfg, db=db, util=util, session=session)

from yogsite.modules.bans import blueprint as bp_bans
from yogsite.modules.library import blueprint as bp_library
from yogsite.modules.donate import blueprint as bp_donate
from yogsite.modules.home import blueprint as bp_home
from yogsite.modules.rounds import blueprint as bp_rounds

app.register_blueprint(bp_bans)
app.register_blueprint(bp_donate)
app.register_blueprint(bp_home)
app.register_blueprint(bp_library)
app.register_blueprint(bp_rounds)