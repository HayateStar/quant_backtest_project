import pandas as pd 

def importCSV(filename):
    df = pd.read_csv(filename, index_col= 0) 
    return df

def convertToDatetime(df, timeCols : list):
    for timeCol in timeCols : 
        df[timeCol] = pd.to_datetime(df[timeCol], format = 'mixed')
    return df 

def changeTokenName(returnRecordDf, cols : list):

    for col in cols :
        returnRecordDf[col] = returnRecordDf[col].str.extract(r'(.*)_close')

    return returnRecordDf
