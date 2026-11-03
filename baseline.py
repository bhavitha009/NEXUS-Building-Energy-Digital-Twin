import pandas as pd


# ==================================================
# NEXUS DIGITAL TWIN - BUILDING BASELINE
# ==================================================

# Load electricity/weather ML dataset
df = pd.read_csv("panther_ml_dataset.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"])

target = "Panther_education_Vincent"


# ==================================================
# 1. BUILDING INFORMATION
# ==================================================

building_info = {
    "building_id": "Panther_education_Vincent",
    "site_id": "Panther",
    "primary_space_usage": "Education",
    "sub_primary_space_usage": "Classroom",
    "area_m2": 11248.1,
    "area_sqft": 121074,
    "year_built": 1989,
    "electricity_available": True,
    "chilled_water_available": True,
    "water_available": True
}


# ==================================================
# 2. ELECTRICITY BASELINE
# ==================================================

average_demand = df[target].mean()

peak_demand = df[target].max()

minimum_demand = df[target].min()

median_demand = df[target].median()


# ==================================================
# 3. HOURLY PROFILE
# ==================================================

hourly_profile = (
    df.groupby("hour")[target]
    .mean()
    .reset_index()
)

hourly_profile.columns = [
    "hour",
    "average_electricity"
]


# ==================================================
# 4. WEEKDAY VS WEEKEND
# ==================================================

weekday_demand = df[df["is_weekend"] == 0][target].mean()

weekend_demand = df[df["is_weekend"] == 1][target].mean()


# ==================================================
# 5. TEMPERATURE BASELINE
# ==================================================

average_temperature = df["airTemperature"].mean()


# ==================================================
# 6. DISPLAY BASELINE
# ==================================================

print("\n========================================")
print("       NEXUS DIGITAL TWIN BASELINE")
print("========================================")

print("\nBUILDING INFORMATION")
print("----------------------------------------")

for key, value in building_info.items():
    print(f"{key}: {value}")


print("\nELECTRICITY BASELINE")
print("----------------------------------------")

print(f"Average demand : {average_demand:.2f}")
print(f"Median demand  : {median_demand:.2f}")
print(f"Peak demand    : {peak_demand:.2f}")
print(f"Minimum demand : {minimum_demand:.2f}")


print("\nOPERATING PROFILE")
print("----------------------------------------")

print(f"Weekday average : {weekday_demand:.2f}")
print(f"Weekend average : {weekend_demand:.2f}")


print("\nWEATHER BASELINE")
print("----------------------------------------")

print(f"Average temperature : {average_temperature:.2f}")


print("\nHOURLY ELECTRICITY PROFILE")
print("----------------------------------------")

print(hourly_profile.to_string(index=False))


# ==================================================
# 7. SAVE BASELINE DATA
# ==================================================

hourly_profile.to_csv(
    "baseline_hourly_profile.csv",
    index=False
)

print("\nBaseline profile saved:")
print("baseline_hourly_profile.csv")

print("\nNEXUS BASELINE CREATED SUCCESSFULLY")