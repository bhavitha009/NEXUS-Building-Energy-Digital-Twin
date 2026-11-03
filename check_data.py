import pandas as pd

df = pd.read_csv("panther_training_data.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

target = "Panther_education_Vincent"

print("TOTAL ROWS:", len(df))

print("\nDUPLICATE TIMESTAMPS:")
print(df["timestamp"].duplicated().sum())

print("\nMISSING ELECTRICITY VALUES:")
print(df[target].isna().sum())

print("\nTIMESTAMP DIFFERENCES:")
print(df["timestamp"].diff().value_counts().head(10))

print("\nMISSING HOURLY TIMESTAMPS:")
full_range = pd.date_range(
    start=df["timestamp"].min(),
    end=df["timestamp"].max(),
    freq="h"
)

missing_timestamps = full_range.difference(df["timestamp"])

print("Missing timestamps:", len(missing_timestamps))
print(missing_timestamps[:10])
# Check duplicate timestamp records
print("\nDUPLICATE TIMESTAMP RECORDS:")

duplicates = df[df["timestamp"].duplicated(keep=False)]

print(
    duplicates.sort_values("timestamp").to_string(index=False)
)

# Check readings around missing hourly timestamps
print("\nDATA AROUND MISSING HOURS:")

for missing_time in missing_timestamps:
    print(f"\nAround {missing_time}:")

    start = missing_time - pd.Timedelta(hours=2)
    end = missing_time + pd.Timedelta(hours=2)

    print(
        df[
            (df["timestamp"] >= start) &
            (df["timestamp"] <= end)
        ][["timestamp", target]].to_string(index=False)
    )