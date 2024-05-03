from datetime import datetime
import pandas as pd 
import numpy as np
from tqdm import *
import requests
from findBumpyFun import *


def calculateBumpyReturn(df_kbar,df_OI ,df_FR , tokens, isFROIFilter = True, returnLen = 5*6*4):

    bumpyIntervalAll = pd.DataFrame()

    for token in tokens : 

        try : 
            # bumpyInterval = get_bumpy_interval(df_kbar, df_OI ,df_FR, 
            #                                     token = token, returnLen = returnLen,
            #                                     isFROIFilter = isFROIFilter)
            bumpyInterval = get_bumpy_interval(df_kbar,
                                               token = token, returnLen = returnLen,
                                               isFROIFilter = isFROIFilter)

            bumpyIntervalAll = pd.concat([bumpyIntervalAll, bumpyInterval], ignore_index=True)

        except :
            pass
    
    return bumpyIntervalAll

def calculateOIFRReturn(priceData , OIData ,FRData, tokens, returnLen = 5*6*4):

    OIFRIntervalAll = pd.DataFrame()

    df_below_ma_threshold = get_bumpy_cond(priceData, OIData, FRData, isFROIFilter = True)
    df_below_ma_threshold = df_below_ma_threshold[df_below_ma_threshold['open_time'] >= date]

    oifrInterval = get_OIFR_interval(df, df_below_ma_threshold, token = token, returnLen = returnLen)
    oifrIntervalAll = pd.concat([oifrIntervalAll, oifrInterval], ignore_index = True)


    # for token in tokens : 

    #     try : 

    #         OIFRInterval= get_OIFR_interval(df_kbar, df_OI, df_FR, token = token, returnLen = returnLen)

    #         OIFRIntervalAll = pd.concat([OIFRIntervalAll, OIFRInterval], ignore_index=True)

    #     except :
    #         pass
    
    return OIFRIntervalAll


def getReturnTable(bumpyIntervalAll):

    yearlyGroup = bumpyIntervalAll.groupby(bumpyIntervalAll['endDate'].dt.year)['futureReturn']
    

    yearlyReturnAnalysis = yearlyGroup.agg(
                                    mean = 'mean',
                                    max = 'max',
                                    min = 'min',
                                    std = 'std',
                                    n_trade = 'size',

                                )

    yearlyReturnAnalysis = yearlyReturnAnalysis.reset_index()

    allReturnSeries = bumpyIntervalAll['futureReturn']
    
    allReturnAnalysisRow = {
        'endDate' : "All",
        'mean' : [np.mean(allReturnSeries)], 
        'max' : [max(allReturnSeries)],
        'min' : [min(allReturnSeries)],
        'std' : [np.std(allReturnSeries)],
        'n_trade' : [len(allReturnSeries)]

    }

    allReturnAnalysisRow = pd.DataFrame(allReturnAnalysisRow)
    yearlyReturnAnalysis = pd.concat([yearlyReturnAnalysis, allReturnAnalysisRow], ignore_index=True)
    
    return yearlyReturnAnalysis
