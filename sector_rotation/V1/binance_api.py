import sys
from datetime import datetime
import pandas as pd 
import datetime
import numpy as np
from binance.client import Client


def get_binance_api_object():

    # Binance API Token
    api_key = 'AccZsoScBxoX6xXZpVZD22iGx2BOFD35L0aIHB4LONPCHlx7A6Bd9gvFBS4WlYJG'
    api_secret = 'CG6RMwPrEn0UEHxRf6ThisxBTa8Og9TpoHbV4XuD0dhniyCo7MRBIfBE0WjbAq2I'
    client = Client(api_key, api_secret)  # 注意 futures=True

    return client


def get_klines_data_from_binance(symbol='BTCUSDT', resample_freq='1h', start_time="1 Jan, 1970", end_time=None, futures=True):
    """
    從 Binance 上抓取數據，並存成 csv 檔案。
    Args:
        symbol (str, optional): 要抓取的交易對. Defaults to 'BTCUSDT'.
        resample_freq (str, optional): 要抓取的時間週期. Defaults to '1h'.
        start_time (str, optional): 要抓取的起始時間. Defaults to '1 Jan, 1970'.
        end_time (str, optional): 要抓取的結束時間. Defaults to None.
    Returns:
        df: 抓取的數據
    """

    # Get Binance API Token
    client = get_binance_api_object()
    
    
    start_time = round(start_time.timestamp()*1000)
    end_time = round(end_time.timestamp()*1000)

    # Fetch BTC/USDT 1hr data
    if futures:
        print('Fetching futures data...')
        klines = client.futures_historical_klines(symbol, resample_freq, start_time, end_time)
        if len(klines) == 0:
            print('Future data empty, fetching spot data...')
            klines = client.get_historical_klines(symbol, resample_freq, start_time, end_time)
    else:
        print('Fetching spot data...')
        try:
            klines = client.get_historical_klines(symbol, resample_freq, start_time, end_time)
            if len(klines) == 0:
                print('Spot data empty, fetching future data...')
                klines = client.futures_historical_klines(symbol, resample_freq, start_time, end_time)
        except:
            print('Spot data return error, fetching futures data...')
            klines = client.futures_historical_klines(symbol, resample_freq, start_time, end_time)
    # turn to df
    df = pd.DataFrame(klines, columns=['open_time', 'open', 'high', 'low', 'close', 'volume',
                      'close_time', 'quote_asset_volume', 'trades', 'taker_buy_volume', 'taker_buy_quote', 'ignored'])
    
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

    # choose interested columns
    df = df[['open_time', 'close_time', 'open', 'high', 'low', 'close', 'volume','taker_buy_volume']]
    # turn to float
    df[['open', 'high', 'low', 'close', 'volume', 'taker_buy_volume']] = df[[
        'open', 'high', 'low', 'close', 'volume', 'taker_buy_volume']].astype(float)

    df['taker_sell_volume'] = df['volume'] - df['taker_buy_volume']
    # # save csv
    # df.to_csv(folder_path + f'{symbol}_{resample_freq}.csv', index=False)
    # # print message
    # print('Data saved to ' + folder_path + f'{symbol}_{resample_freq}.csv')
    return df


def get_funding_rate_data_from_binance(symbol='BTCUSDT', start_time="1970-01-01", end_time=None):

    # Get Binance API Token
    client = get_binance_api_object()

    start_time = round(start_time.timestamp()*1000)
    end_time = round(end_time.timestamp()*1000)

    print('Fetching funding rate data...')
    funding_rate = client.futures_funding_rate(symbol = symbol, startTime = start_time, endTime = end_time)
    df = pd.DataFrame(funding_rate, columns = ["symbol", "fundingRate" , "fundingTime"])
    df['fundingTime'] = pd.to_datetime(df['fundingTime'], unit='ms')

    return df 