import pandas as pd

from sklearn.ensemble import RandomForestRegressor

# Load ML dataset
df = pd.read_csv("panther_ml_dataset.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"])

target = "Panther_education_Vincent"

# Same features used during training
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

# Same chronological split
split_index = int(len(df) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

# Train Random Forest
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

print("Training Random Forest...")
model.fit(X_train, y_train)

# Feature importance
importance = pd.DataFrame({
    "Feature": features,
    "Importance": model.feature_importances_
})

importance = importance.sort_values(
    "Importance",
    ascending=False
)

print("\n==============================")
print("FEATURE IMPORTANCE")
print("==============================")

print(importance.to_string(index=False))

# Save results
importance.to_csv("feature_importance.csv", index=False)

print("\nSaved: feature_importance.csv")