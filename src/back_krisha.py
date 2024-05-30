import json
import requests
import re
import pandas as pd
from pandas import DataFrame
from math import radians, sin, cos, sqrt, atan2
from openai import OpenAI

from src.plotter import *

client = OpenAI(api_key="sk-proj-o8sVKtk3kiLNjojWw3xzT3BlbkFJBBHS6RyrzXxLeSYR7YnO")
def define_openAI_client_with_key_krisha(key: str) -> None:
    """
        Set the global value of OpenAI client with the passed api key

    Args:
        key (str): two gis key.
    """

    global client  # Use the global keyword to modify the global variable inside the function
    client = OpenAI(api_key=key)

def read_sergek_data() -> DataFrame:
    """
    Read SERGEK's dataset

    Returns:
        DataFrame: DataFrame with the data from SERGEK's dataset
    """
    df = pd.read_csv("./lean_sergek_aq_dataset.csv")

    return df


def make_2gis_request_and_return_object_count(
        apiKey: str,
        lat: float,
        lon: float,
        object_type: str,
        radius: int,
        object_to_search: str
) -> int:
    """
        Return the number of objects found within the radius by 2GIS API
    Args:
        apiKey (str): 2GIS API key
        lat (float): latitude of the location
        lon (float): longitude of the location
        radius (int): radius of the search
        object_to_search (str): object to search
    Returns:
        int: total count of objects found within the radius"""

    location = f"{lon}%2C{lat}"

    if object_type != "":
        params = {
            "key": apiKey,
            "point": location,
            "radius": radius,
            "type": object_type,
            "q": object_to_search
        }
        base_url = f"https://catalog.api.2gis.com/3.0/items?q={object_to_search}&point={location}&radius={radius}&type={object_type}&key={apiKey}"

        try:
            response = requests.get(base_url)
            print(response.status_code)
            if response.status_code == 200:
                response_data = json.loads(response.text)
                if "result" in response_data:
                    if response_data["result"]["total"]:
                        total = response_data["result"]["total"]
                        return total
                    else:
                        total = len(response_data["result"])
                        return total
                else:
                    total = 0
                    return total
            elif response.status_code == 404:
                total = 0
                return total
            elif response.status_code == 403:
                print("Authorization error")
                return None
        except requests.RequestException as e:
            print(f"Request error: {e}")
            return None
    else:
        params = {
            "key": apiKey,
            "point": location,
            "radius": radius,
            "q": object_to_search
        }
        base_url = f"https://catalog.api.2gis.com/3.0/items?q={object_to_search}&point={location}&radius={radius}&key={apiKey}"

        try:
            response = requests.get(base_url)
            print(response.status_code)
            if response.status_code == 200:
                response_data = json.loads(response.text)
                if "result" in response_data:
                    if response_data["result"]["total"]:
                        total = response_data["result"]["total"]
                        return total
                    else:
                        total = len(response_data["result"])
                        return total
                else:
                    total = 0
                    return total
            elif response.status_code == 404:
                total = 0
                return total
            elif response.status_code == 403:
                print("Authorization error")
                return None
        except requests.RequestException as e:
            print(f"Request error: {e}")
            return None

def generate_gpt_apartment_report(air_quality_data: dict) -> str:
    """
    Generate a realestate_report for an apartment based on the air quality data

    Args:
        air_quality_data (dict): dictionary with air quality data

    Returns:
        str: realestate_report generated by GPT-3.5-turbo
        """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Hey! Based on the values of PM2.5, PM10 and CO in the air provide a realestate_report overview of the area of the real estate I am thinking of buying. Also add recommendations on living in the area with polluted air. Write each sentence"
                           "on a new line, and each sentence should be shorter than 7 words, add new lines if the sentence is longer. Don't put periods at the ends of the sentences. "
                           "Provide the answer in the following format and respond in russian language: "
                           "Recommendations are:"
                           "1."
                           "2."
                           "3."
                           "..."
            },
            {
                "role": "user",
                "content": f"PM2.5 value {air_quality_data['pm25']}, PM10 value {air_quality_data['pm10']},"
                           f"CO value: {air_quality_data['co']}"

            }
        ],
        max_tokens=150
    )
    report = response.choices[0].message.content

    return report

def calculate_index(metrics_data: dict) -> dict:
    """
    Calculate the air quality index based on the air quality metrics

    Args:
        metrics_data (dict): dictionary with air quality metrics

    Returns:
        dict: dictionary with air quality index and color"""
    aq_index = 0
    pm25_weight = 0.5
    pm10_weight = 0.3
    co_weight = 0.2

    for key in metrics_data:
        if key == "pm25":
            aq_index = pm25_weight*float(metrics_data[key]) + aq_index
        if key == "pm10":
            aq_index = pm10_weight*float(metrics_data[key]) + aq_index
        if key == "co":
            aq_index = co_weight*float(metrics_data[key]) + aq_index

    color = ""
    color_pm25 = ""
    color_pm10 = ""
    color_co = ""

    if aq_index >= 100:
        color = [255, 119, 0]
    if aq_index >= 85:
        color = [255, 189, 55]
    if aq_index >= 45 and aq_index < 85:
        color = [255, 224, 18]
    if aq_index < 30:
        color = [67, 166, 0]
    if aq_index >= 30 and aq_index < 45:
        color = [161, 219, 0]

    if float(metrics_data["pm25"]) >= 100:
        color_pm25 = [255, 119, 0]
    if float(metrics_data["pm25"]) >= 85:
        color_pm25 = [255, 189, 55]
    if float(metrics_data["pm25"]) >= 45 and float(metrics_data["pm25"]) < 85:
        color_pm25 = [255, 224, 18]
    if float(metrics_data["pm25"]) < 30:
        color_pm25 = [67, 166, 0]
    if float(metrics_data["pm25"]) >= 30 and float(metrics_data["pm25"]) < 45:
        color_pm25 = [161, 219, 0]

    if float(metrics_data["pm10"]) >= 100:
        color_pm10 = [255, 119, 0]
    if float(metrics_data["pm10"]) >= 85:
        color_pm10 = [255, 189, 55]
    if float(metrics_data["pm10"]) >= 45 and aq_index < 85:
        color_pm10 = [255, 224, 18]
    if float(metrics_data["pm10"]) < 30:
        color_pm10 = [67, 166, 0]
    if float(metrics_data["pm10"]) >= 30 and float(metrics_data["pm10"]) < 45:
        color_pm10 = [161, 219, 0]

    if float(metrics_data["co"]) >= 100:
        color_co = [255, 119, 0]
    if float(metrics_data["co"]) >= 85:
        color_co = [255, 189, 55]
    if float(metrics_data["co"]) >= 45 and aq_index < 85:
        color_co = [255, 224, 18]
    if float(metrics_data["co"]) < 30:
        color_co = [67, 166, 0]
    if float(metrics_data["co"]) >= 30 and float(metrics_data["co"]) < 45:
        color_co = [161, 219, 0]

    index_color_data = {
        "aq_index_numeric": int(aq_index),
        "aq_index_color": color,
        "color_pm25": color_pm25,
        "color_pm10": color_pm10,
        "color_co": color_co
    }

    return index_color_data


def calculate_haversine(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    Args:
        lat1 (float): latitude of the first point
        lon1 (float): longitude of the first point
        lat2 (float): latitude of the second point
        lon2 (float): longitude of the second point

    Returns:
        float: distance between two points in kilometers"""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance_to_closest_sensor = 6371 * c

    return distance_to_closest_sensor


def find_closest_sensor(
    sensor_locations: DataFrame,
    apartment_location: dict
) -> dict:
    """
    Find the closest sensor to the apartment

    Args:
        sensor_locations (DataFrame): DataFrame with sensor locations
        apartment_location (dict): dictionary with apartment location

    Returns:
        dict: dictionary with the closest sensor location"""
    closest_sensor = None
    min_distance_from_sensor_to_apartment = float('inf')

    for _, sensor_location in sensor_locations.iterrows():
        distance = calculate_haversine(
            float(apartment_location['Latitude']),
            float(apartment_location['Longitude']),
            float(sensor_location['Latitude']),
            float(sensor_location['Longtitude']))
        if distance < min_distance_from_sensor_to_apartment:
            min_distance_from_sensor_to_apartment = distance
            closest_sensor = sensor_location

    return closest_sensor


def read_local_apartment_page(filepath: str) -> dict:
    """
    Read the HTML file with the apartment data

    Args:
        filepath (str): path to the HTML file

    Returns:
        dict: dictionary with the apartment data"""

    apartment_info = {
        "location": None,
        "street": None,
        "floor number": None,
        "area": None,
        "room_type": None,
        "year of construction": None,
    }
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
            print("HTML code read successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

    phys_data = get_phys_data(html_content)
    apartment_info["location"] = get_coordinates(html_content)
    apartment_info["floor number"] = phys_data["floor number"]
    apartment_info["street"] = phys_data["street"]
    apartment_info["area"] = phys_data["area"]
    apartment_info["room_type"] = phys_data["room_type"]
    apartment_info["year of construction"] = phys_data["year of construction"]

    return apartment_info


def download_apartment_webpage(url: str) -> dict:
    """
    Download the HTML file with the apartment data

    Args:
        url (str): URL to the apartment data

    Returns:
        dict: dictionary with the apartment data"""
    realestate_dict = {
        "location": None,
        "street": None,
        "floor number": None,
        "area": None,
        "room_type": None,
        "year of construction": None,
    }

    html_content = ""

    try:
        response = requests.get(url)
        if response.status_code == 200:
            html_content = response.text
        else:
            print(f"Failed to download HTML. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    phys_data = get_phys_data(html_content)
    realestate_dict["location"] = get_coordinates(html_content)
    realestate_dict["floor number"] = phys_data["floor number"]
    realestate_dict["street"] = phys_data["street"]
    realestate_dict["area"] = phys_data["area"]
    realestate_dict["room_type"] = phys_data["room_type"]
    realestate_dict["year of construction"] = phys_data["year of construction"]

    return realestate_dict


def get_phys_data(apartment_html_data: str) -> dict:
    """
    Get the physical data of the apartment

    Args:
        apartment_html_data (str): HTML content of the apartment data

    Returns:
        dict: dictionary with the physical data of the apartment
        """
    room_data_pattern = r'(\d+-комнатная квартира), (\d+ м²), (\d+/\d+ этаж), ([^,]+) за'
    construction_date_pattern = r'<div class="offer__info-item" data-name="house.year">.*?<div class="offer__advert-short-info">(\d+)</div>'
    phys_data_dict = {
        "street": None,
        "floor number": None,
        "year of construction": None,
        "area": None,
        "room_type": None
    }

    match = re.search(
        construction_date_pattern, apartment_html_data, re.DOTALL)
    if match:
        year = match.group(1)
        phys_data_dict["year of construction"] = year
    else:
        print("Year data not found.")
    match = re.search(room_data_pattern, apartment_html_data)
    if match:
        room_type = match.group(1)
        area = match.group(2)
        floor = match.group(3)
        street = match.group(4)
        phys_data_dict["street"] = street
        phys_data_dict["floor number"] = floor
        phys_data_dict["area"] = area
        phys_data_dict["room_type"] = room_type
    else:
        print("Data not found.")

    return phys_data_dict


def get_coordinates(apartment_data: str) -> str:
    """
    Get the coordinates of the apartment

    Args:
        apartment_data (str): HTML content of the apartment data

    Returns:
        str: coordinates of the apartment"""
    pattern = r'"lat":(-?\d+\.\d+),"lon":(-?\d+\.\d+)'
    match = re.search(pattern, apartment_data)
    if match:
        lat = float(match.group(1))
        lon = float(match.group(2))
        lat_lon_combined = f"{lat},{lon}"
        return lat_lon_combined

    return "Coordinates were not found."


def get_sensor_location_id_from_manual_input(location: str) -> int:
    """
    Get the location ID of the closest sensor to the provided location

    Args:
        location (str): latitude and longitude of the provided location

    Returns:
        int: location ID of the closest sensor"""
    sensor_dataframe = read_sergek_data()
    sensor_locations_df = pd.DataFrame(sensor_dataframe)
    sensor_locations_df = sensor_locations_df.drop(
        sensor_locations_df.index[0])

    provided_location = location
    latitude, longitude = map(float, provided_location.split(','))

    provided_location_dict = {
        "Latitude": latitude,
        "Longitude": longitude
    }
    closest_sensor = find_closest_sensor(
        sensor_locations_df, provided_location_dict)
    closest_sensor_dict = closest_sensor.to_dict()

    return closest_sensor_dict["location_id"]


def get_sensor_location_id(url: str) -> int:
    """
    Get the location ID of the closest sensor to the provided location

    Args:
        url (str): URL to the apartment data

    Returns:
        int: location ID of the closest sensor"""
    sensor_dataframe = read_sergek_data()
    phys_data = download_apartment_webpage(url)

    sensor_locations_df = pd.DataFrame(sensor_dataframe)
    sensor_locations_df = sensor_locations_df.drop(
        sensor_locations_df.index[0])
    provided_location = phys_data["location"]
    latitude, longitude = map(float, provided_location.split(','))
    provided_location_dict = {
        "Latitude": latitude,
        "Longitude": longitude
    }
    closest_sensor = find_closest_sensor(
        sensor_locations_df, provided_location_dict)
    closest_sensor_dict = closest_sensor.to_dict()

    return closest_sensor_dict["location_id"]


def create_apartment_report_from_manual_input(apartment_location: str) -> str:
    """
    Create a realestate_report for an apartment based on the air quality data and the coordinates

    Args:
        apartment_location (str): lat and long of the apartment location

    Returns:
        str: path to the generated realestate_report"""

    sensor_dataframe = read_sergek_data()
    sensor_locations_df = pd.DataFrame(sensor_dataframe)
    sensor_locations_df = sensor_locations_df.drop(
        sensor_locations_df.index[0])
    provided_location = apartment_location
    latitude, longitude = map(float, provided_location.split(','))
    provided_location_dict = {
        "Latitude": latitude,
        "Longitude": longitude
    }
    closest_sensor = find_closest_sensor(
        sensor_locations_df, provided_location_dict)
    closest_sensor_dict = closest_sensor.to_dict()

    data_processed = calculate_index(closest_sensor_dict)
    aq_metrics_for_gpt_report = {
        "pm25": closest_sensor_dict['pm25'],
        "pm10": closest_sensor_dict['pm10'],
        "co": closest_sensor_dict['co']
    }
    print(closest_sensor_dict)
    data_processed.update({'latitude': closest_sensor_dict['Latitude']})
    data_processed.update({'longitude': closest_sensor_dict['Longitude']})
    data_processed.update({'pm25': int(float(closest_sensor_dict['pm25']))})
    data_processed.update({'pm10': int(float(closest_sensor_dict['pm10']))})
    data_processed.update({'co': int(float(closest_sensor_dict['co']))})
    data_processed.update(
        {"realestate_report": generate_gpt_apartment_report(
            aq_metrics_for_gpt_report)})

    path_to_report = generate_report_for_an_apartment(
        data_processed['latitude'],
        data_processed['longitude'],
        int(data_processed["aq_index_numeric"]),
        data_processed["aq_index_color"],
        data_processed["color_pm25"],
        data_processed["color_pm10"],
        data_processed["color_co"],
        data_processed["pm25"],
        data_processed["pm10"],
        data_processed["co"],
        data_processed["realestate_report"])

    return path_to_report

def access_metrics(coords: dict) -> dict:

    sensor_dataframe = read_sergek_data()
    sensor_locations_df = pd.DataFrame(sensor_dataframe)
    sensor_locations_df = sensor_locations_df.drop(sensor_locations_df.index[0])

    closest_sensor = find_closest_sensor(sensor_locations_df, coords)

    closest_sensor_dict = closest_sensor.to_dict()


    calculated_index_dict = calculate_index(closest_sensor_dict)
    data_processed = {}

    data_processed.update({'pm25': int(float(closest_sensor_dict['pm25']))})
    data_processed.update({'pm10': int(float(closest_sensor_dict['pm10']))})
    data_processed.update({'co': int(float(closest_sensor_dict['co']))})
    data_processed.update({"aq_index_numeric": int(calculated_index_dict["aq_index_numeric"])})
    data_processed.update({"aq_index_color": calculated_index_dict["aq_index_color"]})
    data_processed.update({"color_pm25": calculated_index_dict["color_pm25"]})
    data_processed.update({"color_pm10": calculated_index_dict["color_pm10"]})
    data_processed.update({"color_co": calculated_index_dict["color_co"]})

    return data_processed

def create_apartment_report_from_link(url: str) -> str:
    """
        Create a realestate_report for an apartment based on the air quality data and the html code
        of the apartment listing

        Args:
            apartment_location (str): lat and long of the apartment location

        Returns:
            str: path to the generated realestate_report"""
    sensor_dataframe = read_sergek_data()
    phys_data = download_apartment_webpage(url)

    sensor_locations_df = pd.DataFrame(sensor_dataframe)
    sensor_locations_df = sensor_locations_df.drop(
        sensor_locations_df.index[0])
    provided_location = phys_data["location"]
    latitude, longitude = map(float, provided_location.split(','))
    provided_location_dict = {
        "Latitude": latitude,
        "Longitude": longitude
    }
    closest_sensor = find_closest_sensor(
        sensor_locations_df, provided_location_dict)
    closest_sensor_dict = closest_sensor.to_dict()

    data_processed = calculate_index(closest_sensor_dict)
    aq_metrics_for_gpt_report = {
        "pm25": closest_sensor_dict['pm25'],
        "pm10": closest_sensor_dict['pm10'],
        "co": closest_sensor_dict['co']
    }
    data_processed.update({'latitude': closest_sensor_dict['Latitude']})
    data_processed.update({'longitude': closest_sensor_dict['Longitude']})
    data_processed.update({'pm25': int(float(closest_sensor_dict['pm25']))})
    data_processed.update({'pm10': int(float(closest_sensor_dict['pm10']))})
    data_processed.update({'co': int(float(closest_sensor_dict['co']))})
    data_processed.update(
        {"realestate_report": generate_gpt_apartment_report(
            aq_metrics_for_gpt_report)})
    path_to_report = generate_report_for_an_apartment(
        data_processed['latitude'],
        data_processed['longitude'],
        int(data_processed["aq_index_numeric"]),
        data_processed["aq_index_color"],
        data_processed["color_pm25"],
        data_processed["color_pm10"],
        data_processed["color_co"],
        data_processed["pm25"],
        data_processed["pm10"],
        data_processed["co"],
        data_processed["realestate_report"])

    return path_to_report


def test_local_file_generation() -> str:
    """
        Create a realestate_report for an apartment based on the air quality data and the local html code of
        apartment listing


        Returns:
    str: path to the generated realestate_report
    """
    sensor_dataframe = read_sergek_data()
    phys_data = read_local_apartment_page(
        "../assets/html_testing_files/apartment.txt")
    sensor_locations_df = pd.DataFrame(sensor_dataframe)
    sensor_locations_df = sensor_locations_df.drop(
        sensor_locations_df.index[0])
    provided_location = phys_data["location"]
    latitude, longitude = map(float, provided_location.split(','))
    provided_location_dict = {
        "Latitude": latitude,
        "Longitude": longitude
    }

    closest_sensor = find_closest_sensor(
        sensor_locations_df, provided_location_dict)
    closest_sensor_dict = closest_sensor.to_dict()
    data_processed = calculate_index(closest_sensor_dict)

    aq_metrics_for_gpt_report = {
        "pm25": int(float(closest_sensor_dict['pm25'])),
        "pm10": int(float(closest_sensor_dict['pm10'])),
        "co": int(float(closest_sensor_dict['co']))
    }
    data_processed.update({'pm25': int(float(closest_sensor_dict['pm25']))})
    data_processed.update({'pm10': int(float(closest_sensor_dict['pm10']))})
    data_processed.update({'co': int(float(closest_sensor_dict['co']))})
    data_processed.update(
        {"realestate_report": generate_gpt_apartment_report(
            aq_metrics_for_gpt_report)})
    path_to_report = generate_report_for_an_apartment(
        int(data_processed["aq_index_numeric"]),
        data_processed["aq_index_color"],
        data_processed["color_pm25"],
        data_processed["color_pm10"],
        data_processed["color_co"],
        data_processed["pm25"],
        data_processed["pm10"],
        data_processed["co"],
        data_processed["realestate_report"])

    return path_to_report


