import pandas as pd
from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import CLA,plotting
from pypfopt import expected_returns
import matplotlib.pyplot as plt
def epf(df):
	mu=expected_returns.mean_historical_return(df)
	s=risk_models.CovarianceShrinkage(df).ledoit_wolf()
	#s=(s)
	ef=EfficientFrontier(mu,s)
	raw_weights=ef.max_sharpe()
	cleaned_weights=ef.clean_weights()
	plt.figure()
	graph=pd.Series(raw_weights).plot.pie(figsize=(5,5),autopct = lambda p:f'{p:.2f}%')
	plt.savefig('./static/plt',dpi=500)
	k=ef.portfolio_performance(verbose=True)
	cla=CLA(mu,s)
	cla.max_sharpe()
	plt.figure()
	k2=cla.portfolio_performance(verbose=True)
	g2=plotting.plot_efficient_frontier(cla,dpi=500,filename='./static/plt2')
	#plotting.plot_dendrogram(cla,filename='tmp')
	#plotting.plot_covariance(s,filename='./static/tmp',dpi=500)
	return cleaned_weights,k,k2
