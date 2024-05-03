import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller


def merge_series(price_df, date, x, y) :

    cols = ['trading_date', 'datetime' , 'close']

    df_x = price_df[(price_df['trading_date'] == date) & (price_df['token'] == x)]
    df_y = price_df[(price_df['trading_date'] == date) & (price_df['token'] == y)]

    df_x = df_x[cols]
    df_y = df_y[cols]

    df_x = df_x.rename(columns = {'close' : x + '_close'})
    df_y = df_y.rename(columns = {'close' : y + '_close'})


    # df_x = df_x[['datetime' , x + '_close' ]]
    # df_y = df_y[['datetime' , y + '_close' ]]

    df = df_x.merge(df_y , on = ['datetime', 'trading_date'])

    return df


def timeinterval_subset(df, start_time, end_time) : 

    start_cond = (df['datetime'] >= pd.Timestamp(start_time))
    end_cond = (df['datetime'] <= pd.Timestamp(end_time))

    df_subset = df[(start_cond) & (end_cond)]

    return df_subset


def coint_test(x,y):

    cointest = sm.tsa.stattools.coint(x,y)
    pvalue = cointest[1]

    return pvalue

def coint_alpha_beta(x, y): 

    X = sm.add_constant(x)
    result = (sm.OLS(y,X)).fit()

    alpha = result.params.values[0]
    beta = result.params.values[1]  
    error = y - (x*beta)

    r2 = result.rsquared_adj

    return alpha, beta, error, r2


def adf_test(x) :

    x = x.dropna()
    dftest = adfuller(x, autolag="AIC")
    pvalue = dftest[1]

    return pvalue
