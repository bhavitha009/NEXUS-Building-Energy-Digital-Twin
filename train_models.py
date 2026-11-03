
import pandas as pd
import numpy as np
import joblib

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ==================================================
# 1. LOAD DATASET
# ==================================================

df = pd.read_csv("panther_ml_dataset.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.sort_values("timestamp").reset_index(drop=True)

target = "Panther_education_Vincent"

print("TOTAL DATASET ROWS:", len(df))


# ==================================================
# 2. DEFINE FEATURES
# ==================================================

features = [
    "airTemperature",
    "dewTemperature",
    "precipDepth1HR",
    "seaLvlPressure",
    "windSpeed",
    "hour",
    "day_of_week",
    "month",
    "is_weekend",
    "hour_sin",
    "hour_cos",
    "day_sin",
    "day_cos",
    "lag_1h",
    "lag_24h",
    "lag_168h",
    "windDirection_sin",
    "windDirection_cos"
]

X = df[features]
y = df[target]


# ==================================================
# 3. CHRONOLOGICAL 70:15:15 SPLIT
# ==================================================

total_rows = len(df)

train_end = int(total_rows * 0.70)

validation_end = int(total_rows * 0.85)

X_train = X.iloc[:train_end]
y_train = y.iloc[:train_end]

X_val = X.iloc[train_end:validation_end]
y_val = y.iloc[train_end:validation_end]

X_test = X.iloc[validation_end:]
y_test = y.iloc[validation_end:]

print("\n====================================")
print("CHRONOLOGICAL DATA SPLIT")
print("====================================")

print("Training samples:", len(X_train))
print("Validation samples:", len(X_val))
print("Testing samples:", len(X_test))

print("\nTRAINING PERIOD:")
print(df["timestamp"].iloc[0], "to",
      df["timestamp"].iloc[train_end - 1])

print("\nVALIDATION PERIOD:")
print(df["timestamp"].iloc[train_end], "to",
      df["timestamp"].iloc[validation_end - 1])

print("\nTESTING PERIOD:")
print(df["timestamp"].iloc[validation_end], "to",
      df["timestamp"].iloc[-1])


# ==================================================
# 4. DEFINE MODELS
# ==================================================

models = {

    "Linear Regression": LinearRegression(),

    "Random Forest": RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    ),

    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=100,
        random_state=42
    )
}


# ==================================================
# 5. HELPER FUNCTION FOR METRICS
# ==================================================

def calculate_metrics(actual, predicted):

    mae = mean_absolute_error(actual, predicted)

    rmse = np.sqrt(
        mean_squared_error(actual, predicted)
    )

    r2 = r2_score(actual, predicted)

    return mae, rmse, r2


# ==================================================
# 6. TRAIN AND VALIDATE MODELS
# ==================================================

validation_results = []

trained_models = {}

print("\n====================================")
print("MODEL TRAINING AND VALIDATION")
print("====================================")

for name, model in models.items():

    print("\nTraining:", name)

    model.fit(X_train, y_train)

    predictions = model.predict(X_val)

    mae, rmse, r2 = calculate_metrics(
        y_val,
        predictions
    )

    trained_models[name] = model

    validation_results.append({

        "Model": name,
        "Validation_MAE": mae,
        "Validation_RMSE": rmse,
        "Validation_R2": r2

    })

    print("Validation MAE :", round(mae, 4))
    print("Validation RMSE:", round(rmse, 4))
    print("Validation R2  :", round(r2, 4))


# ==================================================
# 7. PERSISTENCE BASELINE
# ==================================================

# Predict the next hour using the previous
# actual electricity reading.

baseline_val_predictions = X_val["lag_1h"]

baseline_val_mae, baseline_val_rmse, baseline_val_r2 = (
    calculate_metrics(
        y_val,
        baseline_val_predictions
    )
)

print("\n====================================")
print("PERSISTENCE BASELINE - VALIDATION")
print("====================================")

print("MAE :", round(baseline_val_mae, 4))
print("RMSE:", round(baseline_val_rmse, 4))
print("R2  :", round(baseline_val_r2, 4))


# ==================================================
# 8. SELECT BEST MODEL USING VALIDATION MAE
# ==================================================

validation_df = pd.DataFrame(validation_results)

validation_df = validation_df.sort_values(
    by="Validation_MAE"
).reset_index(drop=True)

best_model_name = validation_df.iloc[0]["Model"]

print("\n====================================")
print("BEST MODEL SELECTED")
print("====================================")

print("Selected model:", best_model_name)

print("\nValidation comparison:")

print(validation_df.to_string(index=False))


# ==================================================
# 9. REFIT SELECTED MODEL ON TRAIN + VALIDATION
# ==================================================

X_train_val = pd.concat(
    [X_train, X_val],
    axis=0
)

y_train_val = pd.concat(
    [y_train, y_val],
    axis=0
)

best_model = models[best_model_name]

best_model.fit(
    X_train_val,
    y_train_val
)

# Save the selected best model separately.

joblib.dump(
    best_model,
    "best_model.pkl"
)


# ==================================================
# 10. FINAL TEST EVALUATION
# ==================================================

test_predictions = best_model.predict(X_test)

test_mae, test_rmse, test_r2 = calculate_metrics(
    y_test,
    test_predictions
)

print("\n====================================")
print("FINAL TEST RESULTS - BEST MODEL")
print("====================================")

print("Model:", best_model_name)

print("Test MAE :", round(test_mae, 4))
print("Test RMSE:", round(test_rmse, 4))
print("Test R2  :", round(test_r2, 4))


# ==================================================
# 11. TEST PERSISTENCE BASELINE
# ==================================================

baseline_test_predictions = X_test["lag_1h"]

baseline_test_mae, baseline_test_rmse, baseline_test_r2 = (
    calculate_metrics(
        y_test,
        baseline_test_predictions
    )
)

print("\n====================================")
print("PERSISTENCE BASELINE - FINAL TEST")
print("====================================")

print("MAE :", round(baseline_test_mae, 4))
print("RMSE:", round(baseline_test_rmse, 4))
print("R2  :", round(baseline_test_r2, 4))


# ==================================================
# 12. SAVE RANDOM FOREST FOR SCENARIO ENGINE
# ==================================================

# Keep this filename because the existing
# scenario_engine.py loads this model.

rf_model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(
    X_train_val,
    y_train_val
)

joblib.dump(
    rf_model,
    "random_forest_model.pkl"
)

print("\nRandom Forest model saved!")


# ==================================================
# 13. SAVE MODEL RESULTS
# ==================================================

final_results = pd.DataFrame([

    {
        "Model": best_model_name,
        "Evaluation": "Selected ML Model",
        "MAE": test_mae,
        "RMSE": test_rmse,
        "R2": test_r2
    },

    {
        "Model": "Persistence Baseline",
        "Evaluation": "Previous Hour Prediction",
        "MAE": baseline_test_mae,
        "RMSE": baseline_test_rmse,
        "R2": baseline_test_r2
    }

])

final_results.to_csv(
    "model_results.csv",
    index=False
)

validation_df.to_csv(
    "validation_results.csv",
    index=False
)


# ==================================================
# 14. SAVE TEST PREDICTIONS
# ==================================================

prediction_df = pd.DataFrame({

    "timestamp": df["timestamp"].iloc[validation_end:].values,

    "Actual": y_test.values,

    "Predicted": test_predictions,

    "Persistence_Baseline": baseline_test_predictions.values

})

prediction_df.to_csv(
    "test_predictions.csv",
    index=False
)


# ==================================================
# 15. SAVE BEST MODEL NAME
# ==================================================

with open("best_model_name.txt", "w") as file:

    file.write(best_model_name)


# ==================================================
# 16. FINAL SUMMARY
# ==================================================

print("\n====================================")
print("TRAINING PIPELINE COMPLETE")
print("====================================")

print("Best Model:", best_model_name)

print("Final Test MAE:", round(test_mae, 4))

print("Final Test RMSE:", round(test_rmse, 4))

print("Final Test R2:", round(test_r2, 4))

print("\nFILES SAVED:")

print("1. best_model.pkl")
print("2. random_forest_model.pkl")
print("3. best_model_name.txt")
print("4. model_results.csv")
print("5. validation_results.csv")
print("6. test_predictions.csv")

print("\n====================================")
