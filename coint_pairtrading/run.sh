# Step 1：Get Data
## Input
    # 於 .py 檔內調整日期 & 排名參數 
## Output
    # 檔名：topXtokens_dict.npy 
    # 敘述：每月市值 Top X 的幣種名稱    
python ccm_crawling.py

# Step 2：Get Cointegration Pairs
## Input : topXtokens_dict.npy
## Output
    # 檔名
        # pricePerpDf_60_6M_topX.csv
        # cointPairsData_TopX.csv
    # 敘述
        # 期貨小時 K 資料
        # 共整合幣對資料
python findCointPairs.py

# Step 3：Calculate Stop Profit & Stop Loss Points
## Input
    # pricePerpDf_60_6M_topX.csv
    # cointPairsData_TopX.csv
## Output
    # 檔名
        # pairInOutDataDict_TopX.pkl
    # 敘述
        # 各幣對的進出場點參數  
python getInOutData_new.py

# Step 4：Backtesting
## Input
    # pricePerpDf_60_6M_topX.csv
    # cointPairsData_TopX.csv
    # pairInOutDataDict_TopX.pkl

## Output
    # 檔名
        # returnRecord.csv
    # 敘述
        # 不同參數下的逐筆交易回測紀錄
        # 需要手動篩選交易紀錄 (幣對中至少任一幣種為當時 Top 60 - 90 ，始能與先前回測結果對齊。)
python InOutBacktesting.py