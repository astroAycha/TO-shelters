import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logging.basicConfig(filename='shelter_data.log', level=logging.INFO)




def make_datetime_features(data: pd.DataFrame) -> pd.DataFrame:

    data['day-of-week'] = data['OCCUPANCY_DATE'].dt.dayofweek
    data["weekend"] = data['OCCUPANCY_DATE'].dt.dayofweek.isin([5,6])
    data['day-of-year'] = data['OCCUPANCY_DATE'].dt.dayofyear
    data['month'] = data['OCCUPANCY_DATE'].dt.month
    data['quarter'] = data['OCCUPANCY_DATE'].dt.quarter
    data['year'] = data['OCCUPANCY_DATE'].dt.year

    data["day_x"] = np.sin(np.radians((360/7) * data['day-of-week']))
    data["day_y"] = np.cos(np.radians((360/7) * data['day-of-week']))
    data["month_x"] = np.sin(np.radians((360/12) * data['month']))
    data["month_y"] = np.cos(np.radians((360/12) * data['month']))
    data['quarter_x'] = np.sin(np.radians((360/4) * data['quarter']))
    data['quarter_y'] = np.cos(np.radians((360/4) * data['quarter']))

    return data


def agg_by_day(data: pd.DataFrame) -> pd.DataFrame:

    data_agg_by_day = data.groupby('OCCUPANCY_DATE').agg({'OCCUPANCY_RATE_BEDS': 'sum',
                                                            'temperature_2m_max': 'max',
                                                            'temperature_2m_min': 'min',
                                                            'precipitation_sum': 'sum',
                                                            'rain_sum': 'sum',
                                                            'snowfall_sum': 'sum',
                                                            'wind_speed_10m_max': 'max',
                                                            'sunshine_duration': 'mean',
                                                            # 'day-of-week': 'mean',
                                                            'day_x': 'mean',
                                                            'day_y': 'mean',
                                                            'weekend': 'mean',
                                                            'month_x': 'mean',
                                                            'month_y': 'mean',
                                                            # 'day-of-year': 'mean',
                                                            'quarter_x': 'mean',
                                                            'quarter_y': 'mean',
                                                            'month': 'mean',
                                                            # 'quarter': 'mean',
                                                            'year': 'mean'
                                                            })

    return data_agg_by_day

def create_lag_features(data: pd.DataFrame) -> pd.DataFrame:

    data['temperature_2m_max_prev_day'] = data['temperature_2m_max'].shift(1)
    data['temperature_2m_max_prev_week'] = data['temperature_2m_max'].shift(7)

    data['temperature_2m_min_prev_day'] = data['temperature_2m_min'].shift(1)
    data['temperature_2m_min_prev_week'] = data['temperature_2m_min'].shift(7)

    data['temperature_2m_mean_prev_day'] = data['temperature_2m_mean'].shift(1)
    data['temperature_2m_mean_prev_week'] = data['temperature_2m_mean'].shift(7)

    data['OCCUPANCY_RATE_BEDS_prev_day'] = data['OCCUPANCY_RATE_BEDS'].shift(1)
    data['OCCUPANCY_RATE_BEDS_prev_dweek'] = data['OCCUPANCY_RATE_BEDS'].shift(7)


    return data


def combine_data(data_path: str) -> pd.DataFrame:


    data2022 = pd.read_csv(f"{data_path}shelter_capacity_2022.csv",
                           parse_dates=['OCCUPANCY_DATE'],
                           date_format='%y-%m-%d')
    data2022['OCCUPANCY_DATE'] = pd.to_datetime(data2022['OCCUPANCY_DATE']).dt.strftime('%Y-%m-%d')
    data2023 = pd.read_csv(f"{data_path}shelter_capacity_2023.csv")
    data2023['OCCUPANCY_DATE'] = pd.to_datetime(data2023['OCCUPANCY_DATE']).dt.strftime('%Y-%m-%d')
    data2024 = pd.read_csv(f"{data_path}shelter_capacity_2024.csv")
    data2024['OCCUPANCY_DATE'] = pd.to_datetime(data2024['OCCUPANCY_DATE']).dt.strftime('%Y-%m-%d')
    data2025 = pd.read_csv(f"{data_path}shelter_capacity_2025.csv")    
    data2025['OCCUPANCY_DATE'] = pd.to_datetime(data2025['OCCUPANCY_DATE']).dt.strftime('%Y-%m-%d')



    # first stack the shelter data
    shelter_capacity_data = pd.concat([data2022, data2023, data2024, data2025],
                                      ignore_index=True)

    packed_shelter_data = shelter_capacity_data.groupby(['SHELTER_ID', 
                                                     'LOCATION_ID',
                                                     'ORGANIZATION_NAME',
                                                     'SHELTER_GROUP',
                                                     'LOCATION_NAME',
                                                     'OCCUPANCY_DATE']).agg({'OCCUPANCY_RATE_BEDS': 'mean'})
    
    shelter_data = packed_shelter_data.reset_index()

    shelter_data['OCCUPANCY_DATE'] = pd.to_datetime(shelter_data['OCCUPANCY_DATE'],
                                                    format='mixed')


    # add rows for an additional week for forecasting:
    start = shelter_data['OCCUPANCY_DATE'].max().date() 
    end = start + pd.Timedelta(7, 'D')
    logging.info(f"adding rows for dates: {start}", f"\n end date: {end}")

    new_week_dates = pd.date_range(start, end, freq='D')
    new_week = pd.DataFrame(columns=shelter_data.columns)

    new_week['OCCUPANCY_DATE'] = new_week_dates

    # stack new week on the shelter data frame:
    shelter_data_extended = pd.concat([shelter_data, new_week])

    # read weather data for Toronto
    weather_data = pd.read_csv(f"{data_path}daily_weather_data.csv")
    print(f">>> weather data size: {weather_data.shape}")
    
    weather_data['OCCUPANCY_DATE'] = pd.to_datetime(weather_data['date']).dt.date.astype('datetime64[ns]')

    full_data = shelter_data_extended.merge(weather_data, on='OCCUPANCY_DATE', how='left')

    today_date = datetime.today()
    print(f">>> Today is: {today_date}")

    full_data = full_data[
                        # (full_data['OCCUPANCY_DATE'] < today_date) 
                    #   & 
                      (full_data['OCCUPANCY_DATE'] > today_date - timedelta(days=1200))
                      ]

    full_data.to_csv(f"{data_path}daily-shelter-overnight-capacity.csv",
                   index=False)

    # return full_data

# def create_window_features(data: pd.DataFrame) -> pd.DataFrame:

#     data['Occupancy_rate_last_week_avg'] = data['OCCUPANCY_RATE_BEDS'].shift(1).ewm().mean()

