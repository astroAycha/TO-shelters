import requests
import pandas as pd
from io import StringIO
from datetime import datetime


def update_shelter_data():

    """
    obtain the shelter data and update for the current week
    # TO DO: automate to run on a weekly schedule
    """

    # -- this part is copied from the data source webpage
    # Toronto Open Data is stored in a CKAN instance. It's APIs are documented here:
    # https://docs.ckan.org/en/latest/api/

    # To hit our API, you'll be making requests to:
    base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca"

    # Datasets are called "packages". Each package can contain many "resources"
    # To retrieve the metadata for this package and its resources, use the package name in this page's URL:
    url = base_url + "/api/3/action/package_show"
    params = { "id": "daily-shelter-overnight-service-occupancy-capacity"}
    package = requests.get(url, params = params).json()

    # To get resource data:
    for idx, resource in enumerate(package["result"]["resources"]):

        # for datastore_active resources:
        if resource["datastore_active"]:

            # To get all records in CSV format:
            url = base_url + "/datastore/dump/" + resource["id"]
            resource_dump_data = requests.get(url).text

    # -- end copied part

    shelter_data = StringIO(resource_dump_data)

    # turn into a pandas dataframe
    data_df = pd.read_csv(shelter_data, sep=",")

    data_df['OCCUPANCY_DATE'] = pd.to_datetime(data_df['OCCUPANCY_DATE'])

    today_date = datetime.today()
    print(today_date)

    data_df = data_df[data_df['OCCUPANCY_DATE'] > today_date]

    data_df.to_csv(f"./data/daily-shelter-overnight-capacity.csv")


    return