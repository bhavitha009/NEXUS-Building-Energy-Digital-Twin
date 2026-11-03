
import pandas as pd
import matplotlib.pyplot as plt
import joblib
import os
import numpy as np

from sklearn.metrics import mean_absolute_error


# ============================================================
# NEXUS - ELECTRICITY EFFICIENCY VISUALIZATION
# ============================================================

print("\n==============================================")
print(" NEXUS ELECTRICITY EFFICIENCY VISUALIZATION")
print("==============================================")


# ============================================================
# 1. LOAD REQUIRED FILES
# ============================================================

DATA_FILE = "panther_ml_dataset.csv"
MODEL_FILE = "random_forest_model.pkl"
PREDICTION_FILE = "test_predictions.csv"
SCENARIO_FILE = "scenario_results.csv"

OUTPUT_DIR = "nexus_graphs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

required_files = [
    DATA_FILE,
    MODEL_FILE,
    PREDICTION_FILE,
    SCENARIO_FILE
]

for file in required_files:
    if not os.path.exists(file):
        raise FileNotFoundError(
            f"Required file not found: {file}"
        )

df = pd.read_csv(DATA_FILE)

model = joblib.load(MODEL_FILE)

prediction_df = pd.read_csv(PREDICTION_FILE)

scenario_df = pd.read_csv(SCENARIO_FILE)

df["timestamp"] = pd.to_datetime(df["timestamp"])

prediction_df["timestamp"] = pd.to_datetime(
    prediction_df["timestamp"]
)

print("\nDataset loaded successfully.")

print("Dataset rows:", len(df))

print("Test prediction rows:", len(prediction_df))

print("Scenario rows:", len(scenario_df))


# ============================================================
# 2. DEFINE MODEL FEATURES
# ============================================================

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

target = "Panther_education_Vincent"

# Verify model and dataset compatibility.

missing_features = [
    feature for feature in features
    if feature not in df.columns
]

if missing_features:
    raise ValueError(
        f"Missing model features: {missing_features}"
    )

if not hasattr(model, "feature_importances_"):
    raise ValueError(
        "Loaded Random Forest model does not support "
        "feature importance."
    )


# ============================================================
# 3. ACTUAL VS PREDICTED TEST RESULTS
# ============================================================

print("\n1. GENERATING ACTUAL VS PREDICTED GRAPH")

required_prediction_columns = [
    "timestamp",
    "Actual",
    "Predicted",
    "Persistence_Baseline"
]

for col in required_prediction_columns:
    if col not in prediction_df.columns:
        raise ValueError(
            f"Missing column in test_predictions.csv: {col}"
        )

prediction_df = prediction_df.sort_values(
    "timestamp"
).reset_index(drop=True)

plot_size = min(500, len(prediction_df))

plot_df = prediction_df.iloc[:plot_size]

plt.figure(figsize=(14, 6))

plt.plot(
    plot_df["timestamp"],
    plot_df["Actual"],
    label="Actual Electricity Demand",
    linewidth=1.5
)

plt.plot(
    plot_df["timestamp"],
    plot_df["Predicted"],
    label="Random Forest Prediction",
    linewidth=1.5
)

plt.title(
    "NEXUS: Actual vs Predicted Electricity Demand"
)

plt.xlabel("Timestamp")

plt.ylabel("Electricity Demand")

plt.legend()

plt.grid(alpha=0.3)

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/actual_vs_predicted_test.png",
    dpi=300
)

plt.close()


# ============================================================
# 4. RANDOM FOREST VS PERSISTENCE BASELINE
# ============================================================

print("2. GENERATING MODEL BASELINE COMPARISON")

rf_mae = mean_absolute_error(
    prediction_df["Actual"],
    prediction_df["Predicted"]
)

baseline_mae = mean_absolute_error(
    prediction_df["Actual"],
    prediction_df["Persistence_Baseline"]
)

model_names = [
    "Random Forest",
    "Persistence Baseline"
]

mae_values = [
    rf_mae,
    baseline_mae
]

plt.figure(figsize=(9, 5))

bars = plt.bar(
    model_names,
    mae_values
)

plt.title(
    "NEXUS: Random Forest vs Persistence Baseline"
)

plt.xlabel("Prediction Model")

plt.ylabel("Mean Absolute Error (MAE)")

plt.grid(axis="y", alpha=0.3)

for bar, value in zip(bars, mae_values):

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{value:.2f}",
        ha="center",
        va="bottom"
    )

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/model_baseline_comparison.png",
    dpi=300
)

plt.close()

print("Random Forest MAE:", round(rf_mae, 4))

print("Persistence MAE:", round(baseline_mae, 4))


# ============================================================
# 5. OVERALL SCENARIO COMPARISON
# ============================================================

print("3. GENERATING OVERALL SCENARIO COMPARISON")

required_scenario_columns = [
    "Scenario",
    "Average_Demand",
    "Scenario_Type"
]

for col in required_scenario_columns:
    if col not in scenario_df.columns:
        raise ValueError(
            f"Missing scenario column: {col}"
        )

sorted_scenarios = scenario_df.sort_values(
    "Average_Demand",
    ascending=True
)

plt.figure(figsize=(12, 8))

plt.barh(
    sorted_scenarios["Scenario"],
    sorted_scenarios["Average_Demand"]
)

plt.title(
    "NEXUS: Overall Electricity Scenario Comparison"
)

plt.xlabel("Average Predicted / Simulated Demand")

plt.ylabel("Scenario")

plt.grid(axis="x", alpha=0.3)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/scenario_comparison.png",
    dpi=300
)

plt.close()


# ============================================================
# 6. EFFICIENCY SENSITIVITY ANALYSIS
# ============================================================

print("4. GENERATING EFFICIENCY SENSITIVITY GRAPH")

efficiency_df = scenario_df[
    scenario_df["Scenario_Type"] == "Efficiency"
].copy()

efficiency_df["Efficiency_Percent"] = pd.to_numeric(
    efficiency_df["Scenario"].str.extract(
        r"(\d+)"
    )[0],
    errors="coerce"
)

efficiency_df = efficiency_df.dropna(
    subset=["Efficiency_Percent"]
)

efficiency_df = efficiency_df.sort_values(
    "Efficiency_Percent"
)

baseline_row = scenario_df[
    scenario_df["Scenario"] == "Baseline"
]

if baseline_row.empty:
    raise ValueError("Baseline scenario not found.")

baseline_demand = baseline_row[
    "Average_Demand"
].iloc[0]

plt.figure(figsize=(9, 5))

plt.plot(
    efficiency_df["Efficiency_Percent"],
    efficiency_df["Average_Demand"],
    marker="o",
    linewidth=2,
    label="Simulated Demand"
)

plt.axhline(
    y=baseline_demand,
    linestyle="--",
    label="Baseline Demand"
)

plt.title(
    "NEXUS: Efficiency Sensitivity Analysis"
)

plt.xlabel("Assumed Efficiency Improvement (%)")

plt.ylabel("Average Simulated Demand")

plt.legend()

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/efficiency_sensitivity.png",
    dpi=300
)

plt.close()


# ============================================================
# 7. OPERATING HOURS VS PEAK DEMAND
# ============================================================

print("5. GENERATING OPERATIONAL SCENARIO GRAPH")

operational_df = scenario_df[
    scenario_df["Scenario_Type"].isin(
        ["Operating Hours", "Peak Management"]
    )
].copy()

plt.figure(figsize=(11, 6))

for scenario_type, group in operational_df.groupby(
    "Scenario_Type"
):

    group = group.copy()

    group["Reduction_Percent"] = pd.to_numeric(
        group["Scenario"].str.extract(
            r"(\d+)"
        )[0],
        errors="coerce"
    )

    group = group.dropna(
        subset=["Reduction_Percent"]
    )

    group = group.sort_values(
        "Reduction_Percent"
    )

    plt.plot(
        group["Reduction_Percent"],
        group["Average_Demand"],
        marker="o",
        linewidth=2,
        label=scenario_type
    )

plt.axhline(
    y=baseline_demand,
    linestyle="--",
    label="Baseline"
)

plt.title(
    "NEXUS: Operational Intervention Comparison"
)

plt.xlabel("Assumed Reduction (%)")

plt.ylabel("Average Simulated Demand")

plt.legend()

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/operational_scenario_comparison.png",
    dpi=300
)

plt.close()


# ============================================================
# 8. WEATHER SENSITIVITY ANALYSIS
# ============================================================

print("6. GENERATING WEATHER SENSITIVITY GRAPH")

weather_df = scenario_df[
    scenario_df["Scenario_Type"] == "Weather Sensitivity"
].copy()

weather_df["Temperature_Increase"] = pd.to_numeric(
    weather_df["Scenario"].str.extract(
        r"(\d+)"
    )[0],
    errors="coerce"
)

weather_df = weather_df.dropna(
    subset=["Temperature_Increase"]
)

weather_df = weather_df.sort_values(
    "Temperature_Increase"
)

plt.figure(figsize=(9, 5))

temperature_values = (
    [0] +
    weather_df["Temperature_Increase"].tolist()
)

demand_values = (
    [baseline_demand] +
    weather_df["Average_Demand"].tolist()
)

plt.plot(
    temperature_values,
    demand_values,
    marker="o",
    linewidth=2
)

plt.title(
    "NEXUS: Weather Sensitivity Analysis"
)

plt.xlabel("Assumed Air Temperature Increase (°C)")

plt.ylabel("Model-Predicted Average Demand")

plt.xticks(temperature_values)

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/weather_sensitivity.png",
    dpi=300
)

plt.close()


# ============================================================
# 9. RANDOM FOREST FEATURE IMPORTANCE
# ============================================================

print("7. GENERATING FEATURE IMPORTANCE GRAPH")

importance = pd.DataFrame({

    "Feature": features,

    "Importance": model.feature_importances_

})

importance = importance.sort_values(
    "Importance",
    ascending=False
)

top_features = importance.head(10).sort_values(
    "Importance",
    ascending=True
)

plt.figure(figsize=(10, 6))

plt.barh(
    top_features["Feature"],
    top_features["Importance"]
)

plt.title(
    "NEXUS: Random Forest Feature Importance"
)

plt.xlabel("Feature Importance")

plt.ylabel("Feature")

plt.grid(axis="x", alpha=0.3)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/feature_importance.png",
    dpi=300
)

plt.close()


# ============================================================
# 10. SAVE FEATURE IMPORTANCE
# ============================================================

importance.to_csv(
    "feature_importance_final.csv",
    index=False
)


# ============================================================
# 11. SAVE TEST ERROR ANALYSIS
# ============================================================

print("8. GENERATING TEST ERROR ANALYSIS")

error_df = prediction_df.copy()

error_df["Prediction_Error"] = (
    error_df["Actual"] - error_df["Predicted"]
)

error_df["Absolute_Error"] = (
    error_df["Prediction_Error"].abs()
)

error_df.to_csv(
    "test_error_analysis.csv",
    index=False
)

plt.figure(figsize=(10, 5))

plt.hist(
    error_df["Prediction_Error"],
    bins=40
)

plt.title(
    "NEXUS: Random Forest Prediction Error Distribution"
)

plt.xlabel("Actual - Predicted")

plt.ylabel("Frequency")

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/prediction_error_distribution.png",
    dpi=300
)

plt.close()


# ============================================================
# 12. FINAL OUTPUT
# ============================================================

print("\n==============================================")
print(" VISUALIZATION COMPLETED")
print("==============================================")

graph_files = [

    "actual_vs_predicted_test.png",

    "model_baseline_comparison.png",

    "scenario_comparison.png",

    "efficiency_sensitivity.png",

    "operational_scenario_comparison.png",

    "weather_sensitivity.png",

    "feature_importance.png",

    "prediction_error_distribution.png"

]

print("\nGENERATED GRAPHS:")

for graph in graph_files:

    print(f"{OUTPUT_DIR}/{graph}")

print("\nADDITIONAL FILES:")

print("1. feature_importance_final.csv")

print("2. test_error_analysis.csv")

print("\nMODEL TEST MAE:", round(rf_mae, 4))

print("PERSISTENCE TEST MAE:", round(baseline_mae, 4))

print("\nNEXUS VISUALIZATION COMPLETED")
