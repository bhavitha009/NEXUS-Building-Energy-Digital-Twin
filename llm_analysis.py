
import pandas as pd

# ============================================================
# NEXUS - CONTROLLED AI-ASSISTED SCENARIO ANALYSIS
# ============================================================

print("\n" + "=" * 55)
print("NEXUS AI ANALYSIS")
print("=" * 55)

# 1. LOAD IMPACT RESULTS

FILE = "impact_analysis.csv"

df = pd.read_csv(FILE)

required_columns = [
    "Scenario",
    "Scenario_Type",
    "Average_Demand",
    "Demand_Savings_Percent",
    "Impact_Category",
    "Sustainability_Score",
    "Scenario_Status"
]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    raise ValueError(f"Missing columns in impact_analysis.csv: {missing}")

# 2. GET BASELINE

baseline_rows = df[df["Scenario"] == "Baseline"]

if baseline_rows.empty:
    raise ValueError("Baseline scenario not found.")

baseline = baseline_rows.iloc[0]
baseline_demand = float(baseline["Average_Demand"])

# 3. SELECT BEST ELIGIBLE INTERVENTION
# Exclude baseline and weather sensitivity.
eligible = df[
    ~df["Scenario_Type"].isin(
        ["Reference", "Weather Sensitivity"]
    )
].copy()

if eligible.empty:
    raise ValueError("No eligible intervention scenarios found.")

best = eligible.loc[
    eligible["Sustainability_Score"].idxmax()
]

scenario_name = best["Scenario"]
scenario_type = best["Scenario_Type"]
scenario_demand = float(best["Average_Demand"])
savings = float(best["Demand_Savings_Percent"])
impact = best["Impact_Category"]
score = float(best["Sustainability_Score"])
status = best["Scenario_Status"]

# 4. CREATE ENGINEERED PROMPT

prompt = f"""
You are a building sustainability analyst.

Analyze the following building-level Digital Twin simulation.

BUILDING:
Panther_education_Vincent
Building type: Education / Classroom

BASELINE:
Average predicted electricity demand: {baseline_demand:.2f}

SELECTED SCENARIO:
Scenario: {scenario_name}
Scenario type: {scenario_type}
Average predicted electricity demand: {scenario_demand:.2f}
Demand savings relative to baseline: {savings:.2f}%
Impact category: {impact}
Sustainability heuristic score: {score:.1f}/100
Scenario status: {status}

TASK:
1. Explain the scenario's impact on predicted electricity demand.
2. Compare the scenario with the baseline.
3. Explain the meaning of the sustainability heuristic score.
4. Give one practical recommendation.

CONSTRAINTS:
- Use only the supplied numerical values.
- Do not invent cost, carbon, or occupancy measurements.
- Do not claim simulated savings are measured real-world savings.
- Explain that the sustainability score is a heuristic.
- Clearly distinguish simulation assumptions from model predictions.
"""

print("\nENGINEERED PROMPT")
print("-" * 55)
print(prompt)

# 5. GENERATE CONTROLLED EXPLANATION

if savings > 0:

    explanation = (
        f"The {scenario_name} scenario reduces the average "
        f"predicted electricity demand from {baseline_demand:.2f} "
        f"to {scenario_demand:.2f}. This represents a simulated "
        f"demand reduction of {savings:.2f}% compared with "
        f"the baseline."
    )

elif savings < 0:

    explanation = (
        f"The {scenario_name} scenario increases average "
        f"predicted electricity demand from {baseline_demand:.2f} "
        f"to {scenario_demand:.2f}. This represents a "
        f"{abs(savings):.2f}% increase compared with the baseline."
    )

else:

    explanation = (
        "The selected scenario produces approximately the same "
        "average predicted electricity demand as the baseline."
    )

if scenario_type == "Efficiency":

    recommendation = (
        "Evaluate practical energy-efficiency measures such as "
        "efficient lighting, cooling-system optimization, and "
        "equipment upgrades. Actual savings should be measured "
        "before confirming the intervention's effectiveness."
    )

elif scenario_type == "Operating Hours":

    recommendation = (
        "Review after-hours electricity usage and consider "
        "switching off or scheduling non-essential equipment "
        "when the building is not in active use."
    )

elif scenario_type == "Peak Management":

    recommendation = (
        "Review high-demand operating periods and consider "
        "staggering non-essential equipment operation to "
        "reduce simultaneous electricity demand."
    )

elif scenario_type == "Combined":

    recommendation = (
        "Evaluate a combination of building-wide efficiency "
        "measures and after-hours equipment scheduling. "
        "Validate each intervention using actual consumption data."
    )

else:

    recommendation = (
        "Further evaluate the intervention using additional "
        "building performance measurements before implementation."
    )

# 6. BUILD FINAL REPORT

result = f"""
NEXUS - BUILDING ENERGY SCENARIO ANALYSIS
========================================

BUILDING
--------
Panther_education_Vincent
Type: Education / Classroom

BASELINE
--------
Average predicted demand: {baseline_demand:.2f}

SELECTED SCENARIO
-----------------
Scenario: {scenario_name}
Scenario type: {scenario_type}
Average predicted demand: {scenario_demand:.2f}
Simulated demand savings: {savings:.2f}%

SCENARIO IMPACT
---------------
{explanation}

IMPACT CATEGORY
---------------
{impact}

SUSTAINABILITY HEURISTIC SCORE
------------------------------
{score:.1f}/100

The score is a heuristic decision-support indicator,
not an independently measured sustainability rating.

RECOMMENDATION
--------------
{recommendation}

SCENARIO LIMITATIONS
--------------------
Scenario status: {status}

The reported reduction is based on the scenario simulation
and its stated assumptions. It is not verified real-world
energy savings.

No cost, carbon, or occupancy measurements are inferred.
"""

# 7. DISPLAY RESULT

print("\n" + "=" * 55)
print("FINAL NEXUS AI-ASSISTED ANALYSIS")
print("=" * 55)
print(result)

# 8. SAVE OUTPUT

with open("llm_analysis.txt", "w", encoding="utf-8") as file:
    file.write("ENGINEERED PROMPT\n")
    file.write("=" * 55)
    file.write("\n")
    file.write(prompt)
    file.write("\n\n")
    file.write(result)

print("\nAnalysis saved to llm_analysis.txt")
print("\nNEXUS AI ANALYSIS COMPLETED")
