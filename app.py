
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

SCENARIO_FILE = BASE_DIR / "scenario_results.csv"
IMPACT_FILE = BASE_DIR / "impact_analysis.csv"
PREDICTION_FILE = BASE_DIR / "test_predictions.csv"
FEATURE_FILE = BASE_DIR / "feature_importance_final.csv"
AI_FILE = BASE_DIR / "llm_analysis.txt"


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="NEXUS Digital Twin API",
    description="Building-level electricity demand and scenario analysis API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# DATA HELPERS
# --------------------------------------------------

def load_csv(file_path):
    if not file_path.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Required project file not found: {file_path.name}"
        )

    try:
        return pd.read_csv(file_path)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Could not read {file_path.name}: {str(error)}"
        )


def clean_records(dataframe):
    records = dataframe.to_dict(orient="records")

    return [
        {
            key: None if pd.isna(value) else value
            for key, value in record.items()
        }
        for record in records
    ]


def get_best_scenario():
    impacts = load_csv(IMPACT_FILE)

    eligible = impacts[
        impacts["Scenario_Status"] == "Assumption-Based Simulation"
    ].copy()

    eligible["Rank"] = pd.to_numeric(
        eligible["Rank"], errors="coerce"
    )

    eligible = eligible.dropna(subset=["Rank"])

    if eligible.empty:
        return None

    best = eligible.sort_values("Rank").iloc[0]

    return clean_records(pd.DataFrame([best]))[0]


# --------------------------------------------------
# REQUEST MODEL
# --------------------------------------------------

class SimulationRequest(BaseModel):
    scenario_name: str


# --------------------------------------------------
# API ROUTES
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "project": "NEXUS Digital Twin",
        "message": "Backend API is running",
        "documentation": "/docs"
    }


@app.get("/api/health")
def health():
    required_files = {
        "scenario_results": SCENARIO_FILE,
        "impact_analysis": IMPACT_FILE,
        "test_predictions": PREDICTION_FILE,
        "feature_importance": FEATURE_FILE
    }

    status = {
        name: path.exists()
        for name, path in required_files.items()
    }

    return {
        "status": "healthy" if all(status.values()) else "missing_files",
        "files": status
    }


@app.get("/api/building")
def building():
    return {
        "building_name": "Panther Education - Vincent",
        "building_type": "Education",
        "site": "Panther",
        "area_sqm": 11248.1,
        "resource": "Electricity",
        "dataset_period": "2016-01-01 to 2017-12-31"
    }


@app.get("/api/baseline")
def baseline():
    scenarios = load_csv(SCENARIO_FILE)

    row = scenarios[
        scenarios["Scenario"] == "Baseline"
    ]

    if row.empty:
        raise HTTPException(
            status_code=404,
            detail="Baseline scenario not found"
        )

    return clean_records(row)[0]


@app.get("/api/scenarios")
def scenarios():
    dataframe = load_csv(SCENARIO_FILE)

    return {
        "total_scenarios": len(dataframe),
        "scenarios": clean_records(dataframe)
    }


@app.post("/api/simulate")
def simulate(request: SimulationRequest):
    dataframe = load_csv(SCENARIO_FILE)

    selected = dataframe[
        dataframe["Scenario"].str.lower()
        == request.scenario_name.strip().lower()
    ]

    if selected.empty:
        raise HTTPException(
            status_code=404,
            detail="Scenario not found. Choose an existing scenario."
        )

    return {
        "message": "Precomputed scenario retrieved successfully",
        "simulation_type": "Precomputed assumption-based result",
        "result": clean_records(selected)[0]
    }


@app.get("/api/insights")
def insights():
    best = get_best_scenario()

    explanation = ""

    if AI_FILE.exists():
        explanation = AI_FILE.read_text(encoding="utf-8")

    return {
        "best_scenario": best,
        "explanation": explanation,
        "explanation_type": "Controlled project analysis",
        "warning": (
            "Scenario reductions are assumptions, not verified "
            "real-world energy savings. Sustainability scores are heuristic."
        )
    }


@app.get("/api/best-scenario")
def best_scenario():
    best = get_best_scenario()

    if best is None:
        raise HTTPException(
            status_code=404,
            detail="No ranked intervention found"
        )

    return best


@app.get("/api/predictions")
def predictions(limit: int = 2583):
    if limit < 1 or limit > 2583:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 2583"
        )

    dataframe = load_csv(PREDICTION_FILE)

    return {
        "total_records": len(dataframe),
        "returned_records": min(limit, len(dataframe)),
        "predictions": clean_records(dataframe.head(limit))
    }


@app.get("/api/features")
def features():
    dataframe = load_csv(FEATURE_FILE)

    dataframe = dataframe.sort_values(
        "Importance", ascending=False
    )

    return {
        "features": clean_records(dataframe)
    }


@app.get("/api/impact-analysis")
def impact_analysis():
    dataframe = load_csv(IMPACT_FILE)

    return {
        "total_scenarios": len(dataframe),
        "results": clean_records(dataframe)
    }
