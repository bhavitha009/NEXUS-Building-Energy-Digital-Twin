import pandas as pd

df = pd.read_csv("panther_electricity.csv")

col = "Panther_education_Vincent"

df["timestamp"] = pd.to_datetime(df["timestamp"])

print("BUILDING:", col)
print("START:", df["timestamp"].min())
print("END:", df["timestamp"].max())

print("\nSTATISTICS")
print("Minimum:", df[col].min())
print("Maximum:", df[col].max())
print("Mean:", df[col].mean())
print("Median:", df[col].median())

print("\nZERO VALUES:", (df[col] == 0).sum())
print("MISSING VALUES:", df[col].isna().sum())

print("\nTOP 10 HIGHEST VALUES")
print(df.nlargest(10, col)[["timestamp", col]])

print("\nSAMPLE NON-ZERO VALUES")
print(df[df[col] > 0].head(10))