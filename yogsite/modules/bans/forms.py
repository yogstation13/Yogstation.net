from flask_wtf import FlaskForm

from wtforms import SelectMultipleField
from wtforms import TextAreaField
from wtforms import TextField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import AnyOf, DataRequired, InputRequired, IPAddress, Length, Optional


from yogsite.config import cfg
from yogsite.util import validator_is_ckey, MultiCheckboxField

class BanEditForm(FlaskForm):
	ckey = TextField("CKEY", [InputRequired(), validator_is_ckey])

	reason = TextAreaField("Reason", [Optional(), Length(max=2048)])

	expiration_time = DateTimeLocalField("Expiration Time", [Optional()], format="%Y-%m-%dT%H:%M")

	roles = MultiCheckboxField("Role", [InputRequired()], choices=list(zip(cfg.get("roles"), cfg.get("roles"))))

	ip = TextField("IP", [IPAddress()])

	computerid = TextField("CID", [])
