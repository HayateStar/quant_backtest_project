import sys
sys.path.insert(0, '/home/ivan/projects/TradFi_Projects/coint_pairtrading/Backtesting/backtester')

from importData import *
from other_funs import *
import pandas as pd
import numpy as np
from tqdm import *
from datetime import *

def getTakeProfitPt(pairsFutureProfitLossData, rollingDays = 30 , futureRollingLen = 24*3, p = 0.5):

    # 計算 Top p% 獲利 & Top (1-p) 損失
    profitRollingObj = pairsFutureProfitLossData.rolling(rollingDays*24, min_periods = int(rollingDays*24/2))['futureMaxProfit']
    lossRollingObj = pairsFutureProfitLossData.rolling(rollingDays*24, min_periods = int(rollingDays*24/2))['futureMaxLoss']

    pairsFutureProfitLossData['takeProfitExp_' + str(p) ] = profitRollingObj.apply(lambda x: sorted(x,reverse=True)[int(rollingDays*24*p)])
    pairsFutureProfitLossData['stopLossExp_' + str(p)] = lossRollingObj.apply(lambda x: sorted(x,reverse=True)[int(rollingDays*24*(1-p))])

    # 避免看到未來資料
    pairsFutureProfitLossData['takeProfitCurrent_' + str(p)] = pairsFutureProfitLossData['takeProfitExp_' + str(p)].shift(futureRollingLen)
    pairsFutureProfitLossData['stopLossCurrent_' + str(p)] = pairsFutureProfitLossData['stopLossExp_' + str(p)].shift(futureRollingLen)

    return pairsFutureProfitLossData
    

# def getOptimaProfitLossPt(pairInOutDataDict, futureRollingLen = 24*3, pList = [0.2, 0.3, 0.4, 0.5]) : 

#     optimalPLDict= {}

#     for backtestStartDate, priceDict in tqdm(pairInOutDataDict.items()) :

#         optimalPLDict[backtestStartDate] = {}

#         for pairKey, pairPriceData in priceDict.items() :   

#             # Fitting Stop Loss / Take Profit ZS for Each p
#             for p in pList : 
#                 pairsFutureProfitData = getTakeProfitPt(pairPriceData, rollingDays = 30 , futureRollingLen = futureRollingLen, p = p)

#             # 篩選出交易期間
#             pairsFutureProfitData = pairsFutureProfitData[pairsFutureProfitData['datetime'] >= backtestStartDate].reset_index(drop = True)

#             # Save the data into nested dictionary
#             optimalPLDict[backtestStartDate][pairKey] = pairsFutureProfitData

#     return optimalPLDict
