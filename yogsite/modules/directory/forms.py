from flask_wtf import FlaskForm

from wtforms import TextField
from wtforms.validators import Length

class NoteAddForm(FlaskForm):
	description = TextField("Description", [Length(min=1, max=2048)])