from flask_wtf import FlaskForm

from wtforms import HiddenField, SelectField, TextAreaField, TextField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import AnyOf, DataRequired, InputRequired, IPAddress, Length, Optional

from yogsite.config import cfg
from yogsite.util import validator_is_ckey

class SetLOAForm(FlaskForm):
	reason = TextAreaField("Reason", [InputRequired(), Length(max=2048)])

	expiration_time = DateTimeLocalField("Expiration Time", [InputRequired()], format="%Y-%m-%dT%H:%M")