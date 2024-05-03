from datetime import datetime
import pandas as pd 
import numpy as np
from importData import *    
import requests


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
    

def froiDownloader(tokensDict):


    df_OI = {}
    df_FR = {}

    for sector, symbols in tokensDict.items() : 

        df_OI[sector] = {}
        df_FR[sector] = {}

        for symbol in symbols : 
            #print("Now Downloading : " + symbol)
            
            try : 
                df_OI[sector][symbol] = getOIFundingRateData(ticker = symbol + "USDT", 
                                                            start_date = datetime(2020,1,1),
                                                            end_date = datetime(2024,12,31),
                                                            dataType = 'oi' )
            except : 

                print("No OI Data : " + symbol)
                pass
            
            try : 
            
                df_FR[sector][symbol] = getOIFundingRateData(ticker = symbol + "USDT", 
                                                            start_date = datetime(2020,1,1),
                                                            end_date = datetime(2024,12,31),
                                                            dataType = 'fr' )
            except : 

                print("No FR Data : " + symbol)
                pass

    return df_OI, df_FR
