import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
import datetime
import numpy as np

def get_options():
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    return opts


# 爬取市值前 i 大 Token
def get_top_tokens(url, i = 100):

    top100_tokens= list()
    j = 0    

    # 開啟 Webdriver
    driver = webdriver.Firefox(options=get_options())
    driver.get(url)
    time.sleep(2)


    while j < i :

        try : 
            time.sleep(1)
            crypto_names = driver.find_elements(By.XPATH, '//*[@id="__next"]/div[2]/div[2]/div/div[1]/div[3]/div[1]/div[3]/div/table/tbody/'+'tr[' + str(j+1) + ']/td[3]/div')
            #driver.execute_script("arguments[0].scrollIntoView;", crypto_names)
            
            crypto_names = crypto_names[0].text
            top100_tokens.append(crypto_names)

        except :
                
            break
        
        # 網頁向下捲動
        driver.execute_script("window.scrollBy(0,500)","")

        j = j + 1

    driver.quit()

    return top100_tokens


import sys
import calendar

# 搜尋前一個月最後一周日期，打開網址用。
# e.g. 目前為 2017/3/1，預計使用 2017/2/26 (20170226) 之資料。
url_month_dict = {}

for year in range(2024,2025) : 
    for month in range(1, 13):
        last_sunday = max(week[-1] for week in calendar.monthcalendar(year, month))
        yyyymmdd = year * 10000 + month * 100 + last_sunday
        
        if (yyyymmdd >= 20240301) & (yyyymmdd <= 20240401):

            thenextmonth= pd.Timestamp(year, month, 1) + pd.DateOffset(months = 1)
            url_month_dict[thenextmonth] = yyyymmdd

            


# Navigate to the website
#url = "https://coinmarketcap.com/historical/20130505/"

# iList：下載 Top i 幣種
# iList = [50,70,90,100]
iList = [90]

for i in iList:

    top_i_tokens_dict = {}

    for date_key, url_date in url_month_dict.items() : 

        print("Now Crawling :" , str(url_date) + ' for ' + str(date_key) + ' i : ' + str(i))

        # 網址 = CMC String + str(每月最後一周日期) 
        url = "https://coinmarketcap.com/historical/" + str(url_date) + "/"
        
        top_i_tokens = get_top_tokens(url, i = i)

        top_i_tokens_dict[date_key] = top_i_tokens

    np.save("/home/ivan/projects/TradFi_Projects/coint_pairtrading/Final Code/Data/topTokens/"  + "top" + str(i) + "tokens_dict.npy", top_i_tokens_dict)