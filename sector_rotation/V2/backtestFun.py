from datetime import datetime
import pandas as pd 
import numpy as np
from tqdm import *
import plotly.express as px
import requests
from functools import partial
from multiprocessing import Pool
from importData import *


def entryPtCondition(priceData):

    entryPtData = priceData[priceData['isEntryPoint']]

    return entryPtData

def getEntryPoints(priceData, pastDays, date, swingThreshold = 0.2):

    #pastDays = 30
    pastLen = int(pastDays*24/4)

    closePriceRollingObj = priceData['close'].rolling(pastLen)

    rollingMin = closePriceRollingObj.min().shift(1)
    rollingMax = closePriceRollingObj.max().shift(1)

    priceData = priceData.assign(rollingMin = rollingMin, 
                                 rollingMax = rollingMax,
                                 )

    swing = (1 - priceData['rollingMin']/priceData['rollingMax'])
    priceData = priceData.assign(swing = swing, pastSwing = swing.shift(6))
    #priceData = priceData.assign(swing = swing, pastSwing = swing.shift(1))

    isNewHighClose = (priceData['close'] >= priceData['rollingMax'])
    isLowSwing = (priceData['swing'] <= swingThreshold)
    isLowPastSwing = (priceData['pastSwing'] <= swingThreshold)

    priceData = priceData.assign(isNewHighClose = isNewHighClose, 
                                 isLowSwing = isLowSwing, 
                                 isLowPastSwing = isLowPastSwing)

    isEntryPoint = (priceData['isNewHighClose']) & (priceData['isLowPastSwing'])
    priceData = priceData.assign(isEntryPoint = isEntryPoint)
    priceData = priceData[priceData['open_time'] >= date]

    return priceData



def backtesting(entryPtData, tokenKey, priceData, investDays = 5):

    tradeRecords = []

    stopTime = pd.Timestamp(2000,1,1)

    #priceMA= priceData['close'].rolling(50).mean().shift(1)
    #priceData = priceData.assign(priceMA = priceMA)

    for i in (range(0, len(entryPtData))) :

        entryTime = entryPtData.iloc[i]['open_time']
        now = entryPtData.iloc[i]['open_time']

        if entryTime > stopTime : 
            stopTime = entryTime + pd.DateOffset(days = investDays)

            #futureReturn = None

            while now <= stopTime :

                try : 
                    startPrice = priceData[priceData['open_time'] == entryTime]['close'].values[0]
                    currentPrice = priceData[priceData['open_time'] == now]['close'].values[0]
                    #currentPriceMA = priceData[priceData['open_time'] == now]['priceMA'].values[0]

                    futureReturn = (currentPrice - startPrice)/startPrice

                    if (futureReturn <= -0.1):
                        break
                    
                except :
                    pass
                
                now = now + pd.DateOffset(hours = 4)
            
            tradeRecord = { 'token' : tokenKey,
                            'entryTime' : entryTime,
                            'stopTime' : now,
                            'return' : futureReturn,
                        }

            stopTime = now

            tradeRecords.append(tradeRecord)
        
    return tradeRecords

