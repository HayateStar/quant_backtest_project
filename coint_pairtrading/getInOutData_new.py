import sys

from importData import *
from other_funs import *
import pandas as pd
import numpy as np
from tqdm import *
from datetime import *
from inOutFuns.inOutPreprocess import *
from inOutFuns.inOutPtEstimate import *
import time
import pickle
from multiprocessing import Pool
import multiprocessing
from functools import partial


def importDataFun(rank) : 

    # Import Price & Pairs Data
    # fileDirPath = '/home/ivan/projects/TradFi_Projects/coint_pairtrading/Backtesting/'
    fileDirPath = "/home/ivan/projects/TradFi_Projects/coint_pairtrading/Final Code/Data/"

    priceDf = importCSV(fileDirPath + 'pricePerpDf_60_6M_top' + str(i) + '.csv')
    cointPairsData = importCSV(fileDirPath + 'cointPairsData_Top' + str(i) + '.csv')
    # priceDf = importCSV(fileDirPath + 'KBar/pricePerpDf_60_6M_top90_202404.csv')
    # cointPairsData = importCSV(fileDirPath + 'cointPairs/cointPairsData_Top60_90_202404.csv')

    priceDf = convertToDatetime(priceDf, ['trading_date', 'datetime'])
    cointPairsData = convertToDatetime(cointPairsData, ['trading_date'])

    return priceDf, cointPairsData

def getZS(priceDf, cointPairsData, rank = 30) : 
    
    pairZSdict = calculateCointPairZS(cointPairsData, priceDf)
    fileDirPath = "/home/ivan/projects/TradFi_Projects/coint_pairtrading/Final Code/Data/inOutPoints/"
    pairZSdictFileName = fileDirPath + 'pairZSdict_Top' + str(rank) + '.pkl'

    with open(pairZSdictFileName, "wb") as outfile: 
        pickle.dump(pairZSdict, outfile)

    return pairZSdict


def preProcessFun(item: tuple, backtestStartDate):
    tokenKey, zsInput = item
    
    # 計算未來三天內最大 ZS ＆ 最小 ZS，以推斷未來期望最大利益 & 損失。
    zsInput = getFutureMaxMinSpread(zsInput, futureRollingLen = 3*24)
    zsInput = getFutureMaxProfitLoss(zsInput)
    
    ## 計算 spreadDemean 過去 30 天的百分位數數值
    zsInput['entryPercentile'] = zsInput['spreadDemean'].rolling(30*24).apply(lambda x : getPercentile(x, lenThreshold = 30*24/4))
    
    pList = [0.2,0.3,0.4,0.5]
    for p in pList : 
        zsInput = getTakeProfitPt(zsInput, rollingDays = 30 , futureRollingLen = 24*3, p = p)
    
    zsInput = zsInput[zsInput['datetime'] >= backtestStartDate].reset_index(drop = True)

    return (tokenKey, zsInput)

def main():

    rankList = [90]

    priceDf, cointPairsData = importDataFun(rank = 90)
    pairZSdict = getZS(priceDf, cointPairsData, rank = 90)

    for iRank in rankList : 
        
        print("Now Processing : Top " + str(iRank))

        fileDirPath = "/home/ivan/projects/TradFi_Projects/coint_pairtrading/Final Code/Data/inOutPoints/"
        zsPklFileName = fileDirPath + 'pairZSdict_Top' + str(iRank)  + '.pkl'
        pairZSdict = pickle.load(open(zsPklFileName, "rb"))
        pairInOutDataDict = {}

        for dateKey, pairZSdictEachMonth in tqdm(pairZSdict.items()):
            
            pairInOutDataDict[dateKey] = {}

            #if dateKey == pd.Timestamp(2021,1,1) : 

            cpus = multiprocessing.cpu_count()
            print(f"Start with {cpus} cpus")

            _preProcessFun = partial(preProcessFun,
                                     backtestStartDate = dateKey,
                                    )

            with Pool(processes=6) as pool:
                pairInOutData = list(tqdm(pool.imap(_preProcessFun, pairZSdictEachMonth.items())))

            final_dict = dict()
            final_dict.update(pairInOutData)

        
            pairInOutDataDict[dateKey] = final_dict


        fileDirPath = "/home/ivan/projects/TradFi_Projects/coint_pairtrading/Final Code/Data/inOutPoints/"
        pairInOutDataDictFileName = fileDirPath + 'pairInOutDataDict' + '_Top' + str(iRank) + '.pkl'

        with open(pairInOutDataDictFileName, "wb") as outfile: 
            pickle.dump(pairInOutDataDict, outfile)


if __name__ == "__main__":
    
    main()

