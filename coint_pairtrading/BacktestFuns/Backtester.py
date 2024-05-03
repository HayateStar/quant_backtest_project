import numpy as np
import pandas as pd
import statsmodels.api as sm
from other_funs import *
# from backtest_funs import *
from multiprocessing import Pool
import multiprocessing
from entryExitPointer import *
from returnCalculator import *
from importData import *


class CoinBacktester :

    def __init__(self, cointPairsData, rollingZSProbData , riskReward = 1/3, entryExitOption = "Dynamic", entryPercentile = 0.01, p = 0.1, initialMargin = 150):
        
        # Input Data 
        self.cointPairsData = cointPairsData
        self.rollingZSProbData = rollingZSProbData

        # Pair Trading Parameters
        self.riskReward = riskReward

        # Choose Entry/Exit Pointer
        self.entryExitOption = entryExitOption

        # Set Initial Margin
        self.initialMargin = initialMargin

        # Probability Search Threshold 
        self.entryPercentile = entryPercentile
        self.p = p

        # Result Record Dataframe
        self.returnRecordEachMonth = pd.DataFrame()
        self.numberOfTradeEachMonth = pd.DataFrame()

        self.returnRecord = pd.DataFrame()
        self.numberOfTrade = pd.DataFrame()

        self.positionRecord = pd.DataFrame()

    
    def getParams(self, cointPairsData, index) :
        
        token1 = cointPairsData.iloc[index]['token1']
        token2 = cointPairsData.iloc[index]['token2']
        
        token1Close_Colname = token1 + '_close'
        token2Close_Colname = token2 + '_close'

        selectPairCond = (cointPairsData['token1'] == token1) & (cointPairsData['token2'] == token2) 
        
        alpha = cointPairsData[selectPairCond]['alpha'].values
        beta = cointPairsData[selectPairCond]['beta'].values
        mu = cointPairsData[selectPairCond]['mu'].values
        sigma = cointPairsData[selectPairCond]['sigma'].values

        self.token1 = token1
        self.token2 = token2

        self.token1Close_Colname = token1Close_Colname
        self.token2Close_Colname = token2Close_Colname

        self.alpha = alpha
        self.beta = beta
        self.mu = mu
        self.sigma = sigma


    def cleanParams(self) :
        
        self.token1 = None
        self.token2 = None

        self.token1Close_Colname = None
        self.token2Close_Colname = None

        self.alpha = None
        self.beta = None
        self.mu = None
        self.sigma = None

    def pairTradingBacktest(self, pairsPriceData, backtestStartDate) : 

        # Get Entry & Exit Points
        #pairsPriceData = pairsPriceData[pairsPriceData['datetime']>= pd.Timestamp(2024,4,24,8,0)]

        entryExitPointer = getEntryExitPointer(self.entryExitOption)
        getEntryExitPoint = entryExitPointer(pairsPriceData = pairsPriceData, 
                                             beta = self.beta, 
                                             riskReward = self.riskReward, 
                                             entryPercentile = self.entryPercentile, 
                                            )

        getEntryExitPoint.main()
        pairsPriceData_withEntryExitPts = getEntryExitPoint.getPositionRecord()

        getWeightedReturn = returnCalculator(
                                            extryExitPtData = pairsPriceData_withEntryExitPts, 
                                            token1 = self.token1, 
                                            token2 = self.token2, 
                                            beta = self.beta,
                                            initialMargin = self.initialMargin,
                                        )

        getWeightedReturn.main()
        numberOfTrade_EachPair = getWeightedReturn.getNumberofTrade_EachPair()
        returnRecord_EachPair = getWeightedReturn.getReturnRecord_EachPair()
        
        numberOfTrade_EachPair = numberOfTrade_EachPair.assign(trading_date = backtestStartDate)
        returnRecord_EachPair = returnRecord_EachPair.assign(trading_date = backtestStartDate)

        # 查看 Position Holding 紀錄
        pairsPriceData_withEntryExitPts = pairsPriceData_withEntryExitPts.assign(trading_date = backtestStartDate)
        pairsPriceData_withEntryExitPts = pairsPriceData_withEntryExitPts.assign(token1 = self.token1)
        pairsPriceData_withEntryExitPts = pairsPriceData_withEntryExitPts.assign(token2 = self.token2)

        self.positionRecord = pd.concat([self.positionRecord, pairsPriceData_withEntryExitPts], ignore_index = True)

        return numberOfTrade_EachPair, returnRecord_EachPair

    
    def mergeTradeAndReturnRecord(self, numberOfTrade_EachPair, returnRecord_EachPair) :
        
        self.numberOfTradeEachMonth = pd.concat([self.numberOfTradeEachMonth, numberOfTrade_EachPair], ignore_index = True)
        self.returnRecordEachMonth = pd.concat([self.returnRecordEachMonth, returnRecord_EachPair], ignore_index = True)


    def coinBacktesting(self, backtestStartDate) :

        cointPairsData = self.cointPairsData.copy()
        cointPairsData = cointPairsData[cointPairsData['trading_date'] == backtestStartDate]
        cointPairsData = cointPairsData.reset_index(drop = True)

        if len(self.cointPairsData) > 0 :
            
            for index in range(0, len(cointPairsData)):
                
                # 拿出參數
                self.getParams(cointPairsData, index)

                rollingZSProbData_pair = self.rollingZSProbData[backtestStartDate][(self.token1, self.token2)]
                rollingZSProbData_pair = convertToDatetime(rollingZSProbData_pair, ['trading_date', 'datetime'])
                
                rollingZSProbData_pair = rollingZSProbData_pair.assign(takeProfitCurrent = rollingZSProbData_pair['takeProfitCurrent_' + str(self.p)])
                rollingZSProbData_pair = rollingZSProbData_pair.assign(stopLossCurrent = rollingZSProbData_pair['stopLossCurrent_' + str(self.p)])

                # 個別幣種 Pair Trading 回測
                numberOfTrade_EachPair, returnRecord_EachPair = self.pairTradingBacktest(rollingZSProbData_pair,backtestStartDate)

                self.mergeTradeAndReturnRecord(numberOfTrade_EachPair = numberOfTrade_EachPair , returnRecord_EachPair = returnRecord_EachPair)
                self.cleanParams()
                    

    def getReturnRecord_EachMonth(self) :

        return self.returnRecordEachMonth

    def getNumberofTrade_EachMonth(self) :

        return self.numberOfTradeEachMonth

    def main(self) : 

        uniqueTradingDates = self.cointPairsData['trading_date'].unique()
        backtestStartDateList = uniqueTradingDates[uniqueTradingDates.argsort()]

        for backtestStartDate in backtestStartDateList : 
            
            #if backtestStartDate >= pd.Timestamp(2022,2,1) : 
            print("Now Backtesting : ", backtestStartDate)
            
            self.coinBacktesting(backtestStartDate)
            returnRecordEachMonth = self.getReturnRecord_EachMonth()
            numberOfTradeEachMonth= self.getNumberofTrade_EachMonth()

            self.returnRecord = pd.concat([self.returnRecord, returnRecordEachMonth], ignore_index = True)
            self.numberOfTrade = pd.concat([self.numberOfTrade, numberOfTradeEachMonth], ignore_index = True)

            self.returnRecordEachMonth = None
            self.numberOfTradeEachMonth = None
        
    def getAllReturnRecord(self) :

        return self.returnRecord

    
    def getAllNumberOfTrades(self) :

        return self.numberOfTrade

    def getAllPositionRecord(self) : 
        
        return self.positionRecord
            
