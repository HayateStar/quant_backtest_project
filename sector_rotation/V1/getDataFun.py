from datetime import datetime
import pandas as pd 
import numpy as np
import requests


def get_future_data(symbol : str , start_ts, end_ts , exchange = 'binance', interval = '1d', dataType = 'oi'):
    req = requests.get(f'http://192.168.1.140:8002/coinglass/data?exchange={exchange}&interval={interval}&type={dataType}&symbol={symbol}&start={str(start_ts)}&end={str(end_ts)}')
    return req.json()


def getOIFundingRateData(ticker, start_date, end_date, dataType = 'oi') : 


    start_ts = datetime.timestamp(start_date)
    end_ts = datetime.timestamp(end_date)


    coinGlassDict = get_future_data(symbol = ticker, 
                                    interval = '4h', 
                                    start_ts = start_ts, 
                                    end_ts = end_ts , 
                                    dataType = dataType)
    
    dfBars =  pd.DataFrame(coinGlassDict['data'])
    dfBars.columns = coinGlassDict['columns'][0:len(dfBars.columns)]

    dfBars['datetime'] = pd.to_datetime(dfBars['timestamp'], unit='s')
    dfBars = dfBars.sort_values(by = 'datetime')

    return dfBars