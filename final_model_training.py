
import pandas as pd
import numpy as np
import joblib
import json

from sklearn.ensemble import RandomForestRegressor
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


# ==================================================
# 2. SELECT FINAL FEATURES
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
# 3. CHRONOLOGICAL DATA SPLIT
# ==================================================

total_rows = len(df)

train_end = int(total_rows * 0.70)

validation_end = int(total_rows * 0.85)

# Training + validation data

X_train_val = X.iloc[:validation_end]
y_train_val = y.iloc[:validation_end]

# Final chronological evaluation period

X_test = X.iloc[validation_end:]
y_test = y.iloc[validation_end:]

test_timestamps = df["timestamp"].iloc[validation_end:]


print("\n====================================")
print("NEXUS FINAL MODEL TRAINING")
print("====================================")

print("Training + validation:", len(X_train_val))
print("Final evaluation:", len(X_test))

print(
    "Training period:",
    df["timestamp"].iloc[0],
    "to",
    df["timestamp"].iloc[validation_end - 1]
)

print(
    "Evaluation period:",
    test_timestamps.iloc[0],
    "to",
    test_timestamps.iloc[-1]
)


# ==================================================
# 4. TRAIN FINAL RANDOM FOREST
# ==================================================

print("\nTraining final Random Forest...")

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

model.fit(
    X_train_val,
    y_train_val
)

print("Training completed!")


# ==================================================
# 5. FINAL MODEL PREDICTIONS
# ==================================================

predictions = model.predict(X_test)


# ==================================================
# 6. EVALUATE MODEL
# ==================================================

model_mae = mean_absolute_error(
    y_test,
    predictions
)

model_rmse = np.sqrt(
    mean_squared_error(y_test, predictions)
)

model_r2 = r2_score(
    y_test,
    predictions
)


# ==================================================
# 7. PERSISTENCE BASELINE
# ==================================================

baseline_predictions = X_test["lag_1h"]

baseline_mae = mean_absolute_error(
    y_test,
    baseline_predictions
)

baseline_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        baseline_predictions
    )
)

baseline_r2 = r2_score(
    y_test,
    baseline_predictions
)


# ==================================================
# 8. DISPLAY FINAL RESULTS
# ==================================================

print("\n====================================")
print("FINAL MODEL PERFORMANCE")
print("====================================")

print("\nRandom Forest")

print("MAE :", round(model_mae, 4))
print("RMSE:", round(model_rmse, 4))
print("R2  :", round(model_r2, 4))

print("\nPersistence Baseline")

print("MAE :", round(baseline_mae, 4))
print("RMSE:", round(baseline_rmse, 4))
print("R2  :", round(baseline_r2, 4))


# ==================================================
# 9. CALCULATE IMPROVEMENT
# ==================================================

mae_improvement = (
    (baseline_mae - model_mae) / baseline_mae
) * 100

rmse_improvement = (
    (baseline_rmse - model_rmse) / baseline_rmse
) * 100

print("\n====================================")
print("MODEL IMPROVEMENT")
print("====================================")

print(
    "MAE improvement:",
    round(mae_improvement, 2),
    "%"
)

print(
    "RMSE improvement:",
    round(rmse_improvement, 2),
    "%"
)


# ==================================================
# 10. SAVE FINAL MODEL
# ==================================================

joblib.dump(
    model,
    "random_forest_model.pkl"
)

joblib.dump(
    model,
    "best_model.pkl"
)

print("\nFinal model saved successfully!")


# ==================================================
# 11. SAVE TEST PREDICTIONS
# ==================================================

prediction_df = pd.DataFrame({

    "timestamp": test_timestamps.values,

    "Actual": y_test.values,

    "Predicted": predictions,

    "Persistence_Baseline": baseline_predictions.values

})

prediction_df["Prediction_Error"] = (
    prediction_df["Actual"] -
    prediction_df["Predicted"]
)

prediction_df["Absolute_Error"] = (
    prediction_df["Prediction_Error"].abs()
)

prediction_df.to_csv(
    "test_predictions.csv",
    index=False
)


# ==================================================
# 12. SAVE FEATURE IMPORTANCE
# ==================================================

importance_df = pd.DataFrame({

    "Feature": features,

    "Importance": model.feature_importances_

}).sort_values(
    "Importance",
    ascending=False
)

importance_df.to_csv(
    "feature_importance_final.csv",
    index=False
)


# ==================================================
# 13. SAVE MODEL METRICS
# ==================================================

metrics_df = pd.DataFrame([

    {
        "Model": "Random Forest",
        "MAE": model_mae,
        "RMSE": model_rmse,
        "R2": model_r2
    },

    {
        "Model": "Persistence Baseline",
        "MAE": baseline_mae,
        "RMSE": baseline_rmse,
        "R2": baseline_r2
    }

])

metrics_df.to_csv(
    "final_model_metrics.csv",
    index=False
)


# ==================================================
# 14. SAVE MODEL METADATA
# ==================================================

metadata = {

    "model": "Random Forest Regressor",

    "selected_feature_group": "All 18 Features",

    "number_of_features": len(features),

    "number_of_trees": 100,

    "random_state": 42,

    "training_samples": len(X_train_val),

    "evaluation_samples": len(X_test),

    "prediction_horizon": "One-hour-ahead rolling prediction",

    "features": features

}

with open(
    "model_metadata.json",
    "w"
) as file:

    json.dump(
        metadata,
        file,
        indent=4
    )


# ==================================================
# 15. FINAL SUMMARY
# ==================================================

print("\n====================================")
print("NEXUS FINAL MODEL COMPLETED")
print("====================================")

print("Model: Random Forest")

print("Features:", len(features))

print("Test MAE:", round(model_mae, 4))

print("Test RMSE:", round(model_rmse, 4))

print("Test R2:", round(model_r2, 4))

print("\nGenerated files:")

print("1. random_forest_model.pkl")
print("2. best_model.pkl")
print("3. test_predictions.csv")
print("4. feature_importance_final.csv")
print("5. final_model_metrics.csv")
print("6. model_metadata.json")

print("\n====================================")
