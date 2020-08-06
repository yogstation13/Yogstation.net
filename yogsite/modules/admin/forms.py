from flask_wtf import FlaskForm

from wtforms import HiddenField
from wtforms import SelectField
from wtforms import TextAreaField
from wtforms import TextField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import AnyOf, DataRequired, InputRequired, IPAddress, Length, Optional


from yogsite.config import cfg
from yogsite.util import validator_is_ckey

class SetLOAForm(FlaskForm):
	ckey = TextField("CKEY", [InputRequired(), validator_is_ckey])

	reason = TextAreaField("Reason", [InputRequired(), Length(max=2048)])

	expiration_time = DateTimeLocalField("Expiration Time", [InputRequired()], format="%Y-%m-%dT%H:%M")