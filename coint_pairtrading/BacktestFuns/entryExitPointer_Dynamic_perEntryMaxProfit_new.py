import numpy as np
import pandas as pd
import statsmodels.api as sm
from other_funs import *


class entryExitPointer_Dynamic_perEntryMaxProfit:

    def __init__(self, pairsPriceData, beta, riskReward = 1/3 , reEntryThreshold = 0, entryPercentile = 0.01) :

        self.pairsPriceData = pairsPriceData
        
        self.beta = beta
        self.riskReward = riskReward
        
        self.entryPercentile = entryPercentile
        self.reEntryThreshold = reEntryThreshold

    def setInitSignal(self) : 
        
        self.exitPointAfterStopLoss = float('Inf') 

        self.reEntryAfterStopLossCond = 'None'
        
        self.exitSignalRecord = list()
        self.positionHoldRecord = list()
        
        self.isExitPoint = False
        self.isInvestAtFirstDate = False
        self.isCurrentHoldPortfolio = False
        self.isStopLossRecord = False

        self.keepHoldPosition = 0
        self.positionHold = 0

        self.spreadValuePrevious = 0
        self.spreadValueCurrent = 0

    def markEntryPoint(self) :
        
        # 判斷進場點
        spreadDemean = self.pairsPriceData['spreadDemean'].iloc[self.index]
        spreadPercentile = self.pairsPriceData['entryPercentile'].iloc[self.index]
        
        isPercentileBelowThreshold = spreadPercentile <= self.entryPercentile
        isSpreadPos = spreadDemean >= 0 
        isSpreadNeg = spreadDemean < 0


        # 判斷停利點是否有值
        takeProfitPt = self.pairsPriceData['takeProfitCurrent'].iloc[self.index]
        isTakeProfitExit = ~np.isnan(takeProfitPt)

        # 入場點 Spread 收斂條件
        isSpreadProfitable = abs(spreadDemean)/takeProfitPt >= 3

        # 停損後再進場條件
        self.reEntryAfterStopLossDict = {
            'None' : True,
            # 'SpreadShouldBeNeg' : (spreadDemean < 0),
            # 'SpreadShouldBePos' : (spreadDemean > 0),
            'SpreadShouldBeLowerThan' : (spreadDemean < self.reEntryThreshold),
            'SpreadShouldBeHigherThan' : (spreadDemean > -self.reEntryThreshold),

            }

        entryCondAfterStopLoss = self.reEntryAfterStopLossDict[self.reEntryAfterStopLossCond] # 停損後再進場條件 (New)

        # 若停損後再進場條件達成，則解除限制。
        if entryCondAfterStopLoss == True : 
            self.reEntryAfterStopLossCond = 'None'
            entryCondAfterStopLoss = self.reEntryAfterStopLossDict[self.reEntryAfterStopLossCond]

        self.positionHold = np.where(isSpreadPos &  entryCondAfterStopLoss & isTakeProfitExit & isPercentileBelowThreshold & isSpreadProfitable, 
                                     -1, 
                                     np.where(isSpreadNeg & entryCondAfterStopLoss & isTakeProfitExit & isPercentileBelowThreshold & isSpreadProfitable ,
                                              1, 
                                              0)
                                    )          

    def startGetPortfolio(self):

        # 若出現進場點 & 手上無資產，則開始持有投資組合。
        if (self.positionHold != 0) & (~self.isExitPoint) & (~self.isCurrentHoldPortfolio): 
            
            self.keepHoldPosition = self.positionHold
            spreadValueWhenEntry = self.pairsPriceData['spreadDemean'].iloc[self.index]
            
            # 最大停利點
            self.maxProfit = self.pairsPriceData['takeProfitCurrent'].iloc[self.index]
            self.exitCondStopProfit = (np.absolute(spreadValueWhenEntry) - self.maxProfit)
            self.exitCondStopLoss = (np.absolute(spreadValueWhenEntry) + self.maxProfit* self.riskReward)

            self.isCurrentHoldPortfolio = True
            self.isInvestAtFirstDate = True

    def markExitPoint(self) :

        # 若手上有投組，則依照入場點的 ZS 判斷目前是否為出場點。
        #if (self.index > 0) & (self.isCurrentHoldPortfolio) :
        if (self.isCurrentHoldPortfolio) :   
            
            if self.index > 0 : 
                self.spreadValuePrevious = self.pairsPriceData['spreadDemean'].iloc[self.index-1]
                
            self.spreadValueCurrent = self.pairsPriceData['spreadDemean'].iloc[self.index]

            # 出場條件判斷
            #isStopLoss = (np.absolute(self.spreadValueCurrent) >  self.exitCondStopLoss)
            isStopLoss = (np.absolute(self.spreadValueCurrent) >  self.exitCondStopLoss)
            isStopProfit = (np.absolute(self.spreadValueCurrent) < self.exitCondStopProfit)
            isCrossPosNeg = (self.spreadValuePrevious*self.spreadValueCurrent < 0)

            # 出場條件依目前的 ZS 更新
            newexitCondStopLoss = np.absolute(self.spreadValueCurrent) + self.maxProfit* self.riskReward
            self.exitCondStopLoss = min(self.exitCondStopLoss, newexitCondStopLoss)

            # 若第一天同時出現進場 & 出場訊號，則不考慮 ZS 正負號變化條件，直接出場。
            if self.isInvestAtFirstDate : 

                self.isExitPoint = isStopLoss | isStopProfit | isCrossPosNeg
                
                if isStopLoss : 
                    self.isStopLossRecord = True
                # else :                    
                #     # 若非停損出場則取消停損 Alert
                #     self.isStopLossRecord = False
                #     self.reEntryAfterStopLossCond = 'None'

            else : 
                self.isExitPoint = isStopLoss | isStopProfit | isCrossPosNeg

                if isStopLoss : 
                    self.isStopLossRecord = True
                # else :
                #     # 若非停損出場則取消停損 Alert
                #     self.isStopLossRecord = False
                #     self.reEntryAfterStopLossCond = 'None'

        else :
            self.isExitPoint = False

    def clearPortfolioIfExit(self) :
        
        self.exitSignalRecord.append(self.isExitPoint)
        self.positionHoldRecord.append(self.keepHoldPosition)
        self.isInvestAtFirstDate = False
        #self.isExitPoint = False

        # 若出現出場點，且目前手中持有投組，則將投資組合 Hold 到當天收盤為止。
        
        if (self.isCurrentHoldPortfolio) & (self.isExitPoint) : 

            if len(self.positionHoldRecord) < len(self.pairsPriceData)-1 :

                if self.isStopLossRecord : 
                    # 停損後再進場條件生效

                    # print(self.pairsPriceData['datetime'].iloc[self.index])

                    if self.spreadValueCurrent > 0 :
                        #self.reEntryAfterStopLossCond = 'SpreadShouldBeNeg'
                        self.reEntryAfterStopLossCond = 'SpreadShouldBeLowerThan'

                    else : 
                        #self.reEntryAfterStopLossCond = 'SpreadShouldBePos'
                        self.reEntryAfterStopLossCond = 'SpreadShouldBeHigherThan'

                    #self.exitPointAfterStopLoss = self.exitThresholdAfterStopLoss
                                
                #self.exitSignalRecord.append(self.isExitPoint)
                #self.positionHoldRecord.append(self.keepHoldPosition)        
                #self.keepHoldPosition = 0
                #self.index = self.index + 1
            
            self.isExitPoint = False
            self.keepHoldPosition = 0
            self.isCurrentHoldPortfolio = False



    def main(self) :

        self.setInitSignal()
        self.index = 0

        while self.index < len(self.pairsPriceData) : 

            self.markEntryPoint()
            self.startGetPortfolio()
            self.markExitPoint()
            self.clearPortfolioIfExit()

            self.index = self.index + 1

        self.pairsPriceData = self.pairsPriceData.assign(position = self.positionHoldRecord)
        self.pairsPriceData = self.pairsPriceData.assign(isExitPoint = self.exitSignalRecord)


    def getPositionRecord(self) : 
        
        return self.pairsPriceData
    