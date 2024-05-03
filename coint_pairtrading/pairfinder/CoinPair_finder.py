import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from pairfinder.other_funs import *

class FindCointPairs : 

    def __init__(self, priceDf , backtestStartDate, backtestEndDate) :


        self.priceDf = priceDf
        self.backtestStartDate = backtestStartDate
        self.backtestEndDate = backtestEndDate

        self.cointPairsData = pd.DataFrame()



    def findAllPairs(self, currentBacktestDate):

        priceDf = self.priceDf.copy()

        # Get token on specific currentBacktestDate
        priceDf = priceDf[priceDf['trading_date'] == currentBacktestDate]
        tokens = priceDf['token'].unique()

        allTokenPairs = [(a, b) for idx, a in enumerate(tokens) for b in tokens[idx + 1:]]

        self.allTokenPairs = allTokenPairs


    def mergePairsPriceData(self, pair, backtestStartDate) : 
        
        token1 = pair[0]
        token2 = pair[1]

        token1Close_Colname = token1 + '_close'
        token2Close_Colname = token2 + '_close'

        tokenPairsReturnData = merge_series(self.priceDf, backtestStartDate, token1, token2)

        # 設定檢定共整合區間
        cointDateStartDate = backtestStartDate - pd.DateOffset(months = 3)
        cointTestEndDate = backtestStartDate - pd.DateOffset(days = 1)

        tokenPairsReturnData_Coint = timeinterval_subset(tokenPairsReturnData, cointDateStartDate ,cointTestEndDate)
        tokenPairsReturnData_Coint = tokenPairsReturnData_Coint.reset_index(drop = True)

        return token1, token2, token1Close_Colname, token2Close_Colname, tokenPairsReturnData_Coint


    def cointPvalueCalculator(self, tokenPairsReturnData_Coint, token1Close_Colname, token2Close_Colname):

        cointPvalue = coint_test(tokenPairsReturnData_Coint[token1Close_Colname], tokenPairsReturnData_Coint[token2Close_Colname])
        token1ADFPvalue = adf_test(tokenPairsReturnData_Coint[token1Close_Colname].diff())
        token2ADFPvalue = adf_test(tokenPairsReturnData_Coint[token2Close_Colname].diff())

        return cointPvalue, token1ADFPvalue, token2ADFPvalue

    def cointConditions(self, cointPvalue, token1ADFPvalue, token2ADFPvalue) :

        # 設定共整合 Pvalue 檢定數值
        isPassCoint = (cointPvalue <= 0.05)
        isToken1PassADF = (token1ADFPvalue <= 0.1)
        isToken2PassADF = (token2ADFPvalue <= 0.1)

        return (isPassCoint & isToken1PassADF & isToken2PassADF)

    def r2Tester(self, adjR2) :

        # 設定 OLS R2 標準
        isR2LargeEnough = (adjR2 >= 0.2)
        return isR2LargeEnough
    
    # def paramsCollecter(self) :

    #     list_name = ['token1' , 'token2', 'alpha', 'beta', 'mu', 'sigma']
    #     params = {}

    #     for para in list_name :
    #         params[para] = []

    #     return params

    # def append_params(self, params_dict, cointPairParamsRow) :

    #     for para in params_dict.keys() :

    #         params_dict[para].append(cointPairParamsRow[para])
        
    #     return params_dict

    def cointJudger(self, tokenPairsReturnData_Coint, token1, token2, token1Close_Colname, token2Close_Colname, backtestStartDate) : 

        try : 

            cointPvalue, token1ADFPvalue, token2ADFPvalue = self.cointPvalueCalculator(tokenPairsReturnData_Coint, token1Close_Colname, token2Close_Colname)

            isPairPassCointTest = self.cointConditions(cointPvalue, token1ADFPvalue, token2ADFPvalue)


            if (isPairPassCointTest): 

                # Calculate Alpha & Beta
                alpha, beta, error, adjR2 = coint_alpha_beta(tokenPairsReturnData_Coint[token1Close_Colname], tokenPairsReturnData_Coint[token2Close_Colname])
                isR2LargeEnough = self.r2Tester(adjR2)

                if (isR2LargeEnough) : 

                    spread = tokenPairsReturnData_Coint[token2Close_Colname] - tokenPairsReturnData_Coint[token1Close_Colname]*beta
                    mu = np.mean(spread)
                    sigma = np.std(spread)


                    cointPairParamsRow= {
                        'token1' : [token1], 
                        'token2' : [token2], 
                        'alpha' : [alpha], 
                        'beta' : [beta], 
                        'mu' : [mu] , 
                        'sigma' : [sigma],
                        'trading_date' : [backtestStartDate]

                    }

                    cointPairParamsRow = pd.DataFrame(cointPairParamsRow)


                    self.cointPairsData = pd.concat([self.cointPairsData, cointPairParamsRow], ignore_index = True)
                    self.cointPairsData = self.cointPairsData[self.cointPairsData['beta'] > 0].reset_index(drop = True)

                    #params = self.append_params(params, cointPairParamsRow)
                
                else : 
                    pass
        
        except : 
            pass



    def main(self) : 

        backtestStartDate = self.backtestStartDate
        backtestEndDate = self.backtestEndDate

        while backtestStartDate <= backtestEndDate : 

            print('Now Finding Pairs : ' , backtestStartDate)

            #params = self.paramsCollecter()
            self.findAllPairs(backtestStartDate)
            

            for pair in self.allTokenPairs :

                token1, token2, token1Close_Colname, token2Close_Colname, tokenPairsReturnData_Coint = self.mergePairsPriceData(pair, backtestStartDate)
                # print(len(tokenPairsReturnData_Coint))
                # print(tokenPairsReturnData_Coint.head(5))

                if len(tokenPairsReturnData_Coint) > 0 : 
                    
                    self.cointJudger(tokenPairsReturnData_Coint, token1, token2, token1Close_Colname, token2Close_Colname, backtestStartDate)

                                
                else :
                    pass    
                
                                                
            backtestStartDate = backtestStartDate + pd.DateOffset(months = 1)
        

    
    def getCointPairs(self) : 

        return self.cointPairsData





        