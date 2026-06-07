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
    model1.compile(loss=MeanSquaredError(), optimizer=Adam(), metrics=[RootMeanSquaredError()])
    
    if verbose:
        print(tf.config.list_physical_devices())    
        
    model1.fit(X_train,Y_train,validation_data=(X_val,Y_val), epochs=5, callbacks=[cp], verbose=verbose)     

def zscoreNorm_manual(inp,mean,std):
    return (inp-mean)/std

def normalizedata(X_train, Y_train, X_val, Y_val, X_test, Y_test,verbose=0): 
    
    x_train_1=zscoreNorm_manual(X_train,unNormData["xtrain"][0],unNormData["xtrain"][1])
    y_train_1=zscoreNorm_manual(Y_train,unNormData["ytrain"][0],unNormData["ytrain"][1])
    
    x_val_1=zscoreNorm_manual(X_val,unNormData["xval"][0],unNormData["xval"][1])
    y_val_1=zscoreNorm_manual(Y_val,unNormData["yval"][0],unNormData["yval"][1])
    
    x_test_1=zscoreNorm_manual(X_test,unNormData["xtest"][0],unNormData["xtest"][1])
    y_test_1=zscoreNorm_manual(Y_test,unNormData["ytest"][0],unNormData["ytest"][1])

    return x_train_1, y_train_1, x_val_1, y_val_1, x_test_1, y_test_1

def unNormalize(normddata,meann,stddev):
    # print(meann,stddev)
    orig=normddata*stddev + meann
    return orig


if __name__ == "__main__": 
    verbose = 1
    
    # data prep
    df = dfprep(verbose=verbose)
    X,Y = df2XY(df, windowsize=5)
    X_train, Y_train, X_val, Y_val, X_test, Y_test = splitsy(X,Y)
    
    #training call
    training = False
    x_train_1, y_train_1, x_val_1, y_val_1, x_test_1, y_test_1 = normalizedata(X_train, Y_train, X_val, Y_val, X_test, Y_test)
    if training:
        train(x_train_1, y_train_1, x_val_1, y_val_1, x_test_1, y_test_1,verbose=verbose)
    
    #reload good model  
    results=True
    if results: 
        normed_ytrain=unNormalize(x_train_1,unNormData['ytrain'][0],unNormData['ytrain'][1])
        normed_yval=unNormalize(y_val,unNormData['yval'][0],unNormData['yval'][1])
        normed_ytest=unNormalize(y_test,unNormData['ytest'][0],unNormData['ytest'][1])

        normValPreedict=unNormalize(val_predictions,unNormData['yval'][0],unNormData['yval'][1])
        normTestPredictions=unNormalize(test_predictions,unNormData['ytest'][0],unNormData['ytest'][1])
        normed_futurePrediction=unNormalize(future_predict,unNormData['ytest'][0],unNormData['ytest'][1])
        
        
        
        model1 = load_model('.data/LSTM-model1.keras')    
        train_predictions = model1.predict(x_train_1).flatten()
        if verbose: 
            print(train_predictions.shape)
            print(y_train_1.shape)
        train_results = pd.DataFrame(data={'Predicted Open':train_predictions,'Actual Open': y_train_1})
        
        if verbose: 
            print(train_results)
    
        plt.plot(train_results['Predicted Open'], label='Predicted')
        plt.plot(train_results['Actual Open'], label='Actual')
        plt.show()
        
        val_predictions = model1.predict(x_val_1).flatten()
        val_results = pd.DataFrame(data={'Predicted Open':val_predictions,'Actual Open': y_val_1})
        
        plt.plot(val_results['Predicted Open'], label='Predicted')
        plt.plot(val_results['Actual Open'], label='Actual')
        plt.show()

    