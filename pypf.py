import pandas as pd
from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import CLA,plotting
from pypfopt import expected_returns
import matplotlib.pyplot as plt
def epf(df):
	mu=expected_returns.mean_historical_return(df)
	s=risk_models.sample_cov(df)
	ef=EfficientFrontier(mu,s)
	raw_weights=ef.max_sharpe()
	cleaned_weights=ef.clean_weights()
	plt.figure()
	graph=pd.Series(raw_weights).plot.pie(figsize=(10,10))
	plt.savefig('./static/plt')
	k=ef.portfolio_performance(verbose=True)
	cla=CLA(mu,s)
	cla.max_sharpe()
	plt.figure()
	k2=cla.portfolio_performance(verbose=True)
	g2=plotting.plot_efficient_frontier(cla)
	plt.savefig('./static/plt2')
	return cleaned_weights,k,k2
