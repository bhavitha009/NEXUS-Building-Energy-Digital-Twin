import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

file_path = r"C:\Users\USER\Downloads\building-data-genome-project-2-v1.0\buds-lab-building-data-genome-project-2-3d0cbaf\data\meters\cleaned\electricity_cleaned.csv"

df = pd.read_csv(file_path, nrows=5)

building = "Panther_education_Vincent"

if building in df.columns:
    print("YES - Building found!")
    print("Building:", building)
else:
    print("NO - Building not found.")

print("\nNumber of columns:", len(df.columns))
print("Number of building columns:", len(df.columns) - 1)