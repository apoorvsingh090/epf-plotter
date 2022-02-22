from flask import Flask,render_template,request,flash,redirect
from forms import dropdown
import pandas as pd
import numpy as np
import investpy
import os
from make_dataframe import make_dataframe
from pypf import epf

app=Flask(__name__)
app.config['SECRET_KEY'] = '5ecc8f8cfc9b7281c14faab192f57ca9'

@app.route("/",methods = ['GET','POST'])
def hello():
	submit = dropdown(request.form)
	if request.method == "POST":
		return submit_results(submit)
	return render_template('about.html',title = 'EPF',form = submit)

@app.route("/reference")
def reference():
	x = investpy.get_stocks(country = "India")[['name','full_name','isin','symbol']]
	return render_template('dropdown.html',data = x.to_html())

@app.route('/results')
def submit_results(submit):
	if len(request.files.getlist('upload')) > 0 and not submit.data['ticker']:
		df2 = pd.DataFrame()
		lst = request.files.getlist('upload')
		for i in range(len(lst)):
			#print(i)
			lst[i].save(str(request.files.to_dict(flat = False)['upload'][i]).split("'")[1])
			data = pd.read_csv(str(request.files.to_dict(flat = False)['upload'][i]).split("'")[1],parse_dates=['Date'])
			data[str(request.files.to_dict(flat = False)['upload'][i]).split("'")[1]]=data.Close
			data = data[[str(request.files.to_dict(flat = False)['upload'][i]).split("'")[1],'Date']]
			if not 'Date' in df2:
				df2['Date'] = pd.to_datetime(data.Date)
			df2=df2.merge(data,on='Date',how='outer')
		df2.set_index('Date',inplace=True)
		data,ef_perf,cla_perf=epf(df2)
		return render_template('results.html',data=data,ef_perf=ef_perf,cla_perf=cla_perf)
	elif str(request.files.to_dict(flat=False)['upload'][0]).split("'")[1] and  submit.data['ticker']:
		df=make_dataframe(submit.data['ticker'])
		lst=request.files.getlist('upload')
		for i in range(len(lst)):
			lst[i].save(str(request.files.to_dict(flat=False)['upload'][i]).split("'")[1])
			data=pd.read_csv(str(request.files.to_dict(flat=False)['upload'][i]).split("'")[1],parse_dates=['Date'])
			data[str(request.files.to_dict(flat=False)['upload'][i]).split("'")[1]]=data.Close
			data=data[[str(request.files.to_dict(flat=False)['upload'][i]).split("'")[1],'Date']]
			df=df.merge(data,on='Date',how='outer')
		df.set_index('Date',inplace=True)
		data,epf_perf,cla_perf = epf(df)
		return render_template('results.html',data=data,ef_perf=epf_perf,cla_perf=cla_perf)
	else:
		df=make_dataframe(submit.data['ticker'])
		data,epf_perf,cla_perf=epf(df)
		return render_template('results.html',data=data,ef_perf=epf_perf,cla_perf=cla_perf)
if __name__=='__main__':
	app.run(debug=True)
