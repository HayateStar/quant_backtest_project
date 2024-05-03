from datetime import datetime
import pandas as pd 
import numpy as np
from importData import *
from coinGlassDataLoader import *
from froiDownload import *


def get_rank_data(year, month, day):

    req = requests.get(f'http://192.168.1.140:8001/coingecko/historical_100_coins?year={year}&month={month}&day={day}')
    return req.json()


startDate = pd.Timestamp(2020,1,1)
downloadStartDate = pd.Timestamp(2020,1,1)
tokensTop100 = {}

while startDate <=  pd.Timestamp(2024,4,1) : 
    
    marketCapDate = startDate - pd.DateOffset(days = 1)
    
    year = marketCapDate.year
    month = marketCapDate.month
    day = marketCapDate.day

    rankDict = get_rank_data(year,month,day)
    rankDf = pd.json_normalize(rankDict)

    tokensTop100[startDate] = rankDf['symbol'].array

    startDate = startDate + pd.DateOffset(months = 3)


futureDownloader = CoinGlassDataLoader(tokensTop100, downloadStartDate, freq = '4h')
futureDownloader.main()
futurePriceDict = futureDownloader.getPriceData()
np.save('futurePriceDict.npy', futurePriceDict)


df_FR, df_OI = froiDownloader(tokensDict)
np.save('df_FR.npy', df_FR)
np.save('df_OI.npy', df_OI)
