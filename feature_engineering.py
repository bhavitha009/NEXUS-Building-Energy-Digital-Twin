
import pandas as pd
import numpy as np

# ==================================================
# 1. LOAD ORIGINAL DATASET
# ==================================================

df = pd.read_csv("panther_training_data.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.sort_values("timestamp").reset_index(drop=True)

target = "Panther_education_Vincent"

print("Original rows:", len(df))


# ==================================================
# 2. REMOVE DUPLICATE TIMESTAMPS
# ==================================================

# Duplicate electricity readings are identical.
# Average numeric measurements for each timestamp.

df = (
    df.groupby("timestamp", as_index=False)
    .mean(numeric_only=True)
)

print("Rows after duplicate handling:", len(df))


# ==================================================
# 3. RESTORE COMPLETE HOURLY TIMELINE
# ==================================================

full_range = pd.date_range(
    start=df["timestamp"].min(),
    end=df["timestamp"].max(),
    freq="h"
)

df = df.set_index("timestamp").reindex(full_range)

df.index.name = "timestamp"

print("Rows after restoring hourly timeline:", len(df))


# ==================================================
# 4. REMOVE COLUMNS WITH EXCESSIVE MISSING VALUES
# ==================================================

df = df.drop(
    columns=[
        "cloudCoverage",
        "precipDepth6HR",
        "site_id"
    ],
    errors="ignore"
)


# ==================================================
# 5. HANDLE WEATHER DATA
# ==================================================

weather_columns = [
    "airTemperature",
    "dewTemperature",
    "precipDepth1HR",
    "seaLvlPressure",
    "windDirection",
    "windSpeed"
]

# Fill short weather gaps using previous observations.
# No backward filling, to avoid using future information.

df[weather_columns] = df[weather_columns].ffill(limit=3)


# ==================================================
# 6. CREATE TIME-BASED FEATURES
# ==================================================

df["hour"] = df.index.hour

df["day_of_week"] = df.index.dayofweek

df["month"] = df.index.month

df["is_weekend"] = (
    df["day_of_week"] >= 5
).astype(int)


# ==================================================
# 7. CREATE CYCLIC TIME FEATURES
# ==================================================

df["hour_sin"] = np.sin(
    2 * np.pi * df["hour"] / 24
)

df["hour_cos"] = np.cos(
    2 * np.pi * df["hour"] / 24
)

df["day_sin"] = np.sin(
    2 * np.pi * df["day_of_week"] / 7
)

df["day_cos"] = np.cos(
    2 * np.pi * df["day_of_week"] / 7
)


# ==================================================
# 8. CREATE HISTORICAL ELECTRICITY FEATURES
# ==================================================

# Generate lags on the complete hourly timeline.
# Missing electricity values remain missing.

df["lag_1h"] = df[target].shift(1)

df["lag_24h"] = df[target].shift(24)

df["lag_168h"] = df[target].shift(168)


# ==================================================
# 9. WIND DIRECTION TRANSFORMATION
# ==================================================

df["windDirection_sin"] = np.sin(
    np.deg2rad(df["windDirection"])
)

df["windDirection_cos"] = np.cos(
    np.deg2rad(df["windDirection"])
)


# ==================================================
# 10. REMOVE ROWS WITH MISSING REQUIRED VALUES
# ==================================================

# Missing target values and unavailable weather/lag
# values are removed only after generating the lags.

df = df.dropna()

print("Rows after removing missing values:", len(df))


# ==================================================
# 11. RESTORE TIMESTAMP AS A COLUMN
# ==================================================

df = df.reset_index()


# ==================================================
# 12. SAVE FINAL ML DATASET
# ==================================================

df.to_csv(
    "panther_ml_dataset.csv",
    index=False
)


# ==================================================
# 13. DISPLAY DATASET INFORMATION
# ==================================================

print("\n====================================")
print("FEATURE ENGINEERING COMPLETE")
print("====================================")

print("Total rows:", len(df))

print("Total columns:", len(df.columns))

print("\nFEATURES:")

print(df.columns.tolist())

print("\nMISSING VALUES:")

print(df.isna().sum())

print("\nDUPLICATE TIMESTAMPS:")

print(df["timestamp"].duplicated().sum())

print("\nTIMESTAMP RANGE:")

print("Start:", df["timestamp"].min())

print("End:", df["timestamp"].max())

print("\nFIRST 5 ROWS:")

print(df.head())

print("\nLAST 5 ROWS:")

print(df.tail())

print("\n====================================")
