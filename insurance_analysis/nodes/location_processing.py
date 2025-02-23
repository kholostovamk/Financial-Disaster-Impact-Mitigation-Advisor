import requests
from config import API_URL
from model.predict_model import predict_disaster_prob

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
    latitude, longitude = state["location"]["latitude"], state["location"]["longitude"]
    fips = state["fips"]
    disaster_probability = predict_disaster_prob(fips, 1.19, 69.4, 44.3, 56.8, 5, 2023, latitude, longitude)
    
    
    return {"disaster_probability": disaster_probability}
