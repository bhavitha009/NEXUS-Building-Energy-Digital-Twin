
import pandas as pd
import numpy as np

# ============================================================
# NEXUS - ELECTRICITY SCENARIO IMPACT ANALYSIS
# ============================================================

print("\n==============================================")
print(" NEXUS ELECTRICITY SCENARIO IMPACT ANALYSIS")
print("==============================================")

# 1. LOAD SCENARIO RESULTS

INPUT_FILE = "scenario_results.csv"
OUTPUT_FILE = "impact_analysis.csv"

df = pd.read_csv(INPUT_FILE)

required_columns = [
    "Scenario",
    "Average_Demand",
    "Change_From_Baseline_Percent"
]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    raise ValueError(f"Missing columns in scenario results: {missing}")

if df["Scenario"].duplicated().any():
    raise ValueError("Duplicate scenario names found.")

# 2. IDENTIFY BASELINE

baseline_rows = df[df["Scenario"] == "Baseline"]

if len(baseline_rows) != 1:
    raise ValueError("Exactly one Baseline scenario is required.")

baseline_demand = float(
    baseline_rows.iloc[0]["Average_Demand"]
)

if not np.isfinite(baseline_demand) or baseline_demand <= 0:
    raise ValueError("Baseline demand must be a positive number.")

print("\nBASELINE")
print("----------------------------------------------")
print(f"Baseline average demand: {baseline_demand:.2f}")

# 3. CALCULATE IMPACT METRICS

df["Demand_Difference"] = (
    df["Average_Demand"] - baseline_demand
)

df["Demand_Change_Percent"] = (
    df["Demand_Difference"] / baseline_demand
) * 100

df["Demand_Savings"] = (
    baseline_demand - df["Average_Demand"]
)

df["Demand_Savings_Percent"] = (
    df["Demand_Savings"] / baseline_demand
) * 100

df["Relative_Energy_Impact"] = (
    df["Average_Demand"] / baseline_demand
)

# 4. CLASSIFY SCENARIO TYPE

if "Scenario_Type" not in df.columns:
    df["Scenario_Type"] = "Unclassified"

def identify_status(row):

    if row["Scenario"] == "Baseline":
        return "Reference"

    if row["Scenario_Type"] == "Weather Sensitivity":
        return "Model-Based Sensitivity"

    return "Assumption-Based Simulation"

df["Scenario_Status"] = df.apply(
    identify_status,
    axis=1
)

# 5. CLASSIFY IMPACT

def classify_impact(change):

    if np.isclose(change, 0, atol=1e-9):
        return "Baseline"

    elif change < -10:
        return "High Positive Impact"

    elif change < 0:
        return "Positive Impact"

    elif change <= 5:
        return "Low Negative Impact"

    else:
        return "High Negative Impact"

df["Impact_Category"] = (
    df["Demand_Change_Percent"].apply(classify_impact)
)

# 6. HEURISTIC DECISION-SUPPORT SCORE

# This is NOT a measured sustainability score.
# It is a transparent, illustrative score based only
# on simulated demand reduction.
#
# Baseline = 50
# Every 1% demand reduction adds 2 points.
# Every 1% demand increase subtracts 2 points.

df["Sustainability_Score"] = np.clip(
    50 + 2 * df["Demand_Savings_Percent"],
    0,
    100
)

df["Score_Method"] = (
    "Heuristic: 50 + 2 x demand savings percentage; "
    "clipped to 0-100"
)

# 7. RANK SIMULATED INTERVENTIONS

# Weather sensitivity is excluded because it is not
# an energy-saving intervention.

intervention_types = [
    "Efficiency",
    "Operating Hours",
    "Peak Management",
    "Combined"
]

interventions = df[
    (df["Scenario"] != "Baseline")
    & (df["Scenario_Type"].isin(intervention_types))
].copy()

if not interventions.empty:

    interventions["Rank"] = (
        interventions["Demand_Savings_Percent"]
        .rank(
            ascending=False,
            method="min"
        )
        .astype(int)
    )

    df["Rank"] = np.nan

    df.loc[
        interventions.index,
        "Rank"
    ] = interventions["Rank"]

else:
    df["Rank"] = np.nan

# 8. DISPLAY COMPLETE SCENARIO ANALYSIS

display_columns = [
    "Scenario",
    "Scenario_Type",
    "Scenario_Status",
    "Average_Demand",
    "Demand_Savings_Percent",
    "Impact_Category",
    "Sustainability_Score",
    "Rank"
]

print("\nSCENARIO IMPACT ANALYSIS")
print("----------------------------------------------")

print(
    df[display_columns].to_string(
        index=False,
        formatters={
            "Average_Demand": "{:.2f}".format,
            "Demand_Savings_Percent": "{:+.2f}%".format,
            "Sustainability_Score": "{:.1f}".format,
            "Rank": lambda x: "-" if pd.isna(x) else str(int(x))
        }
    )
)

# 9. IDENTIFY BEST SIMULATED INTERVENTION

print("\nBEST SIMULATED INTERVENTION")
print("----------------------------------------------")

if not interventions.empty:

    best_scenario = interventions.loc[
        interventions["Demand_Savings_Percent"].idxmax()
    ]

    print("Scenario :", best_scenario["Scenario"])

    print(
        f"Average demand : "
        f"{best_scenario['Average_Demand']:.2f}"
    )

    print(
        f"Demand reduction : "
        f"{best_scenario['Demand_Savings_Percent']:.2f}%"
    )

    print(
        f"Heuristic score : "
        f"{best_scenario['Sustainability_Score']:.1f}/100"
    )

    print(
        "\nNote: This is the best result among the "
        "current assumption-based simulations."
    )

else:
    print("No eligible intervention scenarios found.")

# 10. SAVE RESULTS

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n==============================================")
print("IMPACT ANALYSIS COMPLETED")
print("==============================================")

print("Total scenarios analysed:", len(df))
print("Output file:", OUTPUT_FILE)

print("\nNEXUS IMPACT ANALYSIS COMPLETED")
