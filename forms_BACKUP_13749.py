from flask_wtf import *
import wtforms
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
import pymongo
from pymongo import MongoClient
=======
>>>>>>> f480652f8731a3936dbbfce266946627126d8fb4
=======
>>>>>>> f480652f8731a3936dbbfce266946627126d8fb4
=======
>>>>>>> f480652f8731a3936dbbfce266946627126d8fb4
from wtforms import SelectMultipleField,SubmitField,MultipleFileField
import investpy
client = pymongo.MongoClient("mongodb+srv://apoorv:apoorv@cluster0.xzygt.mongodb.net/investpy?retryWrites=true&w=majority")
class dropdown(FlaskForm):
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
	cursor = client.investpy.list.find().distinct('tickerlist')

	lst=[document['tickerlist'].split('.')[0] for document in cursor]
=======
	lst=sorted(list(set(investpy.get_stocks(country="India").symbol)))
>>>>>>> f480652f8731a3936dbbfce266946627126d8fb4
=======
	lst=sorted(list(set(investpy.get_stocks(country="India").symbol)))
>>>>>>> f480652f8731a3936dbbfce266946627126d8fb4
=======
	lst=sorted(list(set(investpy.get_stocks(country="India").symbol)))
>>>>>>> f480652f8731a3936dbbfce266946627126d8fb4
	ticker=wtforms.SelectMultipleField(label='Ticker',choices=[i for i in lst])
	#search=wtforms.StringField('')
	submit=SubmitField("Submit")
	upload=MultipleFileField(render_kw={'multiple': True})
