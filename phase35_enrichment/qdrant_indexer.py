from pathlib import Path
import json
import logging
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
)


PROJECT_ROOT = Path(__file__).resolve().parent

OUTPUT_DIR = PROJECT_ROOT / "output"

INPUT_FILE = OUTPUT_DIR / "embeddings.jsonl"

COLLECTION_NAME = "semantic_transport_graph"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class QdrantIndexer:
    def __init__(
        self,
        input_file: Path,
        collection_name: str,
        batch_size: int = 128,
        recreate_collection: bool = True
    ):
        self.input_file = input_file

        self.collection_name = collection_name

        self.batch_size = batch_size

        self.recreate_collection = recreate_collection

        self.embedding_records = []

        self.client = QdrantClient(
            host="localhost",
            port=6333
        )

    def load_embeddings(self):
        logging.info(
            "Loading embedding records..."
        )

        try:
            with open(
                self.input_file,
                "r",
                encoding="utf-8"
            ) as f:

                for line in f:
                    self.embedding_records.append(
                        json.loads(line)
                    )

            logging.info(
                f"Loaded "
                f"{len(self.embedding_records)} "
                f"embedding records."
            )

        except Exception as e:
            logging.error(
                f"Failed loading embeddings: {e}"
            )

            self.embedding_records = []

    def infer_vector_dimension(self):
        if not self.embedding_records:
            raise ValueError(
                "No embedding records loaded."
            )

        first_embedding = (
            self.embedding_records[0]
            .get("embedding")
        )

        if not first_embedding:
            raise ValueError(
                "Embedding vector missing."
            )

        dimension = len(first_embedding)

        logging.info(
            f"Inferred embedding dimension: "
            f"{dimension}"
        )

        return dimension

    def recreate_qdrant_collection(
        self,
        vector_dimension: int
    ):
        logging.info(
            f"Recreating collection: "
            f"{self.collection_name}"
        )

        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=vector_dimension,
                distance=Distance.COSINE
            )
        )

        logging.info(
            "Collection created successfully."
        )

    def batch_generator(self, items, batch_size):
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]

    def create_points(self, batch):
        points = []

        for item in batch:

            embedding = item.get("embedding")

            if not embedding:
                continue

            semantic_text = item.get(
                "semantic_text",
                ""
            )

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "node_id": item.get("id"),
                    "node_class": item.get(
                        "node_class"
                    ),
                    "semantic_text": semantic_text
                }
            )

            points.append(point)

        return points

    def upload_batches(self):
        logging.info(
            "Uploading embeddings to Qdrant..."
        )

        total_batches = (
            len(self.embedding_records)
            + self.batch_size - 1
        ) // self.batch_size

        for batch_index, batch in enumerate(
            self.batch_generator(
                self.embedding_records,
                self.batch_size
            )
        ):
            logging.info(
                f"Uploading batch "
                f"{batch_index + 1}/"
                f"{total_batches}"
            )

            points = self.create_points(batch)

            if not points:
                continue

            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

        logging.info(
            "All embeddings uploaded successfully."
        )

    def run(self):
        logging.info("=" * 80)

        logging.info(
            "QDRANT VECTOR INDEXING PIPELINE"
        )

        logging.info("=" * 80)

        self.load_embeddings()

        if not self.embedding_records:
            logging.warning(
                "No embeddings available."
            )

            return

        vector_dimension = (
            self.infer_vector_dimension()
        )

        if self.recreate_collection:
            self.recreate_qdrant_collection(
                vector_dimension
            )

        self.upload_batches()

        logging.info(
            "Qdrant indexing completed successfully."
        )


def main():
    indexer = QdrantIndexer(
        INPUT_FILE,
        COLLECTION_NAME
    )

    indexer.run()


if __name__ == "__main__":
    main()