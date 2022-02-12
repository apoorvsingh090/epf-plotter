from flask_wtf import *
import wtforms
from wtforms import *
import investpy
class dropdown(FlaskForm):
	ticker=wtforms.SelectMultipleField(label='Ticker',choices=[i for i in investpy.get_stocks(country="India").symbol.sort_values()])
	#search=wtforms.StringField('')
	submit=SubmitField("Submit")
	upload=MultipleFileField()
