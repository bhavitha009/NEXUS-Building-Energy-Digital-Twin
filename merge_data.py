import pandas as pd

# Load electricity data
electricity = pd.read_csv("panther_electricity.csv")

# Load weather data
weather = pd.read_csv("panther_weather.csv")

# Convert timestamps
electricity["timestamp"] = pd.to_datetime(electricity["timestamp"])
weather["timestamp"] = pd.to_datetime(weather["timestamp"])

# Merge using timestamp
df = pd.merge(
    electricity,
    weather,
    on="timestamp",
    how="inner"
)

# Save merged dataset
df.to_csv("panther_training_data.csv", index=False)

print("MERGED DATASET CREATED")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nCOLUMNS:")
print(df.columns.tolist())

print("\nMISSING VALUES:")
print(df.isna().sum())

print("\nFIRST 5 ROWS:")
print(df.head())