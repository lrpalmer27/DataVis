import os
import sys
import pandas as pd
import numpy as np
import math
import tensorflow as tf
import datetime
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import *
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.metrics import RootMeanSquaredError
from tensorflow.keras.optimizers import Adam

def dfprep(verbose=0):
    basesavepath = './.rawdata'
    datasource= [f for f in os.listdir(basesavepath) if f.endswith(".pkl")]
    df = pd.read_pickle(f"{basesavepath}/{datasource[0]}")
    df.index = pd.to_datetime(df['open_time'],format="%Y-%m-%d %H:%S:%S")
    
    if verbose:
        print(df.head(5))
        print(df.shape)
        print(df['open_time'].dtype)
    
    splitdf = df.iloc[:, [df.columns.get_loc("open"),df.columns.get_loc("volume")]]
    
    if verbose: 
        print(splitdf.shape)
        print(splitdf.head(5))
    
    return splitdf
    
def df2XY(df,windowsize=5):
    df_as_np = df.to_numpy()
    X=[]
    Y=[]
    for i in range(len(df_as_np)-windowsize):
        row = [a for a in df_as_np[i:i+windowsize]]
        X.append(row)
        label = df_as_np[i+windowsize,0]
        Y.append(label)
        
    return np.array(X), np.array(Y)
   
def splitsy(X,Y): 
    X_train, Y_train  = X[:45000], Y[:45000]
    X_val, Y_val  = X[45000:52000], Y[45000:52000]
    X_test, Y_test = X[52000:], Y[52000:]
    
    if verbose: 
        print(X_train.shape, Y_train.shape)    
        print(X_val.shape, Y_val.shape)    
        print(X_test.shape, Y_test.shape)  
        print(X_test.dtype,Y_test.dtype)  
        print(X_train)
    
    return X_train, Y_train, X_val, Y_val, X_test, Y_test
    

def train(X_train, Y_train, X_val, Y_val, X_test, Y_test,verbose=0):
    if verbose:     
        print(df.head(5))
        print(X.shape, Y.shape)
        # print(X,Y)
    
    model1 = Sequential()
    model1.add(InputLayer((X_train.shape[1],X_train.shape[2])))
    model1.add(LSTM(256, return_sequences=True))
    model1.add(Dropout(0.1))
    model1.add(LSTM(128,return_sequences=True))
    model1.add(Dropout(0.1))
    model1.add(Dense(16,'relu'))
    model1.add(Dense(1,'linear'))
    
    model1.summary()
    
    cp = ModelCheckpoint(filepath='.data/LSTM-model1.keras', save_best_only=True)
    model1.compile(loss=MeanSquaredError(), optimizer=Adam(learning_rate=0.0011), metrics=[RootMeanSquaredError()])
    
    if verbose:
        print(tf.config.list_physical_devices())    
        
    model1.fit(X_train,Y_train,validation_data=(X_val,Y_val), epochs=200, callbacks=[cp])     

if __name__ == "__main__": 
    verbose = 1
    
    # data prep
    df = dfprep(verbose=verbose)
    X,Y = df2XY(df, windowsize=5)
    X_train, Y_train, X_val, Y_val, X_test, Y_test = splitsy(X,Y)
    
    #training call
    training = True
    if training: 
        train(X_train, Y_train, X_val, Y_val, X_test, Y_test,verbose=verbose)
    
    #reload good model
    results=True
    if results: 
        model1 = load_model('.data/LSTM-model1.keras')    
        train_predictions = model1.predict(X_train).flatten()
        train_results = pd.DataFrame(data={'Predicted Open':train_predictions,'Actual Open': Y_train})
        print(train_results)
    
        plt.plot(train_results['Predicted Open'], label='Predicted')
        plt.plot(train_results['Actual Open'], label='Actual')
        plt.show()

    