import pandas as pd

def combine_data() -> pd.DataFrame:


    # read the shelter data
    data_22 = pd.read_csv('./data/daily-shelter-overnight-service-occupancy-capacity-2022.csv')
    print(data_22.shape)
    data_22['OCCUPANCY_DATE'] = pd.to_datetime(data_22['OCCUPANCY_DATE'], format='%y-%m-%d')

    data_23 = pd.read_csv('./data/daily-shelter-overnight-service-occupancy-capacity-2023.csv')
    print(data_23.shape)
    data_23['OCCUPANCY_DATE'] = pd.to_datetime(data_23['OCCUPANCY_DATE'])

    data_24 = pd.read_csv('./Data/Daily shelter overnight occupancy.csv')
    print(data_24.shape)
    data_24['OCCUPANCY_DATE'] = pd.to_datetime(data_24['OCCUPANCY_DATE'])

    input_data = pd.concat([data_22, data_23, data_24], ignore_index=True)


    # read weather data for Toronto
    weather_22 = pd.read_csv('./data/en_climate_daily_ON_6158355_2022_P1D.csv')
    weather_23 = pd.read_csv('./data/en_climate_daily_ON_6158355_2023_P1D.csv')
    weather_24 = pd.read_csv('./data/en_climate_daily_ON_6158355_2024_P1D.csv')
    weather_data = pd.concat([weather_22, weather_23, weather_24])
    print(f"weather data size: {weather_data.shape}")
    
    weather_data['OCCUPANCY_DATE'] = pd.to_datetime(weather_data['Date/Time'])

    full_data = input_data.merge(weather_data, on='OCCUPANCY_DATE', how='left')

    return full_data



def split_train_test(full_data: pd.DataFrame,
                    city: str = "Toronto") -> (pd.DataFrame, pd.DataFrame):

    # keep only those weather features:
    weather_features = ['Max Temp (°C)', 'Min Temp (°C)', 'Total Precip (mm)']
    # weather_data = weather_data[weather_features+['OCCUPANCY_DATE']]

    # select the city
    city_filter = full_data['LOCATION_CITY'] == city

    # split into train and test data
    train_date_filter = full_data['OCCUPANCY_DATE'] < '2024-01-01'
    test_date_filter = full_data['OCCUPANCY_DATE'] >= '2024-01-01'

    train_data = full_data[['OCCUPANCY_DATE', 'OCCUPANCY_RATE_BEDS']+weather_features][city_filter & train_date_filter]
    test_data = full_data[['OCCUPANCY_DATE', 'OCCUPANCY_RATE_BEDS']+weather_features][city_filter & test_date_filter]


    return train_data, test_data


def make_datetime_features(data: pd.DataFrame) -> pd.DataFrame:

    data['day-of-week'] = data['OCCUPANCY_DATE'].dt.dayofweek
    data['day-of-year'] = data['OCCUPANCY_DATE'].dt.dayofyear
    data['month'] = data['OCCUPANCY_DATE'].dt.month
    data['quarter'] = data['OCCUPANCY_DATE'].dt.quarter
    # data['year'] = data['OCCUPANCY_DATE'].dt.year

    return data


def agg_by_day(data: pd.DataFrame) -> pd.DataFrame:

    data_agg_by_day = data.groupby('OCCUPANCY_DATE').agg({'OCCUPANCY_RATE_BEDS': 'sum',
                                                            'Max Temp (°C)': 'max',
                                                            'Min Temp (°C)': 'min',
                                                            'Total Precip (mm)': 'mean',
                                                            'day-of-week': 'mean',
                                                            'day-of-year': 'mean',
                                                            'month': 'mean',
                                                            'quarter': 'mean',
                                                            # 'year': 'mean'
                                                            })

    return data_agg_by_day
