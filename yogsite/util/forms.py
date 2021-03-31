from wtforms import SelectMultipleField, ValidationError, widgets

import re

from .converters import byondname_to_ckey

def validator_is_ckey(form, field):
	ckey = byondname_to_ckey(field.data)

	if not re.match(r"^[a-z0-9]{2,32}$", ckey):
		raise ValidationError('Invalid CKEY!')


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()