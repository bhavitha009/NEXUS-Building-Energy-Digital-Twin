
import pandas as pd

# ============================================================
# NEXUS - PROMPT ENGINEERING COMPARISON
# ============================================================

print("\n" + "=" * 55)
print("NEXUS PROMPT ENGINEERING")
print("=" * 55)

# 1. LOAD IMPACT RESULTS

df = pd.read_csv("impact_analysis.csv")

baseline_rows = df[df["Scenario"] == "Baseline"]

scenario_rows = df[
    df["Scenario"] == "Efficiency +15%"
]

if baseline_rows.empty or scenario_rows.empty:
    raise ValueError(
        "Baseline or Efficiency +15% scenario not found."
    )

baseline = baseline_rows.iloc[0]
scenario = scenario_rows.iloc[0]

baseline_demand = float(baseline["Average_Demand"])
scenario_demand = float(scenario["Average_Demand"])
change = float(scenario["Demand_Savings_Percent"])
score = float(scenario["Sustainability_Score"])

# 2. PROMPT 1 - BASIC

prompt_1 = f"""
Explain this building electricity scenario.

Baseline demand: {baseline_demand:.2f}
Scenario demand: {scenario_demand:.2f}
Demand savings: {change:.2f}%
"""

# 3. PROMPT 2 - STRUCTURED

prompt_2 = f"""
Analyze the following building energy scenario.

Building: Panther_education_Vincent

Baseline average demand: {baseline_demand:.2f}

Scenario: Efficiency +15%
Scenario average demand: {scenario_demand:.2f}
Demand savings compared with baseline: {change:.2f}%

Explain:
1. The impact of the scenario.
2. Whether predicted energy performance improves.
3. One practical sustainability recommendation.
"""

# 4. PROMPT 3 - ENGINEERED

prompt_3 = f"""
ROLE:
You are a building sustainability analyst.

CONTEXT:
Analyze a building-level Digital Twin simulation
for Panther_education_Vincent, an education building.

BASELINE:
Average predicted electricity demand = {baseline_demand:.2f}

SCENARIO:
Intervention = Efficiency +15%
Average predicted electricity demand = {scenario_demand:.2f}
Demand savings relative to baseline = {change:.2f}%
Sustainability heuristic score = {score:.1f}/100

TASKS:
1. Explain the scenario's impact.
2. Compare predicted demand with the baseline.
3. Explain the sustainability score.
4. Give ONE practical sustainability recommendation.
5. Explain why the recommendation is useful.

CONSTRAINTS:
- Use only the supplied values.
- Do not invent cost values.
- Do not invent carbon emission values.
- Do not invent occupancy measurements.
- Do not introduce unsupported numerical values.
- Clearly distinguish simulation assumptions from measured results.
- Explain that the sustainability score is heuristic.
- Do not claim that simulated savings are verified real-world savings.
"""

# 5. DISPLAY PROMPTS

prompts = [
    ("PROMPT 1 - BASIC", prompt_1),
    ("PROMPT 2 - STRUCTURED", prompt_2),
    ("PROMPT 3 - ENGINEERED", prompt_3)
]

for title, prompt in prompts:

    print("\n" + title)
    print("-" * 55)
    print(prompt)

# 6. SAVE PROMPT COMPARISON

with open(
    "prompt_comparison.txt",
    "w",
    encoding="utf-8"
) as file:

    for title, prompt in prompts:

        file.write("\n" + title + "\n")
        file.write("-" * 55 + "\n")
        file.write(prompt)
        file.write("\n\n")

print("\n" + "=" * 55)
print("PROMPT ENGINEERING COMPLETED")
print("=" * 55)
print("Output file: prompt_comparison.txt")
