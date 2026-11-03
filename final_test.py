import os
import pandas as pd

print("=" * 50)
print("          NEXUS FINAL SYSTEM TEST")
print("=" * 50)

files = [
    "panther_ml_dataset.csv",
    "random_forest_model.pkl",
    "model_results.csv",
    "baseline_hourly_profile.csv",
    "scenario_results.csv",
    "impact_analysis.csv",
    "llm_analysis.txt",
    "prompt_comparison.txt",
    "actual_vs_predicted.png",
    "scenario_comparison.png",
    "feature_importance.png"
]

print("\nFILE CHECK")
print("-" * 50)

all_ok = True

for file in files:
    if os.path.exists(file):
        print(f"[OK] {file}")
    else:
        print(f"[MISSING] {file}")
        all_ok = False

print("\nMODEL PERFORMANCE")
print("-" * 50)

results = pd.read_csv("model_results.csv")
print(results.to_string(index=False))

print("\nSCENARIO RESULTS")
print("-" * 50)

scenarios = pd.read_csv("scenario_results.csv")
print(scenarios.to_string(index=False))

print("\nBEST SCENARIO")
print("-" * 50)

impact = pd.read_csv("impact_analysis.csv")

best = impact.loc[
    impact["Sustainability_Score"].idxmax()
]

print("Scenario :", best["Scenario"])
print("Average demand :", best["Average_Demand"])
print("Change :", best["Demand_Change_Percent"])
print("Sustainability score :", best["Sustainability_Score"])

print("\n" + "=" * 50)

if all_ok:
    print("NEXUS SYSTEM TEST: PASSED")
else:
    print("NEXUS SYSTEM TEST: CHECK MISSING FILES")

print("=" * 50)