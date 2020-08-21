from flask_wtf import FlaskForm

from wtforms import SelectField
from wtforms import TextAreaField
from wtforms import TextField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import AnyOf, DataRequired, InputRequired, IPAddress, Length, Optional


from yogsite.config import cfg
from yogsite.util import validator_is_ckey

class BookEditForm(FlaskForm):
	title = TextField("Title", [InputRequired(), Length(max=45)])

	author = TextField("Author", [InputRequired(), Length(max=45)])

	content = TextAreaField("Content", [Optional(), Length(max=16777215)])

	category = SelectField("Category", [AnyOf(cfg.get("library.categories"))], choices=list(zip(cfg.get("library.categories"), cfg.get("library.categories"))))