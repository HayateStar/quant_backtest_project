# 共整合 Pair Trading 說明

## Alpha Idea

- 已知兩資產價格走勢呈共整合，若將兩資產依固定比例作線性組合，其數值應在一長期水準上下徘徊。若該數值出現過度正向或負向偏離，則均值回歸的機會較大。

- 若兩幣之間擁有共整合關係，如果共整合關係偏離，可做多價格被低估的幣種，同時做空價格被高估的幣種，當兩幣間重回長期均衡，則能夠藉此獲利。

## 使用資料
- CoinMarketCap 每月市值 Top 90 幣種期貨資料

## 策略建構流程

### Step 1

- 用過往三個月的日資料，挑出具共整合關係幣對。
- 使用線性回歸 OLS 計算資產多空比例 (β)

    > 有時候 β 會出現極小且在統計意義上不顯著之數值，避免 β 數值為雜音，故僅對 Adjusted R-Square ≥ 0.2 以上之幣對進行交易。

    > 若資產多空比例 (β) 為負數，則會失去 Pair Trading 的多空對沖效果，故 β < 0 之幣對一律不交易。

### Step 2
- 使用實證估計入場點條件 & 進出場點，詳細說明在此[連結](https://www.notion.so/sudo-research-labs/Doc-Cointegrated-Pair-Trading-5d06c8d84a3a4ee4b25bb84477a0329c?pvs=4#0912c15980c8444db30e39c1e799452b)。

### Step 3
- 根據先前共整合幣對 & 入場條件進行回測，回測後再依下列條件篩選交易紀錄以得到最終結果。
    > 幣對中至少其中一幣需在當時市值 Top 60 - 90 之間

    > 當下 SpreadDemean 絕對值需大於實證停利點數值的三倍
 
## 程式說明
    - ccm_crawling.py：在 CoinmarketCap 網站每月爬取 Top 90 幣種名稱 
    - findCointPairs.py：找出共整合幣對
    - getInOutData_new.py：使用實證資料估計進出場點
    - InOutBacktesting.py：Pair Trading 回測 
