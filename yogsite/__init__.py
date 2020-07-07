from flask import Flask
from flask import send_from_directory

app = Flask(__name__)

app.url_map.strict_slashes = False


@app.route('/static/<path:path>')
def static_content(path):
    return send_from_directory('./static', path)

from yogsite.modules.donate import blueprint as bp_donate
from yogsite.modules.home import blueprint as bp_home

app.register_blueprint(bp_donate)
app.register_blueprint(bp_home)