import numpy as np
import keras
import keras.backend as K
from keras.layers.core import Activation
from keras.models import Sequential,load_model
import pandas as pd
import matplotlib.pyplot as plt
import math
#matplotlib inline
from keras.layers import Conv1D, BatchNormalization,\
Dropout, Dense, InputLayer, Flatten, MaxPool1D, Activation, GlobalAveragePooling1D
import os

from keras import Sequential



from sklearn.preprocessing import MinMaxScaler


# Setting seed for reproducibility
np.random.seed(1234)
PYTHONHASHSEED = 0

# define path to save model
model_path = '../../Output/Google_regression_CNN_w.h5'

stock_data = pd.read_csv("../../Dataset/Google_test.csv",dtype={'Close': 'float64', 'Volume': 'int64','Open': 'float64','High': 'float64', 'Low': 'float64'})
print(stock_data.head(2))
stock_data.info()

stock_true = pd.read_csv("../../Dataset/Google_train.csv",dtype={'Close': 'float64', 'Volume': 'int64','Open': 'float64','High': 'float64', 'Low': 'float64'})

stock_data.columns = ['date', 'close/last', 'volume', 'open', 'high', 'low']

stock_data.info()

stock_data['average'] = (stock_data['high'] + stock_data['low'])/2

stock_data.info()
print(stock_data.head(2))

stock_true.columns = ['date', 'close/last', 'volume', 'open', 'high', 'low']


stock_true['average'] = (stock_true['high'] + stock_true['low'])/2

input_feature= stock_data.iloc[:,[2,6]].values
input_data = input_feature

input_feature1= stock_true.iloc[:,[2,6]].values
input_data1 = input_feature1

#minMax
sc= MinMaxScaler(feature_range=(0,1))
input_data[:,0:2] = sc.fit_transform(input_feature[:,:])

cs= MinMaxScaler(feature_range=(0,1))
input_data1[:,0:2] = cs.fit_transform(input_feature1[:,:])

lookback = 60

test_size = int(.3 * len(stock_data))
X = []
y = []
for i in range(len(stock_data) - lookback - 1):
    t = []
    for j in range(0, lookback):
        t.append(input_data[[(i + j)], :])
    X.append(t)
    y.append(input_data[i + lookback, 1])


X, y= np.array(X), np.array(y)
X_test = X[:test_size+lookback]

X = X.reshape(X.shape[0],lookback, 2)
X_test = X_test.reshape(X_test.shape[0],lookback, 2)
print(X.shape)
print(X_test.shape)


def rmse(y_true, y_pred):
    return K.sqrt(K.mean(K.square(y_pred - y_true), axis=-1))

cnn = Sequential()
cnn.add(InputLayer(input_shape=(X.shape[1], 2)))
cnn.add(BatchNormalization(axis=-1))  #Scaling the data

cnn.add(Conv1D(filters=60,
               kernel_size=3,
               padding="valid",
               activation="relu")
       )
# cnn.add(MaxPool1D(pool_size=2))
# cnn.add(BatchNormalization(axis=-1))
cnn.add(Conv1D(filters=60,
               kernel_size=3,
               padding="valid",
               activation="relu")
       )

cnn.add(Conv1D(filters=60,
               kernel_size=3,
               padding="valid",
               activation="relu")
       )
# cnn.add(BatchNormalization(axis=-1))
# cnn.add(MaxPool1D(pool_size=2))
# cnn.add(BatchNormalization(axis=-1))


cnn.add(Flatten())
cnn.add(Dense(50, activation='relu'))
cnn.add(Dense(units=1))
cnn.add(Activation("relu"))

cnn.compile(optimizer='adam', loss='mean_squared_error',metrics=[rmse])

# if best iteration's model was saved then load and use it
if os.path.isfile(model_path):
    cnn.load_weights(model_path)


    # test metrics
    scores = cnn.evaluate(X_test, input_data1[lookback:test_size + (2 * lookback),1], verbose=1, batch_size=200)
    print('\nRMSE: {}'.format(scores[1]))

    predicted_value = cnn.predict(X_test,verbose=1, batch_size=200)
    print('\nRMSE: {}'.format(predicted_value[1]))

    df = pd.DataFrame(predicted_value)
    df1 = pd.DataFrame(input_data1[lookback:test_size + (2 * lookback), 1])

    ## save to xlsx file

    filepath1 = '../../Output/Google_GRU_BIM_predicted_file.csv'
    filepath2 = '../../Output/Google_CNN_true_file.csv'

    df.to_csv(filepath1, index=False)
    df1.to_csv(filepath2, index=False)


    #print("Prediction")
    #print(predicted_value);
    #print("Truth")
    #print(input_data[lookback:test_size + (2 * lookback), 1]);

    fig_verify = plt.figure(figsize=(100, 50))
    plt.plot(predicted_value, color='red')
    plt.plot(input_data1[lookback:test_size + (2 * lookback), 1], color='green')
    plt.title("Opening price of stocks sold")
    plt.xlabel("Time (latest-> oldest)")
    plt.ylabel("Stock Opening Price")
    plt.legend(['predicted', 'actual data'], loc='upper left')
    plt.show()
    fig_verify.savefig("../../Output/google_regression_verify.png")
