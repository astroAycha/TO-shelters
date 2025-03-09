from prefect import flow, task
from get_data import (download_hist_shelter_capacity_data, update_shelter_data, 
                      combine_data, weather_dataframe, get_weather_data)
from preproc import split_train_test, make_datetime_features, agg_by_day
from anomaly_detection import detect_outliers


@flow(log_prints=True)
def forecasting_workflow():
    weather_data = 
    shelter_data = 

    # full data 
    data = combine_data()

    data = make_datetime_features(data)

    data = agg_by_day(data)

    exog_features = [
                'temperature_2m_max', 
                'temperature_2m_min', 
                'weekend', 
                'quarter_x', 'quarter_y'
                ]