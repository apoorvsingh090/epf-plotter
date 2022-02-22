from flask_wtf import *
import wtforms
import pymongo
from pymongo import MongoClient
from wtforms import SelectMultipleField,SubmitField,MultipleFileField
import investpy
client = pymongo.MongoClient("###")
class dropdown(FlaskForm):
	cursor = client.investpy.list.find().distinct('tickerlist')

	lst=[document['tickerlist'].split('.')[0] for document in cursor]
	ticker=wtforms.SelectMultipleField(label='Ticker',choices=[i for i in lst])
	#search=wtforms.StringField('')
	submit=SubmitField("Submit")
	upload=MultipleFileField(render_kw={'multiple': True})
