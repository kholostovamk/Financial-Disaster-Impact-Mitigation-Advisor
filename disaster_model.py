import pandas as pd
import numpy as np
import json
from xgboost import XGBClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split

def train_disaster_model(data_path):
    """
    Trains an XGBoost-based multi-output classification model for predicting disaster probabilities.

    Args:
        data_path (str): Path to the CSV file containing the dataset.

    Returns:
        tuple: (trained model, feature names, prediction function)
    """
    df = pd.read_csv(data_path)

    # One-hot encode the 'incidentType' column
    df = pd.get_dummies(df, columns=['incidentType'])

    X = df[['combinedFIPS', 'Precipitation', 'MaxTemp', 'MinTemp', 'AverageTemp', 'Month', 'year', 'Latitude', 'Longitude']]
    y = df.filter(like='incidentType_')  # Selecting all one-hot encoded incident types
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


    base_model = XGBClassifier(n_estimators=200, learning_rate=0.01, eval_metric='logloss')
    model = MultiOutputClassifier(base_model)
    model.fit(X_train, y_train)
    print("✅ Model training complete!")

    disaster_types = y.columns.tolist()

    def predict_disaster_prob(fips, precip, max_temp, min_temp, avg_temp, month, year, latitude, longitude):
        """Predict probability of each disaster type for a given location."""
        input_data = [[fips, precip, max_temp, min_temp, avg_temp, month, year, latitude, longitude]]

        probs_list = model.predict_proba(input_data)
        #print(probs_list)
        arr = []
        for p in probs_list:
            #print(p[0][1])
            arr.append(p[0][1])

        #print(arr)

        # Disaster types
        disaster_types = [
            "Fire", "Severe Storm", "Flood", "Tornado", "Winter Storm", "Snowstorm",
            "Hurricane", "Tropical Storm", "Coastal Storm", "Other", "Severe Ice Storm",
            "Dam/Levee Break", "Biological", "Volcanic Eruption", "Mud/Landslide", "Earthquake",
            "Terrorist", "Drought", "Toxic Substances", "Fishing Losses", "Human Cause",
            "Tsunami", "Freezing", "Typhoon"
        ]

        disaster_prob = {}
        for key, value in zip(disaster_types, arr):
            disaster_prob[key] = value

        return disaster_prob

    return model, X.columns.tolist(), predict_disaster_prob


# Example usage
if __name__ == "__main__":
    # Train the model and get the prediction function
    model, feature_names, predict_func = train_disaster_model("data.csv")

    # Example prediction
    result = predict_func(35033, 1.19, 69.4, 44.3, 56.8, 5, 2023, -104.944561, 36.00972846)
    print(result)
