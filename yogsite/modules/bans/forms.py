from flask_wtf import FlaskForm

from wtforms import SelectMultipleField, TextAreaField, StringField, DateTimeLocalField
from wtforms.validators import AnyOf, DataRequired, InputRequired, IPAddress, Length, Optional

from yogsite.config import cfg
from yogsite.util import validator_is_ckey, MultiCheckboxField

class BanEditForm(FlaskForm):
	ckey = StringField("CKEY", [InputRequired(), validator_is_ckey])

	reason = TextAreaField("Reason", [Optional(), Length(max=2048)])

	expiration_time = DateTimeLocalField("Expiration Time", [Optional()], format="%Y-%m-%dT%H:%M")

	roles = MultiCheckboxField("Role", [], choices=list(zip(cfg.get("roles"), cfg.get("roles"))))

	ip = StringField("IP", [Optional(), IPAddress()])

	computerid = StringField("CID", [Optional()])
