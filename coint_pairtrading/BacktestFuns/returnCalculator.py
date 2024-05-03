import numpy as np
import pandas as pd
import statsmodels.api as sm
import math
from other_funs import *
from minQtyDict import *

class returnCalculator :

    def __init__(self,extryExitPtData, token1, token2, beta, initialMargin = 150):

        self.extryExitPtData = extryExitPtData
        # self.token1Close_Colname = token1Close_Colname
        # self.token2Close_Colname = token2Close_Colname
        
        self.token1 = token1
        self.token2 = token2
        self.initialMargin = initialMargin

        self.beta = beta

        self.returnRecord = pd.DataFrame()
        self.numberOfTradeRecord = pd.DataFrame()


    def transformQty(self, token, tokenQty):
        
        tokenUSDT = token + 'USDT'
        minQty = getMinQty(tokenUSDT)
        transformedQty = math.ceil(tokenQty/minQty) * minQty

        # if math.ceil(tokenQty/minQty) == 0 : 
        #     print(self.token1, self.token2)

        #print(transformedQty)
        #transformedQty = round(tokenQty/minQty) * minQty

        return transformedQty     

    def getEntryQty(self, index):
        
        longSpreadSignal= (self.extryExitPtData['position'].iloc[index] == 1) # Token2 - Beta*Token1
        shortSpreadSignal= (self.extryExitPtData['position'].iloc[index] == -1) # Beta*Token1 - Token1
        
        token2Value = self.initialMargin
        token2Qty = self.initialMargin/self.extryExitPtData['token2_close'].iloc[index]
        token1Qty = token2Qty*self.beta[0]

        token1TransQty = self.transformQty(self.token1, token1Qty)
        token2TransQty = self.transformQty(self.token2, token2Qty)

        self.token1TransQty = token1TransQty
        self.token2TransQty = token2TransQty

        return token1TransQty, token2TransQty

    def getLongShortPortfolio(self, index, token1TransQty, token2TransQty, isStartIndex = False) : 
        
        longSpreadSignal= (self.extryExitPtData['position'].iloc[index] == 1) # Token2 - Beta*Token1
        shortSpreadSignal= (self.extryExitPtData['position'].iloc[index] == -1) # Beta*Token1 - Token1

        token1Value = token1TransQty*self.extryExitPtData['token1_close'].iloc[index]
        token2Value = token2TransQty*self.extryExitPtData['token2_close'].iloc[index]


        longPositionToken1 = np.where(shortSpreadSignal , token1Value , 0).astype(float)
        shortPositionToken1 = np.where(longSpreadSignal , token1Value , 0).astype(float)

        longPositionToken2 = np.where(longSpreadSignal , token2Value , 0).astype(float)
        shortPositionToken2 = np.where(shortSpreadSignal , token2Value , 0).astype(float)


        # print(self.token1, self.token2, longPositionToken1, shortPositionToken1, longPositionToken2, shortPositionToken2, isStartIndex)
        # print(longPositionToken1, shortPositionToken1)
        # print(longPositionToken2, shortPositionToken2)

        if isStartIndex :

            self.longPositionToken1_Start = longPositionToken1
            self.shortPositionToken1_Start = shortPositionToken1
            
            self.longPositionToken2_Start = longPositionToken2
            self.shortPositionToken2_Start = shortPositionToken2


        else : 
            
            self.longPositionToken1_End = longPositionToken1
            self.shortPositionToken1_End = shortPositionToken1
            
            self.longPositionToken2_End = longPositionToken2
            self.shortPositionToken2_End = shortPositionToken2

    # def getLongShortPortfolio(self, index, isStartIndex = False) : 

    #     longSpreadSignal= (self.extryExitPtData['position'].iloc[index] == 1) # Token2 - Beta*Token1
    #     shortSpreadSignal= (self.extryExitPtData['position'].iloc[index] == -1) # Beta*Token1 - Token1

    #     # token1Value = self.beta*self.extryExitPtData[self.token1Close_Colname].iloc[index]
    #     # token2Value = self.extryExitPtData[self.token2Close_Colname].iloc[index]
        
    #     token1Value = self.beta*self.extryExitPtData['token1_close'].iloc[index]
    #     token2Value = self.extryExitPtData['token2_close'].iloc[index]

    #     longPositionToken1 = np.where(shortSpreadSignal , token1Value , 0).astype(float)
    #     shortPositionToken1 = np.where(longSpreadSignal , token1Value , 0).astype(float)

    #     longPositionToken2 = np.where(longSpreadSignal , token2Value , 0).astype(float)
    #     shortPositionToken2 = np.where(shortSpreadSignal , token2Value , 0).astype(float)

    #     # print(longPositionToken1, shortPositionToken1)
    #     # print(longPositionToken2, shortPositionToken2)

    #     if isStartIndex :

    #         self.longPositionToken1_Start = longPositionToken1
    #         self.shortPositionToken1_Start = shortPositionToken1
            
    #         self.longPositionToken2_Start = longPositionToken2
    #         self.shortPositionToken2_Start = shortPositionToken2


    #     else : 
            
    #         self.longPositionToken1_End = longPositionToken1
    #         self.shortPositionToken1_End = shortPositionToken1
            
    #         self.longPositionToken2_End = longPositionToken2
    #         self.shortPositionToken2_End = shortPositionToken2

        

    def calculateWeightedReturn(self) : 

        if self.longPositionToken1_Start > 0 :

            initalPortfolio = self.longPositionToken1_Start + self.shortPositionToken2_Start
            weight = self.longPositionToken1_Start/initalPortfolio

            token1Return = (self.longPositionToken1_End - self.longPositionToken1_Start)/self.longPositionToken1_Start
            token2Return = (self.shortPositionToken2_End - self.shortPositionToken2_Start)/ self.shortPositionToken2_Start

            # print(self.longPositionToken1_End, self.longPositionToken1_Start, self.longPositionToken1_Start)
            # print(self.shortPositionToken2_End, self.shortPositionToken2_Start, self.shortPositionToken2_Start)

            weightReturnLong = weight * token1Return
            weightReturnShort = -(1-weight) * token2Return

            self.token1WeightedReturn = weightReturnLong
            self.token2WeightedReturn = weightReturnShort

            

        else : 
            initalPortfolio = self.shortPositionToken1_Start + self.longPositionToken2_Start
            weight = self.shortPositionToken1_Start / initalPortfolio

            token1Return = (self.shortPositionToken1_End - self.shortPositionToken1_Start)/self.shortPositionToken1_Start
            token2Return = (self.longPositionToken2_End - self.longPositionToken2_Start)/self.longPositionToken2_Start

            # print(self.shortPositionToken1_End, self.shortPositionToken1_Start, self.shortPositionToken1_Start)
            # print(self.longPositionToken2_End, self.longPositionToken2_Start, self.longPositionToken2_Start)

            weightReturnLong = (1-weight) * token2Return
            weightReturnShort = (- weight) * token1Return

            self.token1WeightedReturn = weightReturnShort
            self.token2WeightedReturn = weightReturnLong
        
        weightReturn = weightReturnLong + weightReturnShort

        self.token1Return = token1Return
        self.token2Return = token2Return

        self.weightReturn = weightReturn
        self.weightReturnLong = weightReturnLong
        self.weightReturnShort = weightReturnShort

        #print(self.token1Return, self.token2Return, self.token1WeightedReturn, self.token2WeightedReturn)

    
    def openPosition(self, index) : 
        
        # 過去一天 / 目前持有資產信號
        self.previousPosition = self.extryExitPtData['position'].iloc[index-1]
        self.currentPosition = self.extryExitPtData['position'].iloc[index]

        # 特例：若資產從 i = 0 開始持有
        if (self.previousPosition != 0) & (index == 1) & (self.startIndex == -1):

            self.startIndex = 0

        # 若手上未有資產且出現入場點，則開倉。
        if (self.currentPosition != 0) & (self.previousPosition == 0) & (self.startIndex == -1):
            
            self.startIndex = index
    
    def closePositionMidMonth(self, index) :
        # 月中若在持有資產時出現出場點，則關倉。
        if (self.currentPosition == 0) & (self.previousPosition != 0) & (self.startIndex != -1):
            
            token1TransQty, token2TransQty = self.getEntryQty(index = self.startIndex)

            # 計算出場點 Long/Short 資產價值
            if index == 1 :

                self.getLongShortPortfolio(index = index, 
                                           token1TransQty = token1TransQty, 
                                           token2TransQty = token2TransQty, 
                                           isStartIndex = False)

                self.endDate = self.extryExitPtData['datetime'].iloc[index]
                self.endIndex = index

            else : 
                self.getLongShortPortfolio(index = index - 1, 
                                           token1TransQty = token1TransQty, 
                                           token2TransQty = token2TransQty, 
                                           isStartIndex = False)

                self.endDate = self.extryExitPtData['datetime'].iloc[index-1]
                self.endIndex = index -1
            
            # 計算入場點 Long/Short 資產價值
            self.getLongShortPortfolio(index = self.startIndex, 
                                       token1TransQty = token1TransQty, 
                                       token2TransQty = token2TransQty, 
                                       isStartIndex = True)

            self.startDate = self.extryExitPtData['datetime'].iloc[self.startIndex]

            # 計算加權平均報酬率 (Weighted-Return)
            self.calculateWeightedReturn()

            # 紀錄交易資訊
            self.recordEachTrade()

            # 紀錄交易次數
            self.trades = self.trades + 1

            # Reset Parameters
            self.startIndex = -1
            self.endIndex = -1


        
    def closePositionEndofMonth(self, index) :

        if (index == len(self.extryExitPtData)-1) & (self.startIndex != -1) :

            token1TransQty, token2TransQty = self.getEntryQty(index = self.startIndex)

            # 計算出場點 Long/Short 資產價值
            self.getLongShortPortfolio(index = index, 
                                       token1TransQty = token1TransQty,
                                       token2TransQty = token2TransQty, 
                                       isStartIndex = False)
            self.endDate = self.extryExitPtData['datetime'].iloc[index]
            self.endIndex = index
            
            # 計算入場點 Long/Short 資產價值
            self.getLongShortPortfolio(index = self.startIndex, 
                                       token1TransQty = token1TransQty,
                                       token2TransQty = token2TransQty, 
                                       isStartIndex = True)

            self.startDate = self.extryExitPtData['datetime'].iloc[self.startIndex]

            # 計算加權平均報酬率 (Weighted-Return)
            self.calculateWeightedReturn()
            
            # 紀錄交易資訊
            self.recordEachTrade()

            # 紀錄交易次數
            self.trades = self.trades + 1

            # Reset Parameters
            self.startIndex = -1
            self.endIndex = -1

    
    def recordEachTrade(self) : 

        returnRecordRow = {   
            # 'token1' :[self.token1Close_Colname] , 
            # 'token2' :[self.token2Close_Colname] ,

            'token1' :[self.token1] , 
            'token2' :[self.token2] ,

            'entry_date' : [self.startDate],
            'exit_date' : [self.endDate], 
            'long_return' : [self.weightReturnLong],
            'short_return' : [self.weightReturnShort],
            'return' : [self.weightReturn],

            'token1_return' : [self.token1Return],
            'token2_return' : [self.token2Return],
            
            'token1_weight_return' : [self.token1WeightedReturn],
            'token2_weight_return' : [self.token2WeightedReturn],

            'entry_zs' : [self.extryExitPtData['rollingZS'].iloc[self.startIndex]],
            'exit_zs': [self.extryExitPtData['rollingZS'].iloc[self.endIndex]],
            
            'entry_spread_demean' : [self.extryExitPtData['spreadDemean'].iloc[self.startIndex]],
            'exit_spread_demean': [self.extryExitPtData['spreadDemean'].iloc[self.endIndex]],
            
            'entryPercentile' : [self.extryExitPtData['entryPercentile'].iloc[self.startIndex]],

            # 'rolling_zs_rank' : [self.extryExitPtData['rollingZSRank'].iloc[self.startIndex]],
            # 'rolling_zs_prob' : [self.extryExitPtData['rollingZS_Prob'].iloc[self.startIndex]],

        }

        returnRecordRow = pd.DataFrame(returnRecordRow)
        self.returnRecord = pd.concat([self.returnRecord, returnRecordRow], ignore_index = True)


    def numberOfTrade(self) :
        
        numberOfTradeRow = {
            # 'token1' :[self.token1Close_Colname] , 
            # 'token2' :[self.token2Close_Colname] ,

            'token1' :[self.token1] , 
            'token2' :[self.token2] ,

            'trades' : [self.trades], 
        }

        numberOfTradeRow = pd.DataFrame(numberOfTradeRow)
        self.numberOfTradeRecord = pd.concat([self.numberOfTradeRecord, numberOfTradeRow], ignore_index = True)


    def main(self) :

        self.signal_alert = 0
        self.trades = 0
        self.startIndex = -1

        for i in range(1, len(self.extryExitPtData)):

            self.openPosition(index = i)
            self.closePositionMidMonth(index = i)
            self.closePositionEndofMonth(index = i)
        
        self.numberOfTrade()

    def getReturnRecord_EachPair(self):

        return self.returnRecord
    
    def getNumberofTrade_EachPair(self) : 

        return self.numberOfTradeRecord




