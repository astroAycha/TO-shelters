import pandas as pd


def split_train_test_by_date(data_df: pd.DataFrame,
                    split_date: str) -> (pd.DataFrame, pd.DataFrame):

    # keep only those weather features:
    weather_features = ["temperature_2m_max", "temperature_2m_min", 
                    "apparent_temperature_max", "apparent_temperature_min", 
                    "sunrise", "sunset", "sunshine_duration", 
                    "precipitation_sum", "rain_sum", "snowfall_sum", 
                    "precipitation_hours", 
                    "wind_speed_10m_max", "wind_gusts_10m_max"
                    ]
    # weather_data = weather_data[weather_features+['OCCUPANCY_DATE']]

    # split into train and test data
    train_date_filter = data_df['OCCUPANCY_DATE'] < split_date
    test_date_filter = data_df['OCCUPANCY_DATE'] >= split_date

    train_data = data_df[['OCCUPANCY_DATE', 'OCCUPANCY_RATE_BEDS']+weather_features][train_date_filter]
    test_data = data_df[['OCCUPANCY_DATE', 'OCCUPANCY_RATE_BEDS']+weather_features][test_date_filter]


    return train_data, test_data