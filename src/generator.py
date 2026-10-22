
from src.retriever import AdvisoryRetriever
from src.risk_engine import load_data, filter_records


retriever = AdvisoryRetriever()


INDICATORS = {
    "climate_stress_index": (
        "climate stress",
        "heat",
        "temperature",
        "weather",
        "drought",
    ),
    "disease_risk_score": (
        "disease",
        "crop infection",
        "fungus",
        "fungal",
    ),
    "pest_risk_score": (
        "pest",
        "insect",
        "infestation",
    ),
    "soil_moisture_percent": (
        "soil moisture",
        "dry soil",
        "water stress",
    ),
    "annual_rainfall_mm": (
        "rainfall",
        "precipitation",
    ),
}


def generate_answer(query, country="All", crop="All", top_k=3):
    """Generate a dataset-aware advisory with structured citations."""

    query = query.strip()

    if not query:
        return {
            "answer": "Please enter an agricultural risk question.",
            "citations": [],
        }

    # Retrieve the most relevant local advisory documents.
    retrieved_docs = retriever.retrieve(query, top_k=top_k)

    # Load and filter the agricultural dataset.
    df = load_data()
    filtered_df = filter_records(
        df,
        country=country,
        crop=crop,
    )

    if filtered_df.empty:
        return {
            "answer": (
                "No dataset records match the selected country and crop. "
                "Please change the filters and try again."
            ),
            "citations": [],
        }

    query_lower = query.lower()

    lines = [
        "### Agricultural Risk Analysis",
        "",
        f"**Question:** {query}",
        "",
        "#### Dataset context",
        f"- Records analyzed: {len(filtered_df):,}",
        f"- Country filter: {country}",
        f"- Crop filter: {crop}",
        "",
        "> The following statistics describe records in the dataset, "
        "not necessarily current farm conditions.",
    ]

    # Identify indicators relevant to the question.
    relevant_columns = [
        column
        for column, terms in INDICATORS.items()
        if column in filtered_df.columns
        and any(term in query_lower for term in terms)
    ]

    if relevant_columns:
        lines.extend(["", "#### Relevant recorded indicators"])

        for column in relevant_columns:
            values = filtered_df[column].dropna()

            if values.empty:
                continue

            value = values.mean()
            label = column.replace("_", " ").title()

            if column == "soil_moisture_percent":
                formatted_value = f"{value:.2f}%"
            elif column == "annual_rainfall_mm":
                formatted_value = f"{value:.2f} mm"
            else:
                formatted_value = f"{value:.2f}"

            lines.append(f"- Average {label}: {formatted_value}")

    # Show the distribution of recorded risk categories.
    if "risk_category" in filtered_df.columns:
        counts = filtered_df["risk_category"].value_counts()

        lines.extend(["", "#### Recorded risk categories"])

        for category in ("Critical", "High", "Moderate", "Low"):
            count = int(counts.get(category, 0))

            if count:
                percentage = count / len(filtered_df) * 100
                lines.append(
                    f"- {category}: {count:,} records ({percentage:.1f}%)"
                )

    # Show the most frequently recorded recommended actions.
    if "recommended_action" in filtered_df.columns:
        action_counts = (
            filtered_df["recommended_action"]
            .dropna()
            .astype(str)
            .value_counts()
            .head(3)
        )

        if not action_counts.empty:
            lines.extend(["", "#### Frequently recorded actions"])

            for action, count in action_counts.items():
                lines.append(f"- {action} ({count:,} records)")

    # Add retrieved guidance and structured citations.
    citations = []

    lines.extend(["", "#### Retrieved agricultural guidance"])

    if retrieved_docs:
        for index, doc in enumerate(retrieved_docs, start=1):
            doc_id = doc.get("id", f"AGRI-{index:03d}")
            topic = doc.get("topic", "Agricultural guidance")
            source = doc.get(
                "source",
                "Local starter guidance; requires verification.",
            )
            source_url = doc.get("url", "")
            score = float(
                doc.get("similarity", doc.get("score", 0.0))
            )
            guidance_text = doc.get("text", "").strip()

            lines.extend([
                "",
                f"**{index}. {topic} ({doc_id})**",
                guidance_text or "No guidance text available.",
                f"- Source: {source}",
                f"- Retrieval similarity: {score:.1%}",
            ])

            if source_url.startswith(("https://", "http://")):
                lines.append(f"- Reference: {source_url}")

            citations.append({
                "id": doc_id,
                "topic": topic,
                "source": source,
                "url": source_url,
                "similarity": score,
                "text": guidance_text,
            })
    else:
        lines.append(
            "No relevant local guidance documents were retrieved. "
            "Try rephrasing the question."
        )

    lines.extend([
        "",
        "---",
        "**Important limitations**",
        "- Dataset statistics are descriptive, not validated predictions.",
        "- Retrieval similarity measures textual relevance, not factual accuracy.",
        "- Local starter guidance must be checked against verified "
        "agricultural sources before practical use.",
    ])

    return {
        "answer": "\n".join(lines),
        "citations": citations,
    }


if __name__ == "__main__":
    result = generate_answer(
        "What steps can help manage high pest risk?",
        country="All",
        crop="All",
    )

    print(result["answer"])
    print("\nStructured citations:")
    for citation in result["citations"]:
        print(citation)


