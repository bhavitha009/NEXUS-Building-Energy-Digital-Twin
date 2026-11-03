
import pandas as pd
import numpy as np
import joblib

# ============================================================
# NEXUS - BUILDING ELECTRICITY EFFICIENCY SCENARIO ENGINE
# ============================================================

print("\n" + "=" * 55)
print(" NEXUS ELECTRICITY EFFICIENCY SCENARIO ENGINE")
print("=" * 55)

# 1. CONFIGURATION

DATA_FILE = "panther_ml_dataset.csv"
MODEL_FILE = "random_forest_model.pkl"

RESULT_FILE = "scenario_results.csv"
TIMESERIES_FILE = "scenario_predictions.csv"

BUILDING_ID = "Panther_education_Vincent"
AREA_M2 = 11248.1
YEAR_BUILT = 1989

FEATURES = [
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

# 2. LOAD DATA AND MODEL

print("\nLoading dataset and trained model...")

df = pd.read_csv(DATA_FILE)
model = joblib.load(MODEL_FILE)

if df.empty:
    raise ValueError("Dataset is empty.")

required_columns = FEATURES + ["timestamp"]
missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(f"Missing dataset columns: {missing_columns}")

# Confirm feature order matches the trained model.
if hasattr(model, "feature_names_in_"):
    model_features = list(model.feature_names_in_)

    if model_features != FEATURES:
        raise ValueError(
            "Model feature names or order do not match "
            "the scenario engine."
        )

X = df[FEATURES].copy()

# Ensure all model inputs are numeric and valid.
X = X.apply(pd.to_numeric, errors="coerce")

if X.isnull().any().any():
    raise ValueError(
        "Missing or non-numeric values found in model features."
    )

if not np.isfinite(X.to_numpy()).all():
    raise ValueError("Infinite values found in model features.")

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
)

if df["timestamp"].isnull().any():
    raise ValueError("Invalid timestamps found in dataset.")

# 3. BUILDING INFORMATION

print("\nBUILDING INFORMATION")
print("-" * 55)
print("Building ID :", BUILDING_ID)
print("Area        :", AREA_M2, "m2")
print("Year Built  :", YEAR_BUILT)
print("Data rows   :", len(df))

# 4. BASELINE PREDICTION

print("\nGenerating baseline predictions...")

baseline_predictions = np.asarray(
    model.predict(X),
    dtype=float
)

if not np.isfinite(baseline_predictions).all():
    raise ValueError("Model generated invalid predictions.")

baseline_average = float(np.mean(baseline_predictions))

if baseline_average <= 0:
    raise ValueError("Baseline average demand must be positive.")

print("\nBASELINE ELECTRICITY DEMAND")
print("-" * 55)
print(f"Average predicted demand: {baseline_average:.2f}")

# 5. SCENARIO RESULT STORAGE

results = []
scenario_predictions_dict = {}

def add_scenario(name, predictions, scenario_type, assumption):

    predictions = np.asarray(predictions, dtype=float)

    if len(predictions) != len(baseline_predictions):
        raise ValueError(
            f"Prediction length mismatch in scenario: {name}"
        )

    if not np.isfinite(predictions).all():
        raise ValueError(
            f"Invalid predictions found in scenario: {name}"
        )

    average_demand = float(np.mean(predictions))

    change = (
        (average_demand - baseline_average)
        / baseline_average
    ) * 100

    # Preserve the output schema used by impact_analysis.py.
    results.append({
        "Scenario": name,
        "Average_Demand": average_demand,
        "Change_From_Baseline_Percent": change,
        "Scenario_Type": scenario_type,
        "Assumption": assumption
    })

    scenario_predictions_dict[name] = predictions

    print(f"\n{name}")
    print("-" * 55)
    print(f"Average demand : {average_demand:.2f}")
    print(f"Change         : {change:+.2f}%")

# 6. BASELINE SCENARIO

add_scenario(
    "Baseline",
    baseline_predictions,
    "Reference",
    "Original Random Forest model predictions"
)

# 7. EFFICIENCY IMPROVEMENT SCENARIOS

print("\n" + "=" * 55)
print("EFFICIENCY IMPROVEMENT EXPERIMENTS")
print("=" * 55)

efficiency_levels = [5, 10, 15, 20, 25]

for efficiency in efficiency_levels:

    scenario_predictions = (
        baseline_predictions * (1 - efficiency / 100)
    )

    add_scenario(
        f"Efficiency +{efficiency}%",
        scenario_predictions,
        "Efficiency",
        (
            f"Assumed proportional electricity demand "
            f"reduction of {efficiency}%"
        )
    )

# 8. OPERATING-HOURS OPTIMIZATION

print("\n" + "=" * 55)
print("OPERATING-HOURS OPTIMIZATION")
print("=" * 55)

# Assumed after-hours period: 22:00 to 04:59.
after_hours = df["hour"].isin(
    [22, 23, 0, 1, 2, 3, 4]
).to_numpy()

print("After-hours observations:", int(after_hours.sum()))

for reduction in [5, 10, 15]:

    scenario_predictions = baseline_predictions.copy()

    scenario_predictions[after_hours] *= (
        1 - reduction / 100
    )

    add_scenario(
        f"After-Hours Reduction {reduction}%",
        scenario_predictions,
        "Operating Hours",
        (
            f"Assumed {reduction}% demand reduction "
            f"during hours 22:00-04:59"
        )
    )

# 9. PEAK-DEMAND MANAGEMENT

print("\n" + "=" * 55)
print("PEAK-DEMAND MANAGEMENT")
print("=" * 55)

# Identify observations in the top 10% of baseline predictions.

peak_threshold = float(
    np.percentile(baseline_predictions, 90)
)

peak_mask = baseline_predictions >= peak_threshold

print(f"Peak threshold     : {peak_threshold:.2f}")
print(f"Peak observations  : {int(peak_mask.sum())}")

for reduction in [5, 10, 15]:

    scenario_predictions = baseline_predictions.copy()

    scenario_predictions[peak_mask] *= (
        1 - reduction / 100
    )

    add_scenario(
        f"Peak Reduction {reduction}%",
        scenario_predictions,
        "Peak Management",
        (
            f"Assumed {reduction}% reduction in "
            f"top 10% baseline demand observations"
        )
    )

# 10. WEATHER SENSITIVITY ANALYSIS

print("\n" + "=" * 55)
print("WEATHER SENSITIVITY ANALYSIS")
print("=" * 55)

for temperature_increase in [2, 4]:

    weather_X = X.copy()

    weather_X["airTemperature"] += temperature_increase

    weather_predictions = np.asarray(
        model.predict(weather_X),
        dtype=float
    )

    add_scenario(
        f"Temperature +{temperature_increase}C",
        weather_predictions,
        "Weather Sensitivity",
        (
            f"Air temperature feature increased by "
            f"{temperature_increase} degrees C; "
            f"other features held constant"
        )
    )

# 11. COMBINED ENERGY INTERVENTION

print("\n" + "=" * 55)
print("COMBINED ENERGY INTERVENTION")
print("=" * 55)

combined_predictions = baseline_predictions.copy()

# Assumed 10% proportional reduction across all observations.
combined_predictions *= 0.90

# Additional assumed 5% reduction during after-hours.
combined_predictions[after_hours] *= 0.95

add_scenario(
    "Combined Intervention",
    combined_predictions,
    "Combined",
    (
        "Assumed 10% overall proportional demand reduction "
        "and an additional 5% after-hours reduction"
    )
)

# 12. CREATE SCENARIO RESULTS

results_df = pd.DataFrame(results)

# 13. SAVE SCENARIO SUMMARY

results_df.to_csv(
    RESULT_FILE,
    index=False
)

# 14. SAVE HOURLY SCENARIO PREDICTIONS

timeseries_df = pd.DataFrame({
    "timestamp": df["timestamp"],
    "Baseline": baseline_predictions
})

for scenario_name, predictions in scenario_predictions_dict.items():

    if scenario_name != "Baseline":
        timeseries_df[scenario_name] = predictions

timeseries_df.to_csv(
    TIMESERIES_FILE,
    index=False
)

# 15. DISPLAY FINAL COMPARISON

print("\n" + "=" * 75)
print("FINAL SCENARIO COMPARISON")
print("=" * 75)

print(
    results_df[
        [
            "Scenario",
            "Average_Demand",
            "Change_From_Baseline_Percent"
        ]
    ].to_string(
        index=False,
        formatters={
            "Average_Demand": "{:.2f}".format,
            "Change_From_Baseline_Percent": "{:+.2f}%".format
        }
    )
)

# 16. FINAL SUMMARY

print("\n" + "=" * 55)
print("SCENARIO ENGINE SUMMARY")
print("=" * 55)

print("Building       :", BUILDING_ID)
print("Total rows     :", len(df))
print("Total scenarios:", len(results_df))
print("Baseline       :", f"{baseline_average:.2f}")

print("\nGenerated files:")
print("1.", RESULT_FILE)
print("2.", TIMESERIES_FILE)

print("\nIMPORTANT:")
print("- Efficiency and operational reductions are assumed scenarios.")
print("- Weather scenarios are model sensitivity experiments.")
print("- Results are simulations, not measured energy savings.")

print("\nNEXUS SCENARIO ENGINE COMPLETED SUCCESSFULLY!")
print("=" * 55)
