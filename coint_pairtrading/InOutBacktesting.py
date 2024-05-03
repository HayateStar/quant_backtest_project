### Import Packages
import pandas as pd
import numpy as np
from datetime import datetime
import datetime
from tqdm import tqdm, trange
from importData import *
import time
import pickle

import sys
sys.path.insert(0, '/home/ivan/projects/TradFi_Projects/coint_pairtrading/Final Code/BacktestFuns')
from Backtester import *

rankList = [90]

for i in rankList : 

    ### Import Price & Conintegration Data
    fileDirPath = '/home/ivan/projects/TradFi_Projects/coint_pairtrading/Final Code/Data/'    
    priceDf = importCSV(fileDirPath + 'KBar/pricePerpDf_60_6M_top' + str(i) + '.csv')
    cointPairsData = importCSV(fileDirPath + 'cointPairs/cointPairsData_Top' + str(i) + '.csv')

    priceDf = convertToDatetime(priceDf, ['trading_date', 'datetime'])
    cointPairsData = convertToDatetime(cointPairsData, ['trading_date'])

    # Test Condition 
    # dateCond = (cointPairsData['trading_date'] == pd.Timestamp(2022,2,1))
    # tokenCond = (cointPairsData['token1'] == 'LTC') & (cointPairsData['token2'] == 'NEO')
    # cointPairsData = cointPairsData[dateCond & tokenCond]

    ### 進出場方式
    entryExitDict = {
       
        'EntryPoint_MaxProfit' : 'EntryPoint_MaxProfit',
        #'EntryPoint_MaxLoss' : 'EntryPoint_MaxLoss',

    }

    ### 讀取進出場點資料
    pairsFutureProfitLossDict = pickle.load(open(fileDirPath + "inOutPoints/pairsProfitLossThresholdDict_Top90.pkl", "rb"))
    #pairsFutureProfitLossDict = pickle.load(open(fileDirPath + "inOutPoints/pairInOutDataDict_Top90_202404.pkl", "rb"))

    ### Pair Trading 回測
    for entryExitKey, entryExitname in entryExitDict.items() : 
        
        # 指定策略參數
        ps = [0.3]
        entryPercentileList = [0.01]
        initialMarginList = [150]

        for p in ps : 

            for entryPercentile in entryPercentileList :   

                for initialMargin in initialMarginList :      

                    print("Now Backtesting : ", entryExitname, " p = ", str(p), " entryThreshold = ", str(entryPercentile), " Top " + str(i))

                    T1 = time.time()

                    backtester = CoinBacktester(
                            
                            cointPairsData = cointPairsData, 
                            rollingZSProbData = pairsFutureProfitLossDict, 

                            riskReward = 1/3,
                            entryExitOption = entryExitname,
                            entryPercentile = entryPercentile,
                            p = p, 
                            initialMargin = initialMargin,

                        )
                    
                    backtester.main()
                    returnRecord_df = backtester.getAllReturnRecord()
                    #numberOfTrade_df = backtester.getAllNumberOfTrades()
                    #positionRecord_df = backtester.getAllPositionRecord()
                    
                    T2 = time.time()
                    print('Backtesting Running Time :%s second' % ((T2 - T1)))

                    ## 儲存回測成果
                    outputDirPath = "/home/ivan/projects/TradFi_Projects/coint_pairtrading/Final Code/BacktestingResult/"
                    typeOfExp = entryExitname + '_Hourly'  + entryExitKey + str(entryPercentile) + "_p_" + str(p) + '_top_' + str(i) + '_minQty' + '_' + str(initialMargin)
                    returnRecord_df.to_csv(outputDirPath + 'returnRecord_' + typeOfExp + '.csv')
                    #numberOfTrade_df.to_csv(outputDirPath + 'numberOfTrade_' + typeOfExp + '.csv')
                    #positionRecord_df.to_csv(outputDirPath + 'positionRecord_' + typeOfExp + '.csv')