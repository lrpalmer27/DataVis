import matplotlib.pyplot as plt
import mplcursors
import numpy as np
import pandas as pd
import os

# import data assuming only one pickle file in .rawdata
rawdatafolder = './.rawdata'
datasource= [f for f in os.listdir(rawdatafolder) if f.endswith(".pkl")]
df = pd.read_pickle(f"{rawdatafolder}/{datasource[0]}")

print(df.head())
print(df.tail())
df = df.sort_values(by='open_time', ascending=True)
# ----------- pre-processing -----------
# make rolling calculations
df['volSMA']=df['volume'].rolling(window=365).mean()
df['std'] = df['volume'].rolling(window=365).std()
df['neg3std'] = df['volSMA']-3*df['std']
df['pos3std'] = df['volSMA']+3*df['std']
df['priceSMA'] = df['open'].rolling(window=730).mean()
df['5SMA'] = df['priceSMA']*5

# ----------- showing data -----------
# add data
fig, ax1 = plt.subplots(layout='constrained')
ax1.plot(df['open_time'],df['open'],label="Open Price [$USD]",color='black')
ax3=ax2=ax1.twinx()
ax2.plot(df['open_time'],df['volume'],label="Volume",color='tan')
ax2.plot(df['open_time'],df['volSMA'],label="1Y vol SMA",color='blue')
ax2.fill_between(x=df['open_time'],y1=df['neg3std'],y2=df['pos3std'],alpha=0.1, label="3*std (60day) offset from vol SMA")
ax1.plot(df['open_time'],df['priceSMA'], label="2Y Price SMA", color='green')
ax1.plot(df['open_time'],df['5SMA'], label="5*2Y Price SMA", color='red')

#make legend, labels, show plots
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1+h2,l1+l2)
ax1.set_title("Visualizing BTC/USD Data")
ax1.set_xlabel("Dates")
ax1.set_ylabel("Price [$USD]")
ax2.set_ylabel("Volume")
ax1.tick_params('x', labelrotation=45)
mplcursors.cursor(hover=False)
plt.show()
