from flask_wtf import FlaskForm

from wtforms import SelectField
from wtforms import TextAreaField
from wtforms import TextField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import AnyOf, DataRequired, InputRequired, IPAddress, Length, Optional


from yogsite.config import cfg
from yogsite.util import validator_is_ckey

class BanEditForm(FlaskForm):
	ckey = TextField("CKEY", [InputRequired(), validator_is_ckey])

	reason = TextAreaField("Reason", [Optional(), Length(max=2048)])

	expiration_time = DateTimeLocalField("Expiration Time", [Optional()], format="%Y-%m-%dT%H:%M")

	role = SelectField("Role", [AnyOf(cfg.get("roles"))], choices=list(zip(cfg.get("roles"), cfg.get("roles"))))

	ip = TextField("IP", [Optional(), IPAddress()])

	computerid = TextField("CID", [Optional()])
