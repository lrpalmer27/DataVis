# Data Vis Project

This project is built to be a playground exploring different matplotlib features and technical analysis on a generic dataset.

## What's Included?
### get-data.py
This file pulls data from Binance and pre-processes it into a pickle file to be used by other parts of this project. Data is not included in this repo, but can be generated fairly quickly.

    Binance data explanation here: https://support.binance.us/en/articles/9843310-introducing-historical-market-data-from-binance-us-download-for-free?utm_source=chatgpt.com
    Binance data web explorer: https://www.binance.us/finder?dpath=public_data%2Fspot%2Fdaily%2Fklines%2FBTCUSD%2F1d


### DataVis.py
This file plots some basic items over the range of data available.

### TrainLSTM.py
Training for an LSTM model.

# Known data problems
BTC/USD - Binance has missing data between 2023-07-14 through 2025-02-20
Charts use BTC/USDT moving fwd.

# Current Progress as of 06/01/2026:
Basic plots generated from DataVis.py

![](./assets/Figure_4.png)