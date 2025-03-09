import requests
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta

import openmeteo_requests
import requests_cache
from retry_requests import retry

import logging

logging.basicConfig(filename='shelter_data.log', level=logging.INFO)



def download_hist_shelter_capacity_data():

    base_url = 'https://ckan0.cf.opendata.inter.prod-toronto.ca/datastore/dump/'

    hist_data_code = {'2021': "da8854b8-e570-4de2-b051-a906b62fe7f8",
                      '2022': "1cc46acb-c6d3-4537-93ef-3ebad039275c",
                      '2023':"62786156-b463-4c04-b286-c23f32c726ab",
                      '2024': "fc409fd7-0348-49d7-bba9-70ac1a8c727c"}

    today = datetime.today()
    for year, url in hist_data_code.items():
        file_url = base_url + url
        response = requests.get(file_url)

        if response.status_code == 200:
            file_name = f"./data/shelter_capacity_{year}.csv"

            with open(file_name, "wb") as file:
                file.write(response.content)

            logging.info(f"File downloaded successfully and saved as {file_name} on {today}")
        else:
            logging.info(f"Failed to download the file on {today}. Status code: {response.status_code}")

    return


def update_shelter_data():

    """
    obtain the shelter data and update for the current week
    # TO DO: automate to run on a weekly schedule
    """

    # The URL of the file you want to download
    base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca/datastore/dump/"
    file_url = base_url + "42714176-4f05-44e6-b157-2b57f29b856a"

    # Send a GET request to the URL
    response = requests.get(file_url)

    today = datetime.today()
    # Check if the request was successful
    if response.status_code == 200:
        # Specify the filename you want to save the file as
        file_name = "./data/shelter_capacity_2025.csv"
        
        # Open a local file and write the content to it
        with open(file_name, "wb") as file:
            file.write(response.content)
        
        logging.info(f"File downloaded successfully and saved as {file_name} on {today}")
    else:
        logging.info(f"Failed to download the file on {today}. Status code: {response.status_code}")

    return


def weather_dataframe(url, params):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()

    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
    daily_apparent_temperature_max = daily.Variables(2).ValuesAsNumpy()
    daily_apparent_temperature_min = daily.Variables(3).ValuesAsNumpy()
    daily_sunrise = daily.Variables(4).ValuesAsNumpy()
    daily_sunset = daily.Variables(5).ValuesAsNumpy()
    daily_sunshine_duration = daily.Variables(6).ValuesAsNumpy()
    daily_precipitation_sum = daily.Variables(7).ValuesAsNumpy()
    daily_rain_sum = daily.Variables(8).ValuesAsNumpy()
    daily_snowfall_sum = daily.Variables(9).ValuesAsNumpy()
    daily_precipitation_hours = daily.Variables(10).ValuesAsNumpy()
    daily_wind_speed_10m_max = daily.Variables(11).ValuesAsNumpy()
    daily_wind_gusts_10m_max = daily.Variables(12).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left")
        }
    
    daily_data["temperature_2m_max"] = daily_temperature_2m_max
    daily_data["temperature_2m_min"] = daily_temperature_2m_min
    daily_data["apparent_temperature_max"] = daily_apparent_temperature_max
    daily_data["apparent_temperature_min"] = daily_apparent_temperature_min
    daily_data["sunrise"] = daily_sunrise
    daily_data["sunset"] = daily_sunset
    daily_data["sunshine_duration"] = daily_sunshine_duration
    daily_data["precipitation_sum"] = daily_precipitation_sum
    daily_data["rain_sum"] = daily_rain_sum
    daily_data["snowfall_sum"] = daily_snowfall_sum
    daily_data["precipitation_hours"] = daily_precipitation_hours
    daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
    daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max

    daily_dataframe = pd.DataFrame(data = daily_data)

    return daily_dataframe


def get_weather_data(start_date: str,
                     end_date: str) -> pd.DataFrame:

    '''
    get historic weather data and forecast data
    '''
    daily_params = ["temperature_2m_max", "temperature_2m_min", 
                    "apparent_temperature_max", "apparent_temperature_min", 
                    "sunrise", "sunset", "sunshine_duration", 
                    "precipitation_sum", "rain_sum", "snowfall_sum", 
                    "precipitation_hours", 
                    "wind_speed_10m_max", "wind_gusts_10m_max"
                    ]
    
    toronto_latitude = 43.7001
    toronto_longitude = -79.4163

    logging.info(f"weather data for Toronto between {start_date} and {end_date}")

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    hist_url = "https://archive-api.open-meteo.com/v1/archive"
    hist_params = {
        "latitude": toronto_latitude,
        "longitude": toronto_longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": daily_params,
        "timezone": "America/New_York"
    }
    hist_dataframe = weather_dataframe(hist_url, hist_params)
    logging.info(f"historic weather dataframe has size {hist_dataframe.shape}")
    
    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    forecast_url = "https://api.open-meteo.com/v1/forecast"
    forecast_params = {
        "latitude": toronto_latitude,
        "longitude": toronto_longitude,
        "daily": daily_params,
        "timezone": "America/New_York",
        "past_days":0,
        "forecast_days": 7
    }
    forecast_dataframe = weather_dataframe(forecast_url, forecast_params)
    logging.info(f"weather forecast dataframe has size {forecast_dataframe.shape}")
    # logging.info("CHECKING WHY THIS IS NOT UPDATING")
    logging.info(f"weather forecast dates: {forecast_dataframe['date'].min()} {forecast_dataframe['date'].max()}")

    daily_weather_dataframe = pd.concat([hist_dataframe, forecast_dataframe], 
                                        ignore_index=True)
 

    daily_weather_dataframe.to_csv(f"./data/daily_weather_data.csv",
                                   index=False)

    return

def combine_data() -> pd.DataFrame:


    data2022 = pd.read_csv('./data/shelter_capacity_2022.csv',
                           parse_dates=['OCCUPANCY_DATE'],
                           date_format='%y-%m-%d')
    data2022['OCCUPANCY_DATE'] = pd.to_datetime(data2022['OCCUPANCY_DATE']).dt.strftime('%Y-%m-%d')
    data2023 = pd.read_csv('./data/shelter_capacity_2023.csv')
    data2023['OCCUPANCY_DATE'] = pd.to_datetime(data2023['OCCUPANCY_DATE']).dt.strftime('%Y-%m-%d')
    data2024 = pd.read_csv('./data/shelter_capacity_2024.csv')
    data2024['OCCUPANCY_DATE'] = pd.to_datetime(data2024['OCCUPANCY_DATE']).dt.strftime('%Y-%m-%d')
    data2025 = pd.read_csv('./data/shelter_capacity_2025.csv')    
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


    # read weather data for Toronto
    weather_data = pd.read_csv('./data/daily_weather_data.csv')
    print(f">>> weather data size: {weather_data.shape}")
    
    weather_data['OCCUPANCY_DATE'] = pd.to_datetime(weather_data['date']).dt.date.astype('datetime64[ns]')

    full_data = shelter_data.merge(weather_data, on='OCCUPANCY_DATE', how='outer')

    today_date = datetime.today()
    print(f">>> Today is: {today_date}")

    full_data = full_data[
                        # (full_data['OCCUPANCY_DATE'] < today_date) 
                    #   & 
                      (full_data['OCCUPANCY_DATE'] > today_date - timedelta(days=1200))
                      ]

    full_data.to_csv(f"./data/daily-shelter-overnight-capacity.csv",
                   index=False)

    return full_data