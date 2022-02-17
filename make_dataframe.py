import investpy
import pandas as pd
import pymongo
from pymongo import MongoClient
client = pymongo.MongoClient("mongodb+srv://apoorv:apoorv@cluster0.xzygt.mongodb.net/investpy?retryWrites=true&w=majority")
def make_dataframe(stocks):
	df2=pd.DataFrame()
	for i in stocks:
		cursor = client.investpy.stocks.find({"ticker":i+".csv"})
		lst=[document['historical'] for document in cursor]
		df=pd.DataFrame.from_dict(lst[0])
		df['Date'] = pd.to_datetime(df['Date'])
		df.reset_index(inplace=True)
		df=df[['Date','Close']]
		df[i]=df.Close
		df.drop(columns=['Close'],inplace=True)
		if not 'Date' in df2:
			df2['Date']=pd.to_datetime(df.Date)
		df2=df2.merge(df,on='Date',how='outer')
	df2.set_index('Date',inplace=True)
	return df2
	#print(df2.head())