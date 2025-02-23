import pandas as pd
import numpy as np
import json
from xgboost import XGBClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, log_loss, f1_score


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


    base_model = XGBClassifier(n_estimators=300, learning_rate=0.1, eval_metric='logloss')
    model = MultiOutputClassifier(base_model)
    model.fit(X_train, y_train)
    print("✅ Model training complete!")

    # Predictions on the test set
    y_pred = model.predict(X_test)
    y_pred_proba = np.array([m.predict_proba(X_test)[:, 1] for m in model.estimators_]).T  # Get P(Disaster)

    # Calculate evaluation metrics
    accuracy = accuracy_score(y_test, y_pred)
    valid_disasters = [i for i in range(y_test.shape[1]) if len(set(y_test.iloc[:, i])) > 1]  # Only disasters with 0s & 1s
    roc_auc = roc_auc_score(y_test.iloc[:, valid_disasters], y_pred_proba[:, valid_disasters], average='macro') if valid_disasters else np.nan

    logloss = log_loss(y_test, y_pred_proba)
    f1 = f1_score(y_test, y_pred, average='macro', zero_division=1)

    print(f"\n📊 **Model Performance:**")
    print(f"🔹 Accuracy: {accuracy:.4f}")
    print(f"🔹 ROC AUC Score: {roc_auc:.4f}")
    print(f"🔹 Log Loss: {logloss:.4f}")
    print(f"🔹 F1 Score: {f1:.4f}")


    disaster_types = y.columns.tolist()

    def predict_disaster_prob(fips, precip, avg_temp, month, year, latitude, longitude):
        """Predict probability of each disaster type for a given location."""
        input_data = [[fips, precip, avg_temp, month, year, latitude, longitude]]

        probs_list = model.predict_proba(input_data)
        #print(probs_list)
        arr = []
        for p in probs_list:
            #print(p[0][1])
            arr.append(p[0][1])

        #print(arr)

        # Disaster types
        disaster_types = [
            "Fire", "Flood", "Tornado", "Storm", "Other", "Biological","Mud/Landslide", "Earthquake", "Drought", "Toxic Substances", "Human Cause",
            "Tsunami", "Freezing"
        ]

        disaster_prob = {}
        for key, value in zip(disaster_types, arr):
            disaster_prob[key] = value

        return disaster_prob

    return model, X.columns.tolist(), predict_disaster_prob


# Example usage
if __name__ == "__main__":
    # Train the model and get the prediction function
    model, feature_names, predict_func = train_disaster_model("disaster_data.csv")

    # Example prediction
    result = predict_func(4007, 1.19, 56.8, 5, 2023, -104.944561, 36.00972846)
    print(result)
