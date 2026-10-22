
from pathlib import Path
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_PATH = PROJECT_ROOT / "docs" / "agricultural_advisories.txt"


def load_documents():
    """Load advisory documents and extract their metadata."""
    if not DOCS_PATH.exists():
        raise FileNotFoundError(
            f"Advisory document file not found: {DOCS_PATH}"
        )

    text = DOCS_PATH.read_text(encoding="utf-8")
    chunks = re.split(r"(?=Document ID: )", text.strip())

    documents = []

    for chunk in chunks:
        chunk = chunk.strip()

        if not chunk.startswith("Document ID:"):
            continue

        match = re.search(r"^Document ID:\s*(.+)$", chunk, re.MULTILINE)
        doc_id = match.group(1).strip() if match else "UNKNOWN"

        topic_match = re.search(
            r"^Topic:\s*(.+)$", chunk, re.MULTILINE
        )
        source_match = re.search(
            r"^Source:\s*(.+)$", chunk, re.MULTILINE
        )
        url_match = re.search(
            r"^Source URL:\s*(\S+)", chunk, re.MULTILINE
        )

        # Remove metadata labels from the text used for retrieval.
        content = re.sub(
            r"^(Document ID|Topic|Source|Source URL):.*(?:\n|$)",
            "",
            chunk,
            flags=re.MULTILINE,
        ).strip()

        documents.append({
            "id": doc_id,
            "topic": topic_match.group(1).strip()
            if topic_match else "Agricultural guidance",
            "source": source_match.group(1).strip()
            if source_match else "Local starter guidance; requires verification.",
            "url": url_match.group(1).strip()
            if url_match else "",
            "text": content,
        })

    if not documents:
        raise ValueError(
            "No advisory documents found. Check agricultural_advisories.txt."
        )

    return documents


class AdvisoryRetriever:
    def __init__(self):
        self.documents = load_documents()

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
        )

        self.matrix = self.vectorizer.fit_transform(
            [doc["text"] for doc in self.documents]
        )

    def retrieve(self, query, top_k=3):
        """Return ranked guidance with structured citation metadata."""
        query = query.strip()

        if not query:
            return []

        if top_k < 1:
            return []

        query_vector = self.vectorizer.transform([query])

        scores = cosine_similarity(
            query_vector, self.matrix
        ).flatten()

        ranked_indices = scores.argsort()[::-1][:top_k]
        results = []

        for index in ranked_indices:
            score = float(scores[index])

            # Skip documents with no matching terms.
            if score <= 0:
                continue

            document = self.documents[index]

            results.append({
                "id": document["id"],
                "topic": document["topic"],
                "source": document["source"],
                "url": document["url"],
                "text": document["text"],
                "score": round(score, 4),

                # Keep the previous generator.py field compatible.
                "similarity": round(score, 4),
            })

        return results


if __name__ == "__main__":
    retriever = AdvisoryRetriever()

    test_query = (
        "My crop has high pest risk. "
        "How should I monitor pests and manage the risk?"
    )

    print("\nAGRIRISK AI — RETRIEVAL TEST")
    print("=" * 45)

    for result in retriever.retrieve(test_query):
        print(f"\nDocument ID: {result['id']}")
        print(f"Topic: {result['topic']}")
        print(f"Source: {result['source']}")
        print(f"Source URL: {result['url'] or 'Not provided'}")
        print(f"Similarity: {result['similarity']}")
        print(result["text"])

