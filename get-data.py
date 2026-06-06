import os
import datetime
import wget 
import zipfile
import pandas as pd
from datetime import datetime, timezone

"""
The purpose of this file is to retrieve data from binance programmatically, save it to a location, and post process it, given a date range.
Browser compatible data exploration:
    https://www.binance.us/finder?dpath=public_data%2Fspot%2Fdaily%2Fklines%2FBTCUSD%2F1d
    
"""
def aquireData(basesavepath, daterange, verbose=0):
    """
    The objective of this function is to download all the data within the given daterange and unpack the zip files. 
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
    basefilename = "https://data.binance.us/public_data/spot/daily/klines/BTCUSD/1d/BTCUSD-1d-"
    binancefilenames = [f"{basefilename}{x}.zip" for x in listdates]

    if verbose: 
        print(os.path.isdir(basesavepath)) #does the saved folder exist?
        print(daterange[1]) #checking that daterange is imported correctly.
        print(datetime.datetime.now().strftime('%Y-%m-%d')) #datetime now in correct format
        print("days between: ", days_between,"\nlist of dates: ", listdates) #checking that date list generator works
        print("binanceOK filenames: ", binancefilenames) #checking that filenames follow binance syntax example-> https://data.binance.us/public_data/spot/daily/klines/BTCUSD/12h/BTCUSD-12h-2023-01-01.zip"

    # do the downloading here:
    [wget.download(url=binancefilenames[n],out=f"{basesavepath}/zipfiles/{listdates[n]}.zip") for n in list(range(0,days_between))]
    
    #unpack zip files here:
    zippedfiles = os.listdir(f"{basesavepath}/zipfiles") #grabbing all files in this folder, incase error is encountered above with preferred list
    for path in zippedfiles:
        with zipfile.ZipFile(f"{basesavepath}/zipfiles/{path}",'r') as objct:
            objct.extractall(f"{basesavepath}/csvfiles")

    # delete zipfiles folder content for storage saving
    fullstring=[f"{basesavepath}/zipfiles/{n}" for n in zippedfiles]
    [os.remove(n) for n in fullstring]

def postprocessing(basesavepath, verbose=0):
    """
    The objective of this function is to grab all data generated above, and parse csv files into one file for ease of future use.
    Parameters are:
        basesavepath (str) - folder location, does not have to exist
        daterange(start,end) - both bounds inclusive
        verbose - false by default.
    """
    listcsvfiles = [f"{basesavepath}/csvfiles/{n}" for n in os.listdir(f"{basesavepath}/csvfiles")]
    
    df = pd.concat((pd.read_csv(f) for f in listcsvfiles), ignore_index=True)
    
   
    start=datetime.fromtimestamp(df.iloc[0,df.columns.get_loc('open_time')]/1000,tz=timezone.utc).strftime('%Y-%m-%d')
    end=datetime.fromtimestamp(df.iloc[-1,df.columns.get_loc('close_time')]/1000,tz=timezone.utc).strftime('%Y-%m-%d')
    
    df.to_pickle(f"{basesavepath}/BTCUSD_{start}_{end}.pkl")
    
    if verbose: 
        print(listcsvfiles) #check that csv file names are generated correctly.
        print(df.head(5)) #check df data
        print('Open date: ', start, "close date: ", end) #checking start and end date of data
        
    # delete csv folder content for storage saving
    [os.remove(n) for n in listcsvfiles]
    

if __name__ == "__main__": 
    verbose = 1 
    basesavepath = './.rawdata'
    
    # performfcn = 'aquiredata' #aquiredata, or postprocess
    performfcn = 'postprocess' #aquiredata, or postprocess
    
    if performfcn == 'aquiredata': 
        #update date range as desired
        startdate = datetime.date(2026,6,1) #2026,9,17 is the first day of data in binance
        enddate = datetime.date(2026,6,5) #datetime.datetime.now().strftime('%Y-%m-%d')-1
        
        aquireData(basesavepath,daterange=(startdate, enddate),verbose=verbose)
    
    elif performfcn == 'postprocess': 
        postprocessing(basesavepath,verbose=verbose)
    