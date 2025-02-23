import json
import joblib
import numpy as np

MODEL_FILE = "disaster_model.pkl"
FEATURES_FILE = "feature_names.json"
DISASTER_TYPES_FILE = "disaster_types.json"


# Load the trained model
model = joblib.load(MODEL_FILE)

# Load feature names
with open(FEATURES_FILE, 'r') as f:
    feature_names = json.load(f)

# Disaster types
with open(DISASTER_TYPES_FILE, 'r') as f:
    disaster_types = json.load(f)

def predict_disaster_prob(fips, precip, max_temp, min_temp, avg_temp, month, year, latitude, longitude):
    """
    Predicts the probability of each disaster type for a given input.

    Args:
        fips (int): Combined FIPS code.
        precip (float): Precipitation level.
        max_temp (float): Maximum temperature.
        min_temp (float): Minimum temperature.
        avg_temp (float): Average temperature.
        month (int): Month of occurrence.
        year (int): Year of occurrence.
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.

    Returns:
        dict: Predicted probabilities of disaster types.
    """
    
    
    
    fips = int(fips[5:])
    

    input_data = np.array([[int(fips), float(precip), float(max_temp), float(min_temp), 
                            float(avg_temp), int(month), int(year), float(latitude), float(longitude)]],
                        dtype=np.float32)  # Force float32

        
    print("+="*50)
    
    print(input_data)
    
    
    print("+="*50)

    # Get probabilities from model
    probs_list = model.predict_proba(input_data)
    
    # Extract second column (probability of disaster occurring)
    probs = [p[0][1] for p in probs_list]

    # Map to disaster types
    disaster_prob = dict(zip(disaster_types, probs))
    
    # sort the probabilities in descending order
    disaster_prob = dict(sorted(disaster_prob.items(), key=lambda x: x[1], reverse=True))

    return disaster_prob

# Example usage
if __name__ == "__main__":
    result = predict_disaster_prob(35033, 1.19, 69.4, 44.3, 56.8, 5, 2023, -104.944561, 36.00972846)
    print(result)
