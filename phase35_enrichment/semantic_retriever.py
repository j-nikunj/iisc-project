from pathlib import Path
import logging

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class SemanticRetriever:
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    COLLECTION_NAME = "semantic_transport_graph"

    def __init__(
        self,
        top_k: int = 10
    ):
        self.top_k = top_k

        logging.info(
            f"Loading embedding model: "
            f"{self.MODEL_NAME}"
        )

        self.model = SentenceTransformer(
            self.MODEL_NAME
        )

        self.client = QdrantClient(
            host="localhost",
            port=6333
        )

    def generate_query_embedding(
        self,
        query: str
    ):
        logging.info(
            "Generating query embedding..."
        )

        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding.tolist()

    def semantic_search(
        self,
        query: str
    ):
        logging.info("=" * 80)

        logging.info(
            "SEMANTIC RETRIEVAL"
        )

        logging.info("=" * 80)

        logging.info(
            f"Query: {query}"
        )

        query_embedding = (
            self.generate_query_embedding(
                query
            )
        )

        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_embedding,
            limit=self.top_k
        ).points

        return results

    def print_results(
        self,
        results
    ):
        print("\n" + "=" * 80)
        print("TOP SEMANTIC RETRIEVAL RESULTS")
        print("=" * 80)

        for rank, result in enumerate(
            results,
            start=1
        ):
            payload = result.payload

            node_id = payload.get(
                "node_id",
                "unknown"
            )

            node_class = payload.get(
                "node_class",
                "unknown"
            )

            semantic_text = payload.get(
                "semantic_text",
                ""
            )

            score = result.score

            print("\n" + "-" * 80)

            print(f"Rank: {rank}")

            print(f"Score: {score:.4f}")

            print(f"Node ID: {node_id}")

            print(f"Node Class: {node_class}")

            print("\nSemantic Context:\n")

            preview = semantic_text[:1200]

            print(preview)

    def run(
        self,
        query: str
    ):
        results = self.semantic_search(
            query
        )

        self.print_results(results)


def main():
    query = (
        "flood-prone multimodal "
        "congestion corridors"
    )

    retriever = SemanticRetriever(
        top_k=10
    )

    retriever.run(query)


if __name__ == "__main__":
    main()