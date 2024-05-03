import requests
import pandas as pd
import datetime
from datetime import datetime


# CoinGlass API

def get_future_data(symbol : str , start_ts, end_ts , exchange = 'binance', interval = '1d', dataType = 'kline'):
    req = requests.get(f'http://192.168.1.140:8002/coinglass/data?exchange={exchange}&interval={interval}&type={dataType}&symbol={symbol}&start={str(start_ts)}&end={str(end_ts)}')
    return req.json()


class CoinGlassDataLoader:

    def __init__(self, tickersDict, downloadStartDate, freq = '1d'):

        self.tickersDict = tickersDict
        self.downloadStartDate = downloadStartDate
        self.freq = freq

        self.priceDict = {}
        self.priceDf = pd.DataFrame()
        self.notAvailableTokens = pd.DataFrame()

        # 穩定幣不列入考慮
        self.stableCoins = ['USDT', 'USDC', 'UST', 
                    'DAI', 'BUSD', 'XSGD', 
                    'TUSD', 'PAXG', 'IRON']


    def dataLoader(self, dateKey, tokenList):
        
        # 先下載幣安內資料
        tickerList = [token + 'USDT' for token in tokenList]
        tickersDict = dict(zip(tokenList, tickerList))

        for token, ticker in tickersDict.items() :
            
            start_ts = datetime.timestamp(dateKey - pd.DateOffset(months = 3))
            end_ts = datetime.timestamp(dateKey + pd.DateOffset(months = 3))

            if token not in self.stableCoins: 

                try : 

                    coinGlassDict = get_future_data(symbol = ticker, 
                                                        interval = self.freq, 
                                                        start_ts = start_ts, 
                                                        end_ts = end_ts , 
                                                        dataType = 'kline')

                    dfBars =  pd.DataFrame(coinGlassDict['data'])
                    dfBars.columns = coinGlassDict['columns'][0:len(dfBars.columns)]
                    
                    dfBars['datetime'] = pd.to_datetime(dfBars['timestamp'], unit='s')
                    dfBars = dfBars.sort_values(by = 'datetime')

                    #dfBars = dfBars.assign(trading_date = dateKey)
                    dfBars = dfBars.assign(token = token)
                    

                    dfBars = dfBars.rename(columns = {"datetime" : "open_time"})
                    self.priceDf = pd.concat([self.priceDf, dfBars], ignore_index=True)

                    self.priceDict[dateKey][token] = dfBars

                
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
                self.priceDict[dateKey] = {}
                self.dataLoader(dateKey, tokenList)

    def getPriceData(self) :
        return self.priceDict

    def getNaTokens(self) :
        return self.notAvailableTokens