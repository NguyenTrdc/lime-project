import pandas as pd
import joblib

from preprocessing import preprocessing
from utils import get_data,get_Paris_weather

def predict_current_time():
    paris_weather_rn = get_Paris_weather()
    stations_rn=get_data()
    df_rn = pd.merge(paris_weather_rn,stations_rn,on="time_period")
    
    features=['stationCode','datetime', 'numDocksAvailable', 'lon', 'lat', 'precipitation', 'rain', 'visibility', 'snowfall',
           'temperature', 'windspeed', 'is_day', 'humidity', 'snow_depth']
    target = ['num_bikes_available']
    # Features and target
    X=df_rn[features]
    y=df_rn[target]
    
    X["stationCode"]=X["stationCode"].apply(lambda x : int(x))
    X_preprocessed=preprocessing(X)
    
    model = joblib.load("/home/andre/NguyenTrdc/lime-project/ml_logic/model_save/linear_regression_model.pkl")
    
    y_pred = model.predict(X_preprocessed)
    return y_pred

print(predict_current_time())