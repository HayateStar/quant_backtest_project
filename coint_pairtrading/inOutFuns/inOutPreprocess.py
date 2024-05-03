import sys
sys.path.insert(0, '/home/ivan/projects/TradFi_Projects/coint_pairtrading/Backtesting/backtester')

from importData import *
from other_funs import *
import pandas as pd
import numpy as np
from tqdm import *
from datetime import *
# from maxProfit_funs import *
# from maxProfit_Calculate import *

# 資料合併 & 篩選
def mergePriceSeries(priceDf, date, token1, token2) :

    cols = ['trading_date', 'datetime' , 'close']

    priceToken1 = priceDf[(priceDf['trading_date'] == date) & (priceDf['token'] == token1)]
    priceToken2 = priceDf[(priceDf['trading_date'] == date) & (priceDf['token'] == token2)]

    priceToken1 = priceToken1[cols]
    priceToken2 = priceToken2[cols]

    priceToken1 = priceToken1.rename(columns = {'close' : 'token1_close'})
    priceToken2 = priceToken2.rename(columns = {'close' : 'token2_close'})

    priceTokens = priceToken1.merge(priceToken2 , on = ['datetime', 'trading_date'])
    
    priceTokens = priceTokens.assign(token1 = token1)
    priceTokens = priceTokens.assign(token2 = token2)

    return priceTokens


def getTimeintervalSubset(df, startTime, endTime) : 

    startCond = (df['datetime'] >= pd.Timestamp(startTime))
    endCond = (df['datetime'] <= pd.Timestamp(endTime))

    dfSubset = df[(startCond) & (endCond)]

    return dfSubset

# 計算 Rolling Z-Score 

def calculateRollingZS(pairsPriceData, beta):
    # Get the value of spread (error)
    error = pairsPriceData['token2_close'] - (pairsPriceData['token1_close'] * beta)
    pairsPriceData = pairsPriceData.assign(error = error)
    
    # Calculate rolling 1-Month Mean/Std of the spread
    errorRollingObj = pairsPriceData['error'].rolling(30*24)
    rollingMu = errorRollingObj.mean()
    rollingSigma = errorRollingObj.std() 
    pairsPriceData = pairsPriceData.assign(rolling_mu = rollingMu, 
                                           rolling_sigma = rollingSigma)
                                           
    # Calculate rolling ZS of the spread
    rollingZS = (pairsPriceData['error'] - pairsPriceData['rolling_mu'])/pairsPriceData['rolling_sigma']
    pairsPriceZSData = pairsPriceData.assign(rollingZS = rollingZS)

    return pairsPriceZSData


def getFutureMaxMinSpread(pairsPriceData, futureRollingLen = 24*3) : 
        
        pairsPriceData['spreadDemean'] =  pairsPriceData['error'] - pairsPriceData['rolling_mu']
        pairsReverseRollingObj = pairsPriceData.sort_index(ascending = False).rolling(futureRollingLen, min_periods= int(futureRollingLen/2))['spreadDemean']
                
        futureMinSpread = pairsReverseRollingObj.min().sort_index(ascending = True).shift(-1)
        futureMaxSpread = pairsReverseRollingObj.max().sort_index(ascending = True).shift(-1)
        
        pairsFutureProfitData = pairsPriceData.assign(
                                                 futureMinSpread = futureMinSpread, 
                                                 futureMaxSpread = futureMaxSpread, 
                                                 )
        return pairsFutureProfitData


def getFutureMaxProfitLoss(pairsFutureProfitData) : 
    
    # 計算未來最大收益 
    futureMaxProfit = np.where(np.isnan(pairsFutureProfitData['spreadDemean']), np.nan, 
                              
                               np.where(pairsFutureProfitData['spreadDemean'] > 0 , 
                                        np.where(pairsFutureProfitData['spreadDemean']*pairsFutureProfitData['futureMinSpread'] < 0, 
                                        pairsFutureProfitData['spreadDemean'], 
                                        pairsFutureProfitData['spreadDemean'] - pairsFutureProfitData['futureMinSpread']),

                                        np.where(pairsFutureProfitData['spreadDemean']*pairsFutureProfitData['futureMaxSpread'] < 0, 
                                        abs(pairsFutureProfitData['spreadDemean']), 
                                        pairsFutureProfitData['futureMaxSpread'] - pairsFutureProfitData['spreadDemean'])
                                
                                ) 
                                )
    

    # 計算未來最大損失
    futureMaxLoss = np.where(np.isnan(pairsFutureProfitData['spreadDemean']), np.nan, 
                                np.where(pairsFutureProfitData['spreadDemean'] > 0 , 
                                         np.where(pairsFutureProfitData['futureMaxSpread'] - pairsFutureProfitData['spreadDemean'] > 0 ,
                                                  pairsFutureProfitData['futureMaxSpread'] - pairsFutureProfitData['spreadDemean'], 
                                                  0) ,
                                                    
                                         np.where(pairsFutureProfitData['spreadDemean'] - pairsFutureProfitData['futureMinSpread'] > 0, 
                                                  pairsFutureProfitData['spreadDemean'] - pairsFutureProfitData['futureMinSpread'], 
                                                  0),
                                ) 
                                )
    
    pairsFutureProfitData = pairsFutureProfitData.assign(futureMaxProfit = futureMaxProfit)
    pairsFutureProfitData = pairsFutureProfitData.assign(futureMaxLoss = futureMaxLoss)

    return pairsFutureProfitData



def getPercentile(x, lenThreshold = 30*24/4) : 
    
    if len(x) >= lenThreshold : 
        rank = x.rank() - 1
        percentile = rank/(len(rank)-1)
        percentile = np.where( percentile < 0.5 , percentile , 1 - percentile)
        return percentile[-1]
            
    else : 
        return np.nan

    

def calculateCointPairZS(cointPairsData, priceDf) : 

    #pairZSData_all = pd.DataFrame()
    pairZSData_dict = {}

    backtestStartDateKeys = cointPairsData['trading_date'].unique() 

    for backtestStartDate in backtestStartDateKeys : 
        pairZSData_dict[backtestStartDate] = {}


    for index, row in tqdm(cointPairsData.iterrows()):

        # Get parameters of the pair
        token1 = row['token1']
        token2 = row['token2']
        beta = row['beta']
        backtestStartDate = row['trading_date']

        backtestEndDate = backtestStartDate + pd.DateOffset(months = 1) - pd.DateOffset(days = 1)
        rollingStartDate = backtestStartDate - pd.DateOffset(months = 6)

        # Get price data of the pair
        pairsPriceData = mergePriceSeries(priceDf, backtestStartDate, token1 , token2)
        pairsPriceData = getTimeintervalSubset(pairsPriceData, rollingStartDate, backtestEndDate)
        pairsZSData = calculateRollingZS(pairsPriceData, beta)
        pairZSData_dict[backtestStartDate][(token1, token2)] = pairsZSData

        #pairZSData_all = pd.concat([pairZSData_all, pairsZSData], ignore_index= True)

    #return pairZSData_all
    return pairZSData_dict



def inOutPreProcessMain(pairPricedict, futureRollingLen = 3*24, entryPtRollingLen = 30*24):

    pairZSDatawithInOut = pd.DataFrame()
    
    for backtestStartDate, priceDict in tqdm(pairPricedict.items()) :

        for pairKey, pairPriceData in priceDict.items() : 
            
            # Convert to Datetime
            pairPriceData = convertToDatetime(pairPriceData, ['trading_date', 'datetime'])

            # 計算未來三天內最大 ZS ＆ 最小 ZS，以推斷未來期望最大利益 & 損失。
            pairsDatawithMinMax = getFutureMaxMinSpread(pairPriceData, futureRollingLen = futureRollingLen)
            pairsDatawithMaProfitLoss = getFutureMaxProfitLoss(pairsDatawithMinMax)

            # 計算入場點百分位數
            entryPercentile = pairsDatawithMaProfitLoss['spreadDemean'].rolling(entryPtRollingLen).apply(lambda x : getPercentile(x, lenThreshold = entryPtRollingLen/4))
            pairsDatawithPLEntry = pairsDatawithMaProfitLoss.assign(entryPercentile = entryPercentile)

            # Put the dataframe back to dictionary
            priceDict[pairKey] = pairsDatawithPLEntry

    return pairPricedict
