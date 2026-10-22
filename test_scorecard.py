
from src.risk_engine import (
    load_data,
    filter_records,
    get_risk_scorecard,
)

def main():
    df = load_data()
    filtered_df = filter_records(
        df,
        country="All",
        crop="All",
    )

    scorecard = get_risk_scorecard(filtered_df)

    print("\nAGRIRISK AI — RISK SCORECARD")
    print("=" * 40)
    print(f"Records analyzed: {scorecard['records']:,}")
    print(
        "High/Critical records: "
        f"{scorecard['high_critical_percent']:.2f}%"
    )

    print("\nRisk distribution:")
    print(scorecard["risk_distribution"])

    print("\nIndicator averages:")
    print(scorecard["indicator_averages"])

    print("\nTop recorded actions:")
    print(scorecard["top_actions"])


if __name__ == "__main__":
    main()


