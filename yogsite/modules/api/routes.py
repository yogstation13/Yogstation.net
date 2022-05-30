from flask import abort, Blueprint, jsonify, redirect, request, session

import math

from yogsite.config import cfg
from yogsite import db
from yogsite.util import query_server_status

blueprint = Blueprint("api", __name__)
