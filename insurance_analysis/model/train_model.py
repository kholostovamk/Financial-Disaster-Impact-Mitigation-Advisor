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

    # One-hot encode the 'incidentType' column
    df = pd.get_dummies(df, columns=['incidentType'])

    X = df[['combinedFIPS', 'Precipitation', 'MaxTemp', 'MinTemp', 'AverageTemp', 'Month', 'year', 'Latitude', 'Longitude']]
    y = df.filter(like='incidentType_')  # Selecting all one-hot encoded incident types
    
    disaster_types = list(coloum.replace('incidentType_', '') for coloum in y.columns)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

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
