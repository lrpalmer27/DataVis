import matplotlib.pyplot as plt
import mplcursors
import numpy as np
import pandas as pd
import os

# import data
df = pd.read_csv('../bitcoin_2021-05-31_2026-05-30.csv')

print(df.head())
# ----------- pre-processing -----------
# make rolling calculations
df['SMA']=df['Volume'].rolling(window=30).mean()
df['std'] = df['Volume'].rolling(window=60).std()
df['neg3std'] = df['SMA']-3*df['std']
df['pos3std'] = df['SMA']+3*df['std']

# ----------- showing data -----------
# add data
fig, ax1 = plt.subplots(layout='constrained')
open=df.plot(x='Start',y='Open',ax=ax1,label="Open Price [$USD]",color='green',legend=False)
ax3=ax2=ax1.twinx()
vol=df.plot(x='Start',y='Volume',ax=ax2,label="Volume",color='tan',legend=False)
sma = df.plot(x='Start',y='SMA',ax=ax2,label="SMA 30d",color='blue',legend=False)
fill = ax2.fill_between(x=df['Start'],y1=df['neg3std'],y2=df['pos3std'],alpha=0.1, label="3*std (60day) offset from SMA")

#make legend, labels, show plots
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1+h2,l1+l2)
ax1.set_title("Visualizing BTC/USD Data")
ax1.set_xlabel("Dates")
ax1.set_ylabel("Price [$USD]")
ax1.tick_params('x', labelrotation=45)
mplcursors.cursor(hover=False)
plt.show()
