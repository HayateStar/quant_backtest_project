from datetime import datetime
import pandas as pd 
import numpy as np
from tqdm import *
import plotly.express as px
import requests
from multiprocessing import Pool
import multiprocessing
from functools import partial

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from importData import *
from findBumpyFun import *
from getDataFun import *
from bumpyBacktestFun import *
from randomBeta import *


def getTokensDict():

    tokensAI = ["AGIX","AI","AR","ARKM","CTXC","FET","GRT","IQ","LPT","MDT","NEAR","NFP","OCEAN","PHA","PHB","RNDR","THETA","WLD"]
    tokensGameFi = ["ACE","APE","AXS","BEAMX","BURGER","CHR",
                    "COMBO","DAR","ENJ","FLOW","GALA","GHST","GMT",
                    "HIGH","ILV","IMX","MAGIC","MANA","MBOX","PDA",
                    "PIXEL","PORTAL","PYR","RONIN","SAND","SLP",
                    "SUPER","TLM","VOXEL","XAI","YGG"]

    tokensDict= {
        'AI' : tokensAI,
        'GameFi' : tokensGameFi,
    }

    return tokensDict
         
def importPriceData(): 
    # df_kbar = np.load('sectorKbar.npy',allow_pickle='TRUE').item()
    # df_kbar = np.load('top100Kbar.npy',allow_pickle='TRUE').item()
    priceDateDict = np.load('futurePriceDict.npy',allow_pickle='TRUE').item()
    priceDateDict1H = np.load('futurePriceDict.npy',allow_pickle='TRUE').item()

    return priceDateDict, priceDateDict1H


def importFROIData():

    df_OI = np.load('df_OI_top100.npy',allow_pickle='TRUE').item()
    df_FR = np.load('df_FR_top100.npy',allow_pickle='TRUE').item()
    
    return df_OI, df_FR

def _oiFRBacktestingFun(item: tuple, oiDataDict, frDataDict, date, holdDays):
        
    tokenKey, priceData = item
    
    oiTokens = oiDataDict.keys()
    frTokens = frDataDict.keys()

    if (tokenKey in oiTokens) & (tokenKey in frTokens) : 

        priceDatawithFROI = getOIFRCond(priceData, oiDataDict[tokenKey], frDataDict[tokenKey])
        priceDatawithFROI = priceDatawithFROI[priceDatawithFROI['open_time'] > date]
        oiFRTradeRecord = oiFRBacktesting(priceDatawithFROI, tokenKey, returnLen = holdDays*6*4)

        return oiFRTradeRecord

    else :
        return pd.DataFrame()

def oiFRBacktestingFun(priceDict, oiDataDict, frDataDict , date, holdDays):
    
    oiFRTradeRecordAll = pd.DataFrame()
    
    _func = partial(_oiFRBacktestingFun,
                    date = date,
                    holdDays = holdDays,
                    oiDataDict = oiDataDict,
                    frDataDict = frDataDict, 
                )


    with Pool(processes=6) as pool:
        oiFRTradeRecords = list(tqdm(pool.imap(_func, priceDict.items())))

    for i in range(0, len(oiFRTradeRecords)) : 
        oiFRTradeRecordAll = pd.concat([oiFRTradeRecordAll, oiFRTradeRecords[i]], ignore_index=True)

    return oiFRTradeRecordAll


def _bumpyOnlyBacktestingFun(item: tuple, date, holdDays):
        
    tokenKey, priceData = item

    bumpyIntervalData = getBumpyCond(priceData)
    bumpyIntervalData = bumpyIntervalData[bumpyIntervalData['open_time'] > date]
    bumpyTradeRecord = bumpyBacktesting(priceData = priceData, 
                                        bumpyIntervalData = bumpyIntervalData, 
                                        token = tokenKey, 
                                        returnLen = holdDays*6*4, 
                                        isFROIFilter = False)

    return bumpyTradeRecord


def bumpyOnlyBacktestingFun(priceDict , date, holdDays):
    
    bumpyTradeRecordAll = pd.DataFrame()
    
    _func = partial(_bumpyOnlyBacktestingFun,
                    date = date,
                    holdDays = holdDays,
                )


    with Pool(processes=6) as pool:
        bumpyTradeRecords = list(tqdm(pool.imap(_func, priceDict.items())))

    for i in range(0, len(bumpyTradeRecords)) : 
        bumpyTradeRecordAll = pd.concat([bumpyTradeRecordAll, bumpyTradeRecords[i]], ignore_index=True)

    return bumpyTradeRecordAll



def _bumpyOIFRBacktestingFun(item: tuple, oiDataDict, frDataDict, date, holdDays):
        
    tokenKey, priceData = item

    oiTokens = oiDataDict.keys()
    frTokens = frDataDict.keys()
    price1HTokens= priceDict1H.keys()

    if (tokenKey in oiTokens) & (tokenKey in frTokens) & (tokenKey in price1HTokens): 

        priceData1H = priceDict1H[tokenKey]
        bumpyIntervalData = getBumpyCond(priceData)

        bumpyOIFRData = getOIFRCond(bumpyIntervalData, oiDataDict[tokenKey], frDataDict[tokenKey])
        
        bumpyOIFRData = bumpyOIFRData[bumpyOIFRData['open_time'] > date]
        priceData1H = priceData1H[priceData1H['open_time'] > date]
        
        bumpyOIFRTradeRecord = bumpyBacktesting(priceData = priceData, 
                                                bumpyIntervalData = bumpyOIFRData, 
                                                token = tokenKey, 
                                                returnLen = holdDays*6*4, 
                                                isFROIFilter = True)
        
        return bumpyOIFRTradeRecord
    
    else :

        return pd.DataFrame()


def bumpyOIFRBacktestingFun(priceDict, oiDataDict, frDataDict, date, holdDays):
    
    bumpyOIFRTradeRecordAll = pd.DataFrame()
    
    _func = partial(_bumpyOIFRBacktestingFun,
                    oiDataDict = oiDataDict,
                    frDataDict = frDataDict,
                    date = date,
                    holdDays = holdDays,
                )


    with Pool(processes=6) as pool:
        bumpyOIFRTradeRecords = list(tqdm(pool.imap(_func, priceDict.items())))


    for i in range(0, len(bumpyOIFRTradeRecords)) : 

        bumpyOIFRTradeRecordAll = pd.concat([bumpyOIFRTradeRecordAll, bumpyOIFRTradeRecords[i]], ignore_index=True)

    return bumpyOIFRTradeRecordAll


def main(holdDays = 5):

    # Get Backtesting Result
    df_kbar, df_kbar1H = importPriceData()
    df_OI, df_FR = importFROIData()

    bumpyTradeRecordAll = pd.DataFrame()
    oiFRTradeRecordAll = pd.DataFrame()
    bumpyOIFRTradeRecordAll = pd.DataFrame()
    betaAll = pd.DataFrame()


    for date, priceDict in df_kbar.items() : 

        priceDataDict1H = df_kbar1H[date].copy()
        
        # 只有帶量突破
        bumpyTradeRecord = bumpyOnlyBacktestingFun(priceDict , date, holdDays)
        bumpyTradeRecordAll = pd.concat([bumpyTradeRecordAll, bumpyTradeRecord], ignore_index = True)

        # # 只有 OI / FR 濾網
        try : 
            oiDataDict = df_OI[date].copy()
            frDataDict = df_FR[date].copy()

            oiFRTradeRecord = oiFRBacktestingFun(priceDict, oiDataDict, frDataDict , date, holdDays)
            oiFRTradeRecordAll = pd.concat([oiFRTradeRecordAll, oiFRTradeRecord], ignore_index = True)
        
        except : 
            pass
        
        
        # 帶量突破 + OI/FR 濾網
        try : 

            oiDataDict = df_OI[date].copy()
            frDataDict = df_FR[date].copy()
        
            bumpyOIFRTradeRecord = bumpyOIFRBacktestingFun(priceDict, oiDataDict, frDataDict, date, holdDays)
            bumpyOIFRTradeRecordAll = pd.concat([bumpyOIFRTradeRecordAll, bumpyOIFRTradeRecord], ignore_index = True)

        except : 
            pass
      

        # 市場 Beta 模擬
        betaValue = randomBeta(priceDict , date, returnLen = holdDays*6*4)
        betaAll = pd.concat([betaAll, betaValue], ignore_index = True)

    
    bumpyTradeRecordAll.to_csv("bumpyTradeRecordAll_BumpyAddStaticStoploss.csv")
    bumpyOIFRTradeRecordAll.to_csv("bumpyOIFRTradeRecordAll_NewStoploss.csv")
    oiFRTradeRecordAll.to_csv("oiFRTradeRecordAll.csv")
    betaAll.to_csv("betaAll.csv")

if __name__ == "__main__":
    main(holdDays = 5)
