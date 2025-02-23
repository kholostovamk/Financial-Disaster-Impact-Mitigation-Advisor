import pandas as pd
import requests
import datetime
import numpy as np
from dateutil import parser

NOAA_API_TOKEN = "ONfCCtgGcDlGkiJUxONfdcCBKnzYEqZP"

def get_forecast_zone(latitude, longitude):
    """
    Fetches the forecast zone ID from the NWS API based on latitude and longitude.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.

    Returns:
        str: Forecast Zone ID if found, else None.
    """
    url = f"https://api.weather.gov/points/{latitude},{longitude}"
    headers = {
        "User-Agent": "(myweatherapp.com, contact@myweatherapp.com)",
        "Accept": "application/geo+json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        point_data = response.json()
        forecast_zone = point_data.get("properties", {}).get("forecastZone")
        if forecast_zone:
            print("✅ Forecast Zone ID:", forecast_zone)
            return forecast_zone
        else:
            print("⚠️ Forecast Zone ID not found in the response.")
            return None
    else:
        print("❌ Error fetching point data:", response.status_code, response.text)
        return None


def get_observations(forecast_zone, start, end, limit=10):
    """
    Fetches weather observations for a given forecast zone.

    Args:
        forecast_zone (str): The forecast zone ID from the NWS API.
        start (str): Start date/time in ISO 8601 format (e.g., "2025-02-22T00:00:00Z").
        end (str): End date/time in ISO 8601 format (e.g., "2025-02-22T23:59:59Z").
        limit (int, optional): Number of records to retrieve. Default is 10.

    Returns:
        list: A list of observation data dictionaries.
    """
    if not forecast_zone:
        print("❌ Invalid forecast zone. Cannot fetch observations.")
        return []

    url = f"{forecast_zone}/observations"
    headers = {
        "User-Agent": "(myweatherapp.com, contact@myweatherapp.com)",
        "Accept": "application/geo+json"
    }
    params = {
        "start": start,
        "end": end,
        "limit": limit
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        observations = []
        for feature in data.get("features", []):
            properties = feature.get("properties", {})
            timestamp_str = properties.get("timestamp")
            if timestamp_str:
                dt = parser.isoparse(timestamp_str)
                month = dt.month
                observation_data = {
                    "timestamp": timestamp_str,
                    "month": month,
                    "temperature": properties.get("temperature", {}).get("value"),
                    #"max_temperature": properties.get("maxTemperatureLast24Hours", {}).get("value"),
                    #"min_temperature": properties.get("minTemperatureLast24Hours", {}).get("value"),
                    #"precipitation": properties.get("precipitationLastHour", {}).get("minValue")
                }
                observations.append(observation_data)
        return observations
    else:
        print("❌ Error fetching observations:", response.status_code, response.text)
        return []


def process_and_merge_data():
    """
    Merges two datasets (finaldata.csv and us_county_latlng.csv) based on 'combinedFIPS'.
    Saves the merged dataset as 'merged_data.csv'.
    """
    finaldata = pd.read_csv('finaldata.csv')
    us_county_latng = pd.read_csv('us_county_latlng.csv')

    merged_data = pd.merge(finaldata, us_county_latng, on='combinedFIPS', how='inner')
    print("✅ Merged Data Preview:")
    print(merged_data.head())

    merged_data.to_csv('merged_data.csv', index=False)
    print("✅ Merged dataset saved as 'merged_data.csv'!")

def fetch_noaa_data(dataset_id, fips_code, year, month, datatype_ids, limit=5):
    """
    Fetches historical climate data from NOAA's CDO API for a specific county, year, and month.

    Args:
        dataset_id (str): The dataset ID (e.g., "GSOM" for Global Summary of the Month).
        fips_code (str): The county FIPS code (e.g., "FIPS:37001" for Alamance County, NC).
        year (int): The year (e.g., 2021).
        month (int): The month (1-12).
        datatype_ids (list): List of datatype IDs (e.g., ["PRCP", "AWND", "WSF2"]).
        limit (int, optional): Number of records to fetch (max is 1000).

    Returns:
        pd.DataFrame: A pandas DataFrame containing the filtered historical weather data.
    """

    # Construct start and end date for the given month
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{pd.Period(start_date).days_in_month}"  # Last day of the month

    url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"

    params = {
        "datasetid": dataset_id,  # Required dataset ID
        "locationid": fips_code,  # County FIPS code
        "startdate": start_date,  # Start of the month
        "enddate": end_date,  # End of the month
        "limit": limit,  # Max records per request
        "units": "metric",  # Use metric units
        "datatypeid": datatype_ids  # Request multiple data types
    }

    headers = {"token": NOAA_API_TOKEN}  # API Authentication token

    # Make request to NOAA API
    response = requests.get(url, headers=headers, params=params)

    # Check if response is successful
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])

        # Convert JSON data to Pandas DataFrame
        df = pd.DataFrame(results)

        # Drop 'attributes' column (optional)
        if 'attributes' in df.columns:
            df.drop(columns=['attributes'], inplace=True)
        return df
    else:
        print(f"❌ API Error: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    # HAS TO BE USER INPUT
    latitude = 35.78
    longitude = -78.64

    # Get Forecast Zone ID
    forecast_zone = get_forecast_zone(latitude, longitude)

    # Get Weather Observations
    observations1 = get_observations(forecast_zone, "2025-02-22T00:00:00Z", "2025-02-22T23:59:59Z", limit=1)

    # INPUTS TO MODEL
    if observations1:
        for obs in observations1:
            timestamp = obs.get("timestamp", "N/A")  # Get timestamp (default "N/A" if missing)
            month = obs.get("month", None)  # Get month
            temperature = obs.get("temperature", None)  # Get temperature
            
            print(f"Timestamp: {timestamp}, Month: {month}, Temperature: {temperature}")


    month = 1 #HAS TO BE INPUT OR DETECTED. MONTH HAS TO BE CURRENT MONTH - 1
    year = 2025 #HAS TO BE INPUT OR DETECTED
    dataset_id = "GSOM"
    fips_code = "FIPS:37001" #HAS TO BE INPUT
    datatype_id = "PRCP"
    observations2 = fetch_noaa_data(dataset_id, fips_code, year, month, datatype_id, limit=1)
    precipitation = observations2["value"].iloc[0]*0.0393701
    print(precipitation)  #INPUT VARIABLE TO MODEL. CONVERTED FROM mm -> inches



    #INPUTS TO MODEL
    #1 temperature - FOUND
    #2 precipitation - FOUND
    #3 month - USE THE ONE DETECTED
    #4 year - USE THE ONE DETECTED
    #5 latitude - INPUT
    #6 longitude - INPUT
    #7 fips - INPUT / DETECTED

