import requests
from config import API_URL

def location_input(state: dict) -> dict:
    try:
        latitude, longitude = state["location"]["latitude"], state["location"]["longitude"]
        url = f'{API_URL}?latitude={latitude}&longitude={longitude}&format=json'
        response = requests.get(url)
        data = response.json()
        return {"fips": data['County']['FIPS']}
    except Exception as e:
        return {"fips": 12345}

def disaster_probability_model(state: dict) -> dict:
    return {"disaster_probability": {"earthquake": 0.2, "tornado": 0.3, "floods": 0.5, "fires": 0.7}}
