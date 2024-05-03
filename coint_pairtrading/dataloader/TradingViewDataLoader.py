import requests
import pandas as pd
import datetime
from datetime import datetime


# TradingView API
def get_data(symbol_name: str, interval: str, start_ts , end_ts):
    req = requests.get(f'https://ben-exp1.sudoresearch.dev/api/chart/bars?symbol_name={symbol_name}&interval={interval}&start_ts={str(start_ts)}&end_ts={str(end_ts)}')
    return req.json()
    
# def get_data(symbol_name: str, interval: str):
#     req = requests.get(f'https://ben-exp1.sudoresearch.dev/api/chart/bars?symbol_name={symbol_name}&interval={interval}')

#     return req.json()


class TradingViewDataLoader:

    def __init__(self, tickersDict, downloadStartDate, freq = '1D'):

        self.tickersDict = tickersDict
        self.downloadStartDate = downloadStartDate
        self.freq = freq

        self.priceDf = pd.DataFrame()
        self.notAvailableTokens = pd.DataFrame()

        # 穩定幣不列入考慮
        self.stableCoins = ['USDT', 'USDC', 'UST', 
                    'DAI', 'BUSD', 'XSGD', 
                    'TUSD', 'PAXG', 'IRON']


    def dataLoader(self, dateKey, tokenList):
        
        # 先下載幣安內資料
        tickerList = ['BINANCE:' + token + 'USDT.P' for token in tokenList]
        tickersDict = dict(zip(tokenList, tickerList))

        for token, ticker in tickersDict.items() :
            
            # start_ts = datetime.timestamp(dateKey)
            start_ts = datetime.timestamp(dateKey - pd.DateOffset(months = 6))
            end_ts = datetime.timestamp(dateKey + pd.DateOffset(months = 1) - pd.DateOffset(days = 1))

            if token not in self.stableCoins: 

                try : 

                    if self.freq == '60' : 
                        #tradingviewDict = get_data(ticker, '1D')
                        tradingviewDict = get_data(ticker, '60', start_ts, end_ts)
                        #tradingviewDict = get_data(ticker, '240', start_ts, end_ts)
                        dfBars =  pd.DataFrame(tradingviewDict['bars'])
                        dfBars.columns = tradingviewDict['header'][0:len(dfBars.columns)]
                        
                        dfBars['datetime'] = pd.to_datetime(dfBars['timestamp'], unit='s')
                        #dfBars['datetime'] = dfBars['datetime'].dt.date
                        #dfBars['datetime'] = pd.to_datetime(dfBars['datetime'])
                        dfBars = dfBars.sort_values(by = 'datetime')

                        dfBars = dfBars.assign(trading_date = dateKey)
                        dfBars = dfBars.assign(token = token)
                    
                    if self.freq == '1D':
                        
                        tradingviewDict = get_data(ticker, '1D')
                        #tradingviewDict = get_data(ticker, '60', start_ts, end_ts)
                        #tradingviewDict = get_data(ticker, '240', start_ts, end_ts)
                        dfBars =  pd.DataFrame(tradingviewDict['bars'])
                        dfBars.columns = tradingviewDict['header'][0:len(dfBars.columns)]
                        
                        #dfBars['datetime'] = pd.to_datetime(dfBars['timestamp'], unit='s')
                        dfBars['datetime'] = dfBars['datetime'].dt.date
                        dfBars['datetime'] = pd.to_datetime(dfBars['datetime'])
                        dfBars = dfBars.sort_values(by = 'datetime')

                        dfBars = dfBars.assign(trading_date = dateKey)
                        dfBars = dfBars.assign(token = token)


                    self.priceDf = pd.concat([self.priceDf, dfBars], ignore_index=True)

                
                except : 
                    
                    notavailableTokenRow = pd.DataFrame(
                        { 'trading_date' : [dateKey],
                          'token_na' : [token]
                        }
                    )

                    self.notAvailableTokens = pd.concat([self.notAvailableTokens, notavailableTokenRow] , ignore_index=True)

    def main(self) :

        for dateKey, tokenList in self.tickersDict.items():
            
            if dateKey >= self.downloadStartDate: 
                print('Now Downloading :' , dateKey)
                self.dataLoader(dateKey, tokenList)

    def getPriceData(self) :
        return self.priceDf

    def getNaTokens(self) :
        return self.notAvailableTokens