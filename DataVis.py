import matplotlib.pyplot as plt
import mplcursors
import numpy as np
import pandas as pd
import os

verbose=0
# import data assuming only one pickle file in .rawdata
rawdatafolder = './.rawdata'
datasource= [f for f in os.listdir(rawdatafolder) if f.endswith(".pkl")]
df = pd.read_pickle(f"{rawdatafolder}/{datasource[0]}")

if verbose: 
    print(df.head())
    print(df.tail())
    df = df.sort_values(by='open_time', ascending=True)
# ----------- pre-processing -----------
# make rolling calculations
df['volSMA']=df['volume'].rolling(window=365).mean()
df['std'] = df['volume'].rolling(window=365).std()
df['neg3std'] = df['volSMA']-3*df['std']
df['pos3std'] = df['volSMA']+3*df['std']
df['priceSMA1'] = df['open'].rolling(window=50).mean()
df['priceSMA2'] = df['open'].rolling(window=200).mean()
df['priceSMA3'] = df['open'].rolling(window=600).mean()

# ----------- showing data -----------
# plot 1 (top)
fig, (ax1, ax2) = plt.subplots(2,sharex=True, layout='constrained')

ax1.plot(df['open_time'],df['open'],label="Open Price",color='black')
ax1.plot(df['open_time'],df['priceSMA1'], label="50d Price SMA", color='green')
ax1.plot(df['open_time'],df['priceSMA2'], label="200d Price SMA", color='orange')
ax1.plot(df['open_time'],df['priceSMA3'], label="600d Price SMA", color='pink')

# plot 2 (bottom) -- 
ax2.plot(df['open_time'],df['open'],label="Open Price",color='black')
ax2.plot(df['open_time'],df['volume'],label="Volume",color='tan')
ax2.plot(df['open_time'],df['volSMA'],label="1Y vol SMA",color='blue')
ax2.fill_between(x=df['open_time'],y1=df['neg3std'],y2=df['pos3std'],alpha=0.1, label="Vol SMA offset 2 stdev")


#show plots
fig.canvas.manager.set_window_title('Various BTC/USDT Plots')
ax1.set_title('BTC/USDT Price & Various SMAs')
ax1.set_xlabel("Dates")
ax1.set_ylabel("Price [$USD]")
ax1.tick_params('x', labelrotation=45)
ax1.legend()

ax2.set_title('BTC/USDT Volume & SMA Offsets')
ax2.set_ylabel("Volume [$USD]")
ax2.set_xlabel("Dates")
ax2.tick_params('x', labelrotation=45)
ax2.legend()

mplcursors.cursor(hover=False)
plt.show()
