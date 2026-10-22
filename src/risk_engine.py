
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "agriculture_risk_dataset.csv"

RISK_ORDER = ["Low", "Moderate", "High", "Critical"]

REQUIRED_COLUMNS = [
    "country",
    "crop",
    "climate_stress_index",
    "disease_risk_score",
    "pest_risk_score",
    "risk_category",
    "recommended_action",
]


def load_data():
    """Load and validate the agricultural dataset."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}\n"
            "Check that the CSV is inside the project's data folder."
        )

    df = pd.read_csv(DATA_PATH)

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required dataset columns: {missing}")

    for column in df.select_dtypes(include=["object"]).columns:
        df[column] = df[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )

    df["risk_category"] = (
        df["risk_category"].astype("string").str.strip().str.title()
    )

    numeric_columns = [
        "climate_stress_index",
        "disease_risk_score",
        "pest_risk_score",
        "soil_moisture_percent",
        "annual_rainfall_mm",
        "yield_ton_per_ha",
        "production_tons",
        "profit_usd",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


def filter_records(df, country="All", crop="All"):
    """Filter records by country and crop."""
    result = df.copy()

    if country and country != "All":
        result = result[
            result["country"].astype(str).str.casefold()
            == str(country).casefold()
        ]

    if crop and crop != "All":
        result = result[
            result["crop"].astype(str).str.casefold()
            == str(crop).casefold()
        ]

    return result


def get_summary(df):
    """Return summary metrics expected by the dashboard."""

    def mean_value(column):
        if column not in df.columns:
            return 0.0
        value = pd.to_numeric(df[column], errors="coerce").mean()
        return round(float(value), 2) if pd.notna(value) else 0.0

    risk_distribution = (
        df["risk_category"].value_counts().reindex(
            RISK_ORDER, fill_value=0
        ).to_dict()
        if "risk_category" in df.columns
        else {}
    )

    top_actions = (
        df["recommended_action"].dropna().astype(str)
        .value_counts().head(5).to_dict()
        if "recommended_action" in df.columns
        else {}
    )

    return {
        "records": len(df),
        "avg_climate_stress": mean_value("climate_stress_index"),
        "avg_disease_risk": mean_value("disease_risk_score"),
        "avg_pest_risk": mean_value("pest_risk_score"),
        "risk_distribution": risk_distribution,
        "top_actions": top_actions,
    }


def get_similar_records(df, country="All", crop="All", limit=5):
    """Return a sample of records matching the selected filters."""
    return filter_records(df, country, crop).head(max(0, int(limit)))


def get_risk_scorecard(df):
    """Summarize recorded risk categories and indicator averages."""

    if df.empty:
        return {
            "records": 0,
            "high_critical_percent": 0.0,
            "risk_distribution": {},
            "indicator_averages": {},
            "top_actions": {},
        }

    records = len(df)

    distribution = (
        df["risk_category"].value_counts()
        .reindex(RISK_ORDER, fill_value=0).to_dict()
        if "risk_category" in df.columns
        else {}
    )

    high_critical = sum(
        distribution.get(category, 0)
        for category in ("High", "Critical")
    )

    indicators = {
        "Climate stress": "climate_stress_index",
        "Disease risk": "disease_risk_score",
        "Pest risk": "pest_risk_score",
    }

    averages = {}
    for label, column in indicators.items():
        if column in df.columns:
            value = pd.to_numeric(df[column], errors="coerce").mean()
            if pd.notna(value):
                averages[label] = round(float(value), 2)

    actions = (
        df["recommended_action"].dropna().astype(str)
        .value_counts().head(5).to_dict()
        if "recommended_action" in df.columns
        else {}
    )

    return {
        "records": records,
        "high_critical_percent": round(high_critical / records * 100, 2),
        "risk_distribution": distribution,
        "indicator_averages": averages,
        "top_actions": actions,
    }


if __name__ == "__main__":
    data = load_data()
    summary = get_summary(data)
    scorecard = get_risk_scorecard(data)

    print("AGRIRISK AI — RISK ENGINE TEST")
    print("=" * 40)
    print(f"Dataset records: {summary['records']:,}")
    print(f"Average climate stress: {summary['avg_climate_stress']}")
    print(f"Average disease risk: {summary['avg_disease_risk']}")
    print(f"Average pest risk: {summary['avg_pest_risk']}")
    print(f"High/Critical records: {scorecard['high_critical_percent']}%")
    print("Risk distribution:", scorecard["risk_distribution"])


