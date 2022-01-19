from flask_wtf import FlaskForm

from wtforms import SelectField, StringField, BooleanField
from wtforms.validators import AnyOf, DataRequired, Length

class NoteAddForm(FlaskForm):
	text = StringField("Text", [DataRequired(), Length(min=1, max=2048)])

	note_types = ["note", "message", "message sent", "watchlist entry"]
	type = SelectField(
		"Type",
		choices=list(zip(
			note_types,
			[type.title() for type in note_types]
		)),
		validators=[DataRequired()]
	)

	secret = BooleanField("Secret")