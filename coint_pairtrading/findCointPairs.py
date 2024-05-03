### Import Packages
import pandas as pd
import numpy as np
from datetime import datetime
import datetime

from dataloader.coinGlassDataLoader import *
# from dataloader.TradingViewDataLoader import *
from pairfinder.CoinPair_finder import *


# iList = [50,70,90,100]
iList = [90]

for i in iList : 

    ### Get Top i Tokens Name ### 
    fileDirPath = "/home/ivan/projects/TradFi_Projects/coint_pairtrading/Final Code/Data/topTokens/"
    topiTokensDict = np.load(fileDirPath + "top" + str(i) + "tokens_dict.npy", allow_pickle=True)
    topiTokensDict = topiTokensDict.item()

    ### Set the Timeframe of Backtesting ###
    startDate = pd.Timestamp(2020,1,1)
    endDate = pd.Timestamp(2024,5,1)

    ### Download Hourly Data from Coinglass API ### 
    dataloader = CoinGlassDataLoader(tickersDict = topiTokensDict, 
                                     downloadStartDate = startDate,
                                     freq = '1h')

    dataloader.main()
    priceDftoBackTest = dataloader.getPriceData()

    ### Save Hourly Data for Backtestiing ###
    fileDirPath = "/home/ivan/projects/TradFi_Projects/coint_pairtrading/Final Code/Data/KBar/"
    priceDftoBackTest.to_csv('pricePerpDf_60_6M_' + 'top' + str(i) + '.csv')

### Find Cointegration Pairs ###

    ### Get Daily Data for Finding Cointegrated Pairs ### 
    dataloader = CoinGlassDataLoader(tickersDict = topiTokensDict, 
                                     downloadStartDate = startDate,
                                     freq = '1d')

    dataloader.main()

    priceDftoFindCoint = dataloader.getPriceData()
    #notAvailableTokensDf = dataloader.getNaTokens()
    #priceDftoFindCoint.to_csv('pricePerpDf_1D_6M_' + 'top' + str(i) + '.csv')
    
    ### Find Cointegrated Pairs ###
    cointFinder = FindCointPairs(priceDf = priceDftoFindCoint, 
                                 backtestStartDate = startDate, 
                                 backtestEndDate = endDate)

    cointFinder.main()
    cointPairsData = cointFinder.getCointPairs()

    ### Save Cointegrated Pairs with Parameters (beta) ###
    fileDirPath = "/home/ivan/projects/TradFi_Projects/coint_pairtrading/Final Code/Data/cointPairs/"
    cointPairsData.to_csv(fileDirPath + 'cointPairsData_Top' + str(i) + '.csv')