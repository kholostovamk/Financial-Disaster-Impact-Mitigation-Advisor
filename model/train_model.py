import pandas as pd
import numpy as np
import json
import joblib
from xgboost import XGBClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split

MODEL_FILE = "disaster_model.pkl"
FEATURES_FILE = "feature_names.json"
DISASTER_TYPES_FILE = "disaster_types.json"

def train_disaster_model(data_path):
    """
    Trains an XGBoost-based multi-output classification model and saves it.

    Args:
        data_path (str): Path to the CSV file containing the dataset.
    """
    df = pd.read_csv(data_path)

    df = pd.get_dummies(df, columns=['incidentType'])

    X = df[['combinedFIPS', 'Precipitation', 'AverageTemp', 'Month', 'year', 'Latitude', 'Longitude']]
    y = df.filter(like='incidentType_')  # Selecting all one-hot encoded incident types
    y = y.drop(columns=['incidentType_Volcanic Eruption', 
                    'incidentType_Terrorist', 
                    'incidentType_Fishing Losses', "incidentType_Dam/Levee Break"], errors='ignore')
    
    y['incidentType_Storm'] = (y['incidentType_Severe Storm'] + 
                           y['incidentType_Winter Storm'] + 
                           y['incidentType_Snowstorm'] + 
                           y['incidentType_Tropical Storm'] + 
                           y['incidentType_Severe Ice Storm'] + 
                           y['incidentType_Coastal Storm'])
    
    y['incidentType_Tornado'] = (y['incidentType_Tornado'] + 
                           y['incidentType_Hurricane'] + 
                           y['incidentType_Typhoon'])


    # Drop the original individual storm-related columns
    y = y.drop(columns=['incidentType_Severe Storm', 
                        'incidentType_Winter Storm', 
                        'incidentType_Snowstorm', 
                        'incidentType_Tropical Storm', 
                        'incidentType_Severe Ice Storm', 
                        'incidentType_Coastal Storm', 'incidentType_Hurricane', 'incidentType_Typhoon'], errors='ignore')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    disaster_types = list(coloum.replace('incidentType_', '') for coloum in y.columns)

    

    base_model = XGBClassifier(n_estimators=200, learning_rate=0.01, eval_metric='logloss')
    model = MultiOutputClassifier(base_model)
    model.fit(X_train, y_train)

    print("✅ Model training complete! Saving model...")

    # Save the trained model
    joblib.dump(model, MODEL_FILE)

    # Save feature names
    feature_names = X.columns.tolist()
    with open(FEATURES_FILE, 'w') as f:
        json.dump(feature_names, f)
        
    # Save disaster types
    with open(DISASTER_TYPES_FILE, 'w') as f:
        json.dump(disaster_types, f)

    print(f"✅ Model and feature names saved to {MODEL_FILE} , {DISASTER_TYPES_FILE} and {FEATURES_FILE}")

# Train and save the model
if __name__ == "__main__":
    train_disaster_model("disaster_data.csv")
