from datetime import datetime
import pandas as pd 
import numpy as np
from multiprocessing import Pool
import multiprocessing
import pickle
from tqdm import *
from random import randrange
from functools import partial


def getFutureTimeIndex(kbarYear,returnLen):

    endPrice = []

    while len(endPrice) == 0 : 

        randomIndex = randrange(len(kbarYear))
        startRow = kbarYear.iloc[randomIndex]
        
        startTime = startRow['open_time']
        startPrice = startRow['close']

        endTime = startTime  + pd.DateOffset(hours = returnLen)
        endPrice = kbarYear[kbarYear['open_time'] == endTime]['close'].reset_index(drop=True)

    return startTime


def func(item: tuple, date, bumpyTradeRecord):

    token, kbar = item
    returnLen = 5*6*4

    years = kbar['open_time'].dt.year.unique()
    randomReturnDf = pd.DataFrame()
    
    for year in tqdm(years): 
        
        #kbarYear = kbar[kbar['open_time'].dt.year == year].reset_index(drop = True)
        kbarYear = kbar[kbar['open_time'] >= date].reset_index(drop = True)

        if len(kbarYear) > 360 :
            #for j in range(0,100) :
            for j in range(0,100) :

                startTime = getFutureTimeIndex(kbarYear,returnLen)

                afterSignalHours = 4

                while afterSignalHours <= returnLen : 
                    
                    endTime = startTime  + pd.DateOffset(hours = afterSignalHours)
                    
                    try :
                        startPrice = kbarYear[kbarYear['open_time'] == startTime]['close'].reset_index(drop=True)
                        endPrice = kbarYear[kbarYear['open_time'] == endTime]['close'].reset_index(drop=True)

                        startPrice = startPrice[0]
                        endPrice = endPrice[0]
                        
                        randomReturn = (endPrice - startPrice)/startPrice

                        if randomReturn <= -0.1 : 
                            break

                    except :
                        pass
                    
                    afterSignalHours = afterSignalHours + 4
                    
                    

                randomReturnRow = { 'date' : [date],
                                    'token' : [token],
                                    'randomReturn' : [randomReturn]
                                  }

                randomReturnRow = pd.DataFrame(randomReturnRow)
                randomReturnDf = pd.concat([randomReturnDf, randomReturnRow], ignore_index= True)

    return randomReturnDf


def randomBeta(df_kbar, date, returnLen = 5*6*4) : 
    
    randomReturnDf = pd.DataFrame()
    #countOfToken = bumpyIntervalAll.groupby([bumpyIntervalAll['token'], bumpyIntervalAll['endDate'].dt.year])[['token']].size().reset_index(name = 'count')
    df_kbar_sector = df_kbar.items()

    cpus = multiprocessing.cpu_count()
    print(f"Start with {cpus} cpus")


    _func = partial(func,
                    date = date,
                    )

    with Pool(processes=6) as pool:
        randomReturnDf_token = list(tqdm(pool.imap(_func, df_kbar_sector)))

    # with Pool(processes=6) as pool:
    #     randomReturnDf_token = list(tqdm(pool.imap(func, df_kbar_sector)))
        #randomReturnDf_token = randomReturnDf_token[0]

    for i in range(0, len(randomReturnDf_token)) : 
        randomReturnDf = pd.concat([randomReturnDf, randomReturnDf_token[i]], ignore_index=True)
        
    return randomReturnDf
    