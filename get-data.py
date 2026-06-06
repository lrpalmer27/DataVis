import os
import datetime
import wget 
import zipfile

"""
The purpose of this file is to retrieve data from binance programmatically, save it to a location, and post process it, given a date range.
Browser compatible data exploration:
    https://www.binance.us/finder?dpath=public_data%2Fspot%2Fdaily%2Fklines%2FBTCUSD%2F1d
    
"""
def aquireData(daterange):
    """
    The objective of this function is to download all the data within the given daterange and unpack the zip files. 
    Parameters are daterange(start,end), both bounds inclusive
    """

    basesavepath = './.rawdata'
    
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

def postprocessing():
    None
    

if __name__ == "__main__": 
    verbose = 1 
    performfcn = 'aquiredata' #aquiredata, or postprocess
    
    if performfcn == 'aquiredata': 
        #update date range as desired
        startdate = datetime.date(2019,9,17)
        enddate = datetime.date(2019,9,20) #datetime.datetime.now().strftime('%Y-%m-%d')-1
        
        aquireData(daterange=(startdate, enddate))
    