import pandas as pd
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler,OneHotEncoder

from get_data import get_all_data_from_BQ

# Function to apply cyclical encoding
def apply_cyclical_encoding(X):
    X = X.copy()
    X['datetime'] = pd.to_datetime(X['datetime'])
    X['month_cos'] = np.cos(2 * np.pi * X['datetime'].dt.month / 12)
    X['month_sin'] = np.sin(2 * np.pi * X['datetime'].dt.month / 12)
    X['day_cos'] = np.cos(2 * np.pi * X['datetime'].dt.day / 31)
    X['day_sin'] = np.sin(2 * np.pi * X['datetime'].dt.day / 31)
    X['hour_cos'] = np.cos(2 * np.pi * X['datetime'].dt.hour / 24)
    X['hour_sin'] = np.sin(2 * np.pi * X['datetime'].dt.hour / 24)
    X.drop(columns=['datetime'], inplace=True)
    return X

def preprocessing_pipeline(X):
    # Define the list of categorical and numerical features
    categorical_features = ["stationCode"]
    numerical_features=['numDocksAvailable', 'lon', 'lat', 'precipitation',
        'rain', 'visibility', 'snowfall', 'temperature', 'windspeed', 'is_day',
        'humidity', 'snow_depth', 'month_cos', 'month_sin', 'day_cos',
        'day_sin', 'hour_cos', 'hour_sin']

    # Create the pipeline
    pipeline = Pipeline([
        ("preprocessor", ColumnTransformer([
            ("num", StandardScaler(), numerical_features),
            ("cat", OneHotEncoder(), categorical_features)
        ], remainder="passthrough"))
    ])
    
    pipeline.fit(X)
    
    return pipeline

def preprocessing(X):
    X_preprocessed = apply_cyclical_encoding(X)
    pipeline = preprocessing_pipeline(X_preprocessed)
    X_preprocessed = pipeline.transform(X_preprocessed)
    return X_preprocessed


stations_df = get_all_data_from_BQ("lime_stations_topic")
weather_df = get_all_data_from_BQ("weather_topic")