# Step 1：Get Data
## Output
    # futurePriceDict.npy：期貨四小時線資料
    # df_OI.npy：OI 四小時線資料 (2023/10 - )
    # df_FR.npy：Funding Rate 四小時線資料 (2023/10 - )
python downloadData.py

# Step 2：Find Bumpy Interval & Backtesting
## Input
    # futurePriceDict.npy
    # df_OI.npy
    # df_FR.npy
## Output
    # bumpyTradeRecordAll_BumpyAddStaticStoploss.csv：帶量突破濾網回測結果
    # oiFRTradeRecordAll.csv：OI/FR 濾網回測結果
    # bumpyOIFRTradeRecordAll_NewStoploss.csv：帶量突破 + OI/FR 濾網回測結果
    # betaAll.csv：隨機抽取報酬紀錄

python main.py