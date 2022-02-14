from flask_wtf import *
import wtforms
from wtforms import SelectMultipleField,SubmitField,MultipleFileField
import investpy
class dropdown(FlaskForm):
	lst=sorted(list(set(investpy.get_stocks(country="India").symbol)))
	ticker=wtforms.SelectMultipleField(label='Ticker',choices=[i for i in lst])
	#search=wtforms.StringField('')
	submit=SubmitField("Submit")
	upload=MultipleFileField(render_kw={'multiple': True})
