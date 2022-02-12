import investpy
import pandas as pd
def make_dataframe(stocks):
	df2=pd.DataFrame()
	for i in stocks:
		df=investpy.get_stock_historical_data(stock=i,country='india',
			from_date='01/01/2016',to_date='01/01/2023')
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