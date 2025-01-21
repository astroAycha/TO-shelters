import pandas as pd
import numpy as np




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

# def create_window_features(data: pd.DataFrame) -> pd.DataFrame:

#     data['Occupancy_rate_last_week_avg'] = data['OCCUPANCY_RATE_BEDS'].shift(1).ewm().mean()

