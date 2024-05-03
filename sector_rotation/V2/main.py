from datetime import datetime
import pandas as pd 
import numpy as np
from tqdm import *
import plotly.express as px
import requests
from functools import partial
from multiprocessing import Pool
from importData import *
from backtestFun import *
import pickle

def importData():

    path = '/home/ivan/projects/TradFi_Projects/sector_rotation/data/'
    futurePriceDict = np.load(path + 'futurePriceDict.npy',allow_pickle='TRUE').item()
    return futurePriceDict


def _getEntryPoints(item: tuple, pastDays, date, swingThreshold = 0.2):

    tokenKey, priceData = item
    priceData = getEntryPoints(priceData, pastDays, date, swingThreshold = swingThreshold)
    entryPtData = entryPtCondition(priceData)
    
    return (tokenKey, entryPtData)


def _backtesting(item: tuple, priceDict, investDays = 5) :
    
    tokenKey, entryPtData = item
    priceData = priceDict[tokenKey]

    tradeRecords = backtesting(entryPtData = entryPtData,
                               tokenKey = tokenKey, 
                               priceData = priceData, 
                               investDays = investDays)
                               
    return tradeRecords


def getEntryPtParallelFun(priceDict, date, pastDays = 30, swingThreshold = 0.2):
    
    _func = partial(
        _getEntryPoints,
        pastDays = pastDays,
        date = date,
        swingThreshold = swingThreshold,
    )

    with Pool(processes=6) as pool:
        entryPtTuple = list((pool.imap(_func, priceDict.items())))
    
    entryPtDict = {}
    entryPtDict.update(entryPtTuple)

    return entryPtDict


def backtestParallelFun(entryPtDict, priceDict, investDays = 5):

    _func = partial(
        _backtesting,
        priceDict = priceDict,
        investDays = investDays, 
    )

    with Pool(processes=6) as pool:
        backtestTuple = list(tqdm(pool.imap(_func, entryPtDict.items())))

    backtestListDict = []
    for i in range(0, len(backtestTuple)):
        backtestListDict = backtestListDict + backtestTuple[i]

    return backtestListDict


def main(swingThreshold = 0.2, pastDays = 30, investDays = 5): 

    futurePriceDict = importData()
    entryPtDictAll = {}
    backtestListAll = []

    for date, priceDict in futurePriceDict.items():

        entryPtDict = getEntryPtParallelFun(priceDict = priceDict, 
                                            date = date, 
                                            pastDays = pastDays,
                                            swingThreshold = swingThreshold
                                            )
        entryPtDictAll[date] = entryPtDict

        backtestListDict = backtestParallelFun(entryPtDict = entryPtDict, 
                                               priceDict = priceDict, 
                                               investDays = investDays)

        backtestListAll = backtestListAll + backtestListDict

    # with open("entryPtDict_lowSwing.pkl", "wb") as outfile: 
    #     pickle.dump(entryPtDictAll, outfile)

    # with open("backtestList_lowSwing.pkl", "wb") as outfile: 
    #     pickle.dump(backtestListAll, outfile)
    
    return backtestListAll

if __name__ == "__main__":
    
    # swingThresholdList = [0.1, 0.2, 0.3]
    # pastDaysList = [10,20,30,40,50]
    # backtestDict = {}

    # for swingThreshold in tqdm(swingThresholdList) : 
    #     for pastDays in tqdm(pastDaysList) : 
    #         print(f"Now Backtesting : swingThreshold = {swingThreshold} , pastDays = {pastDays}")
    #         backtestList = main(swingThreshold = swingThreshold, pastDays = pastDays)

    #         backtestDict[(swingThreshold, pastDays)] = backtestList
    
    # with open("backtestGridSearchDict.pkl", "wb") as outfile :
    #     pickle.dump(backtestDict, outfile)

    
    swingThreshold = 0.3
    pastDays = 30
    backtestList = main(swingThreshold = swingThreshold, pastDays = pastDays)

    with open("backtestNonOverlap.pkl", "wb") as outfile :
        pickle.dump(backtestList, outfile)

