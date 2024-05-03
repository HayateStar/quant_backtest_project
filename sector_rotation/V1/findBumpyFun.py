import ta
from datetime import datetime
import pandas as pd 
import numpy as np

def addATRColumn(priceData) : 

    priceData['atr'] = ta.volatility.AverageTrueRange(
        priceData.high,
        priceData.low,
        priceData.close,
        window=6,
        fillna=False
    ).average_true_range() # <- call function

    return priceData

def getMA(priceData, maLen) :
    return priceData['close'].rolling(maLen).mean()

def getMAAbsDiff(priceData, maLen) :

    return abs((priceData['close'] - priceData['close'].rolling(maLen).mean())/priceData['close'])

def getVolMA(priceData, maLen) :
    return priceData['volume'].rolling(maLen).mean()


def getOIFRCond(priceData, oiData, frData): 
    
    # 計算接下來 N 根 K 棒的平均 OI 
    oiData['past_mean_oi'] = oiData['close'].rolling(60).mean()
    oiData['future_mean_oi'] = oiData['close'].sort_index(ascending=False).rolling(6).mean().sort_index()

    #計算接下來 N 根 K 棒的平均 FR 
    frData['past_mean_fr'] = frData['close'].rolling(60).mean()
    frData['future_mean_fr'] = frData['close'].sort_index(ascending=False).rolling(6).mean().sort_index()

    priceDatawithOI = priceData.merge(oiData[['datetime', 'past_mean_oi', 'future_mean_oi']], 
                                                        left_on = ['open_time'], 
                                                        right_on = ['datetime'])
    
    
    priceDatawithFROI = priceDatawithOI.merge(frData[['datetime', 'past_mean_fr', 'future_mean_fr']], 
                                                        left_on = ['open_time'], 
                                                        right_on = ['datetime'])
                                                        
    return priceDatawithFROI

def getBumpyCond(priceData):

    # 計算快慢線
    priceData['quick_ma'] = getMA(priceData, 5*6)
    priceData['slow_ma'] = getMA(priceData, 10*6)

    priceData['quick_ma_pct'] = getMAAbsDiff(priceData, 5*6)
    priceData['slow_ma_pct'] = getMAAbsDiff(priceData, 10*6)

    priceData['vol_ma'] = getVolMA(priceData, 30*6)

    # 計算接下來 N 根 K 棒的報酬率
    priceData['future_close'] = priceData['close'].shift(-6)
    priceData['future_return'] = (priceData['future_close'] - priceData['close'])/priceData['close']

    # 計算接下來 N 根 K 棒的平均交易量
    priceData['past_mean_vol'] = priceData['volume'].rolling(6).mean()
    priceData['future_mean_vol'] = priceData['volume'].sort_index(ascending=False).rolling(6).mean().sort_index()
    

    #盤整量縮條件
    bumpyIntervalData = priceData[(priceData['quick_ma_pct'] < 0.1) & (priceData['slow_ma_pct'] < 0.1) & (priceData['volume'] < priceData['vol_ma']*1.5)].copy()
    
    bumpyIntervalData['index'] = bumpyIntervalData.index
    bumpyIntervalData['index_diff'] = bumpyIntervalData['index'].diff()

    return bumpyIntervalData



def bumpyBacktesting(priceData, bumpyIntervalData, token, isFROIFilter = True , returnLen = 5*6*4) : 
        
    bumpyTradeRecordAll = pd.DataFrame()
    startIndex = 0
    endIndex = 0

    for i in range(1, len(bumpyIntervalData)) :

        past_row = bumpyIntervalData.iloc[i-1]
        current_row = bumpyIntervalData.iloc[i]
        
        indexDiff = current_row['index_diff']
        isNonContinuousBumpy = (indexDiff > 1)
        
        if isNonContinuousBumpy :
            
            endIndex = i-1
            
            futureReturn = bumpyIntervalData['future_return'].iloc[endIndex]
            pastMeanVol = bumpyIntervalData['past_mean_vol'].iloc[endIndex]
            futureMeanVol = bumpyIntervalData['future_mean_vol'].iloc[endIndex]            

            if (endIndex - startIndex >= 6) :                

                if isFROIFilter : 

                    pastMeanOI = bumpyIntervalData['past_mean_oi'].iloc[endIndex]
                    futureMeanOI = bumpyIntervalData['future_mean_oi'].iloc[endIndex]

                    pastMeanFR = bumpyIntervalData['past_mean_fr'].iloc[endIndex]
                    futureMeanFR = bumpyIntervalData['future_mean_fr'].iloc[endIndex]

                    derivativeCond = (futureMeanOI > pastMeanOI*1.1) | (futureMeanFR > pastMeanFR*1.1)
                
                else : 
                    derivativeCond = True
                
                if (futureReturn > 0.5/100) & (futureMeanVol > pastMeanVol*1.1) & (derivativeCond):
                    
                    startDate = bumpyIntervalData['open_time'].iloc[startIndex]
                    endDate = bumpyIntervalData['open_time'].iloc[endIndex]

                    backtestStartTime = endDate  + pd.DateOffset(hours = 4*6)
                    backtestStartPrice = priceData[(priceData['open_time'] == backtestStartTime)]['close'].values[0]

                    afterSignalHours = 4
                    bumpyPrices = priceData[(priceData['open_time'] >= startDate) & (priceData['open_time'] <= endDate)]
                    bumpyMinPrice = bumpyPrices['close'].max()

                    while afterSignalHours <= returnLen :
                        
                        tradingEndDate = endDate + pd.DateOffset(hours = afterSignalHours) + pd.DateOffset(hours = 4*6)
                        
                        if tradingEndDate <= priceData['open_time'].max() :
                            
                            try : 
                                backtestEndPrice = priceData[priceData['open_time'] == tradingEndDate]['close'].values[0]
                                futureReturn = (backtestEndPrice - backtestStartPrice)/backtestStartPrice

                                # if futureReturn <= -0.1 :
                                #     break

                            except : 
                                pass

                        else : 
                            break
                        
                        if (backtestEndPrice <= bumpyMinPrice) :#| (futureReturn <= -0.05) :
                            # if futureReturn <= -0.3 : 
                            #     print(token, futureReturn, backtestStartTime, tradingEndDate)
                            
                            break

                        # if futureReturn <= -0.1 :
                        #     break

                        
                        afterSignalHours = afterSignalHours + 4



                    bumpyTradeRecord = { 
                                         'bumpyStartDate' : [startDate],
                                         'bumpyEndDate' : [endDate],
                                         'tradingStartDate' : [backtestStartTime],
                                         'tradingEndDate' : [tradingEndDate],
                                         'token' : [token],
                                         'futureReturn' : [futureReturn]

                                        }

                    bumpyTradeRecord = pd.DataFrame(bumpyTradeRecord)
                    bumpyTradeRecordAll = pd.concat([bumpyTradeRecordAll, bumpyTradeRecord], ignore_index=True)

            startIndex = i
            endIndex = 0


    return bumpyTradeRecordAll


def oiFRBacktesting(priceDatawithFROI, token, returnLen = 5*6*4) : 

    oiFRTradeRecordAll = pd.DataFrame()

    for i in range(0, len(priceDatawithFROI)) :

        pastMeanOI = priceDatawithFROI['past_mean_oi'].iloc[i]
        futureMeanOI = priceDatawithFROI['future_mean_oi'].iloc[i]

        pastMeanFR = priceDatawithFROI['past_mean_fr'].iloc[i]
        futureMeanFR = priceDatawithFROI['future_mean_fr'].iloc[i]

        
        derivativeCond = (futureMeanOI > pastMeanOI*1.1) | (futureMeanFR > pastMeanFR*1.1)
            
            
        if derivativeCond :
            
            startDate = priceDatawithFROI['open_time'].iloc[i]
            endDate = priceDatawithFROI['open_time'].iloc[i]
            
            backtestStartTime = endDate  + pd.DateOffset(hours = 4*6)

            if backtestStartTime < priceDatawithFROI['open_time'].max() :

                backtestStartPrice = priceDatawithFROI[priceDatawithFROI['open_time'] == backtestStartTime]['close'].values[0]
                
                afterSignalHours = 4

                while afterSignalHours <= returnLen :

                    tradingEndDate = endDate + pd.DateOffset(hours = afterSignalHours) + pd.DateOffset(hours = 4*6)

                    if tradingEndDate <= priceDatawithFROI['open_time'].max() :
                        
                        try : 
                            backtestEndPrice = priceDatawithFROI[priceDatawithFROI['open_time'] == tradingEndDate]['close'].values[0]
                            futureReturn = (backtestEndPrice - backtestStartPrice)/backtestStartPrice
                        
                        except:
                            pass
                    
                    else : 
                        break

                    if futureReturn <= -0.1 :
                        break
                    
                    afterSignalHours = afterSignalHours + 4



            oiFRTradeRecord = { 
                                'startDate' : [startDate],
                                'endDate' : [endDate],
                                'token' : [token],
                                'futureReturn' : [futureReturn]

                               }

            oiFRTradeRecord = pd.DataFrame(oiFRTradeRecord)
            oiFRTradeRecordAll = pd.concat([oiFRTradeRecordAll, oiFRTradeRecord], ignore_index=True)

    return oiFRTradeRecordAll