import os
import datetime
import wget 
import zipfile
import pandas as pd
import datetime
# from datetime import datetime, timezone, date

"""
The purpose of this file is to retrieve data from binance programmatically, save it to a location, and post process it, given a date range.
Browser compatible data exploration:
    https://www.binance.us/finder?dpath=public_data%2Fspot%2Fdaily%2Fklines%2FBTCUSD%2F1d

How to use this?
    1. Run aquireData to pull data from web
    2. Run postprocessing to convert csv files to pkl file
    3. Run ------ to add newest data to pkl file (feature coming soon!)
    
"""
def aquireData(basesavepath, daterange, verbose=0):
    """
    The objective of this function is to download all the data within the given daterange. 
    Parameters are:
        basesave path (str) - folder location, does not have to exist
        daterange(start,end) - both bounds inclusive
        verbose - false by default.
    """
    
    #make sure subfolders exist that are needed: 
    os.makedirs(basesavepath, exist_ok=True) #make basepath if not existing
    os.makedirs(f"{basesavepath}/zipfiles", exist_ok=True) #make subfolder for zipfiles
    os.makedirs(f"{basesavepath}/csvfiles", exist_ok=True) #make subfolder for unpacked zip files (csv format)
        
    # dates between
    days_between = (daterange[1]-daterange[0]).days + 1
    listdates=[str(daterange[0] + datetime.timedelta(days=x)) for x in range(days_between)]
    
    # list of binance filenames
    basefilename = "https://data.binance.us/public_data/spot/daily/klines/BTCUSDT/1h/BTCUSDT-1h-"
    binancefilenames = [f"{basefilename}{x}.zip" for x in listdates]

    if verbose: 
        print(os.path.isdir(basesavepath)) #does the saved folder exist?
        print(daterange[1]) #checking that daterange is imported correctly.
        print(datetime.datetime.now().strftime('%Y-%m-%d')) #datetime now in correct format
        print("days between: ", days_between,"\nlist of dates: ", listdates) #checking that date list generator works
        print("binanceOK filenames: ", binancefilenames) #checking that filenames follow binance syntax example-> https://data.binance.us/public_data/spot/daily/klines/BTCUSD/12h/BTCUSD-12h-2023-01-01.zip"

    # do the downloading here:
    [wget.download(url=binancefilenames[n],out=f"{basesavepath}/zipfiles/{listdates[n]}.zip") for n in list(range(0,days_between))]


def postprocessing(basesavepath, verbose=0):
    """
    The objective of this function is to grab all data generated above, and parse csv files into one file for ease of future use.
    Parameters are:
        basesavepath (str) - folder location, does not have to exist
        daterange(start,end) - both bounds inclusive
        verbose - false by default.
    """
    #unpack zip files here:
    
    zippedfiles = os.listdir(os.path.join(basesavepath,'zipfiles')) #grabbing all files in this folder, incase error is encountered above with preferred list
    for path in zippedfiles:
        with zipfile.ZipFile(os.path.join(basesavepath,'zipfiles',path),'r') as objct:
            objct.extractall(os.path.join(basesavepath,'csvfiles'))

    # delete zipfiles folder content for storage saving
    fullstring=[os.path.join(basesavepath,'zipfiles',n) for n in zippedfiles]
    [os.remove(n) for n in fullstring]
    
    # Combine all csv files into one dataframe
    listcsvfiles = [os.path.join(basesavepath,'csvfiles',n)  for n in os.listdir(os.path.join(basesavepath,'csvfiles'))]
    df = pd.concat((pd.read_csv(f) for f in listcsvfiles), ignore_index=True)
    
    # # convert time columns to datetime obj
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    df['volume'] = df['volume']*1e+9

    if verbose: 
        print(listcsvfiles) #check that csv file names are generated correctly.
        print(df.head(5)) #check df data
        # print('Open date: ', start, "close date: ", end) #checking start and end date of data
    
    # delete csv folder content for storage saving
    [os.remove(n) for n in listcsvfiles]
    
    return df

def updatepickle(basesavepath,newdata,verbose=0):
    """
    This function grabs the old pickle file, together with the new post processed data, combines them, saves, and deletes the old.
    """
    opfn = [f for f in os.listdir(basesavepath) if f.endswith(".pkl")][0]
    oldpicklefilepath=f"{basesavepath}/{opfn}"
    
    olddf = pd.read_pickle(oldpicklefilepath)
    
    combineddf=pd.concat((olddf,newdata),ignore_index=True)
    
    return combineddf


def save2pickle(basesavepath, dataframe, verbose=0):
    """
    All this function does is intake a dataframe, grab the first and last date, and save the file.
    """
    df=dataframe
    # # # save pickle file
    start=df.iloc[0,df.columns.get_loc('open_time')].strftime('%Y-%m-%d')
    end=df.iloc[-1,df.columns.get_loc('close_time')].strftime('%Y-%m-%d')
    df.to_pickle(f"{basesavepath}/BTCUSDT_{start}_{end}.pkl")
    

if __name__ == "__main__": 
    verbose = 0 
    basesavepath = './.rawdata'

    performfcn = 'updateData' #initialDataAq, cleanup, or updateData
    
    if performfcn == 'initialDataAq': 
        #update date range as desired
        startdate = datetime.date(2019,9,23) #2019-09-23 is the first day for btcusdt data in binance. // 2019,9,17 is the first day of data in binance for BTCUSD
        enddate = datetime.date(2020,6,20) #datetime.datetime.now().strftime('%Y-%m-%d')-1
        
        # download data
        aquireData(basesavepath,daterange=(startdate, enddate),verbose=verbose) 
        
        #extract data, post-process and save to pickle file. This outputs the complete df
        df=postprocessing(basesavepath,verbose=verbose)
        
        # save pickle file
        save2pickle(basesavepath=basesavepath, dataframe=df,verbose=verbose)
    
    elif performfcn == 'cleanup':
        #this function is used when there is some kind of http timeout. 
        
        #postprocess new data
        newdata=postprocessing(basesavepath,verbose=verbose)
        
        #combine new data with old pickle data!
        df=updatepickle(basesavepath,newdata=newdata,verbose=verbose)
        
        save2pickle(basesavepath=basesavepath, dataframe=df,verbose=verbose)
    
    elif performfcn == 'updateData': 
        #daterange to update between
        startdate = datetime.date(2021,5,26) #2019,9,17 is the first day of data in binance
        enddate = datetime.date(2026,6,20) #datetime.datetime.now().strftime('%Y-%m-%d')-1
        
        # download data
        aquireData(basesavepath,daterange=(startdate, enddate),verbose=verbose) 
        
        #postprocess new data
        newdata=postprocessing(basesavepath,verbose=verbose)
        
        #grab old data from picklefile
        df=updatepickle(basesavepath,newdata=newdata,verbose=verbose)
        
        save2pickle(basesavepath=basesavepath, dataframe=df,verbose=verbose)

        
        
    