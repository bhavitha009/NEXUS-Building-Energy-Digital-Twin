
import pandas as pd
import numpy as np

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

y = df[target]

print("\n====================================")
print("NEXUS FEATURE ABLATION - VALIDATION")
print("====================================")

print("Total dataset rows:", len(df))


# ==================================================
# 2. DEFINE FEATURE GROUPS
# ==================================================

# MODEL A: Previous hour only

features_A = [
    "lag_1h"
]


# MODEL B: All historical electricity features

features_B = [
    "lag_1h",
    "lag_24h",
    "lag_168h"
]


# MODEL C: All original features

features_C = [
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


experiments = {

    "Model A - Lag 1h Only": features_A,

    "Model B - All Lag Features": features_B,

    "Model C - All Features": features_C

}


# ==================================================
# 3. CHRONOLOGICAL 70:15:15 SPLIT
# ==================================================

total_rows = len(df)

train_end = int(total_rows * 0.70)

validation_end = int(total_rows * 0.85)

# First 70%: Training

X_train = df.iloc[:train_end]

y_train = y.iloc[:train_end]


# Next 15%: Validation

X_val = df.iloc[train_end:validation_end]

y_val = y.iloc[train_end:validation_end]


# Final 15%: Reserved test data

X_test = df.iloc[validation_end:]

y_test = y.iloc[validation_end:]


print("\n====================================")
print("CHRONOLOGICAL DATA SPLIT")
print("====================================")

print("Training samples:", len(X_train))

print("Validation samples:", len(X_val))

print("Reserved test samples:", len(X_test))

print("\nTraining period:")

print(
    df["timestamp"].iloc[0],
    "to",
    df["timestamp"].iloc[train_end - 1]
)

print("\nValidation period:")

print(
    df["timestamp"].iloc[train_end],
    "to",
    df["timestamp"].iloc[validation_end - 1]
)

print("\nReserved test period:")

print(
    df["timestamp"].iloc[validation_end],
    "to",
    df["timestamp"].iloc[-1]
)


# ==================================================
# 4. METRIC FUNCTION
# ==================================================

def evaluate(actual, predicted):

    mae = mean_absolute_error(
        actual,
        predicted
    )

    rmse = np.sqrt(
        mean_squared_error(actual, predicted)
    )

    r2 = r2_score(
        actual,
        predicted
    )

    return mae, rmse, r2


# ==================================================
# 5. TRAIN AND VALIDATE EACH MODEL
# ==================================================

results = []

print("\n====================================")
print("FEATURE ABLATION EXPERIMENTS")
print("====================================")

for name, feature_list in experiments.items():

    print("\n------------------------------------")

    print("Training:", name)

    print("Number of features:", len(feature_list))

    # Create Random Forest

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )

    # Train ONLY on training data

    model.fit(
        X_train[feature_list],
        y_train
    )

    # Evaluate ONLY on validation data

    predictions = model.predict(
        X_val[feature_list]
    )

    mae, rmse, r2 = evaluate(
        y_val,
        predictions
    )

    results.append({

        "Experiment": name,

        "Number_of_Features": len(feature_list),

        "MAE": mae,

        "RMSE": rmse,

        "R2": r2

    })

    print("Validation MAE :", round(mae, 4))

    print("Validation RMSE:", round(rmse, 4))

    print("Validation R2  :", round(r2, 4))


# ==================================================
# 6. PERSISTENCE BASELINE
# ==================================================

print("\n====================================")
print("PERSISTENCE BASELINE - VALIDATION")
print("====================================")

# Predict using previous hour's actual reading.

baseline_predictions = X_val["lag_1h"]

baseline_mae, baseline_rmse, baseline_r2 = evaluate(
    y_val,
    baseline_predictions
)

print("Validation MAE :", round(baseline_mae, 4))

print("Validation RMSE:", round(baseline_rmse, 4))

print("Validation R2  :", round(baseline_r2, 4))


results.append({

    "Experiment": "Persistence Baseline",

    "Number_of_Features": 1,

    "MAE": baseline_mae,

    "RMSE": baseline_rmse,

    "R2": baseline_r2

})


# ==================================================
# 7. COMPARE VALIDATION RESULTS
# ==================================================

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by="MAE",
    ascending=True
).reset_index(drop=True)


print("\n====================================")
print("VALIDATION COMPARISON")
print("====================================")

print(
    results_df.to_string(index=False)
)


# ==================================================
# 8. SELECT BEST FEATURE GROUP
# ==================================================

# Select only among the three ML experiments.
# Persistence is a baseline, not a trained ML model.

ml_results = results_df[
    results_df["Experiment"] != "Persistence Baseline"
]

best_experiment = ml_results.iloc[0]["Experiment"]

print("\n====================================")
print("BEST FEATURE GROUP")
print("====================================")

print("Selected:", best_experiment)

print(
    "Best validation MAE:",
    round(ml_results.iloc[0]["MAE"], 4)
)


# ==================================================
# 9. SAVE RESULTS
# ==================================================

results_df.to_csv(
    "feature_ablation_validation_results.csv",
    index=False
)


# Save selected feature group

with open(
    "best_feature_group.txt",
    "w"
) as file:

    file.write(best_experiment)


# ==================================================
# 10. FINAL SUMMARY
# ==================================================

print("\n====================================")
print("VALIDATION EXPERIMENT COMPLETED")
print("====================================")

print("Best feature group:", best_experiment)

print("\nSaved files:")

print("1. feature_ablation_validation_results.csv")

print("2. best_feature_group.txt")

print("\nThe final test dataset was NOT used.")

print("\n====================================")
