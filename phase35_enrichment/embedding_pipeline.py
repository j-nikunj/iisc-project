from pathlib import Path
import json
import logging

from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parent

OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

INPUT_FILE = OUTPUT_DIR / "semantic_documents.json"

OUTPUT_FILE = OUTPUT_DIR / "embeddings.jsonl"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class EmbeddingPipeline:
    MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(
        self,
        input_file: Path,
        output_file: Path,
        batch_size: int = 64
    ):
        self.input_file = input_file

        self.output_file = output_file

        self.batch_size = batch_size

        self.documents = []

        logging.info(
            f"Loading embedding model: {self.MODEL_NAME}"
        )

        self.model = SentenceTransformer(
            self.MODEL_NAME
        )

    def load_documents(self):
        logging.info(
            "Loading semantic documents..."
        )

        try:
            with open(
                self.input_file,
                "r",
                encoding="utf-8"
            ) as f:
                self.documents = json.load(f)

            logging.info(
                f"Loaded {len(self.documents)} semantic documents."
            )

        except Exception as e:
            logging.error(
                f"Failed loading semantic documents: {e}"
            )

            self.documents = []

    def batch_generator(self, items, batch_size):
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]

    def log_batch_info(
        self,
        batch_index,
        total_batches
    ):
        logging.info(
            f"Processing batch "
            f"{batch_index + 1}/{total_batches}"
        )

    def generate_embeddings(self):
        logging.info(
            "Generating embeddings..."
        )

        if not self.documents:
            logging.warning(
                "No semantic documents found."
            )

            return

        total_batches = (
            len(self.documents) + self.batch_size - 1
        ) // self.batch_size

        with open(
            self.output_file,
            "w",
            encoding="utf-8"
        ) as out_file:

            for batch_index, batch in enumerate(
                self.batch_generator(
                    self.documents,
                    self.batch_size
                )
            ):
                self.log_batch_info(
                    batch_index,
                    total_batches
                )

                valid_items = []

                texts = []

                for item in batch:

                    if "semantic_text" not in item:
                        continue

                    semantic_text = item.get(
                        "semantic_text",
                        ""
                    )

                    if not semantic_text:
                        continue

                    valid_items.append(item)

                    texts.append(semantic_text)

                if not texts:
                    continue

                embeddings = self.model.encode(
                    texts,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )

                for item, embedding in zip(
                    valid_items,
                    embeddings
                ):
                    output_entry = {
                        "id": item.get("id"),
                        "node_class": item.get(
                            "node_class"
                        ),
                        "semantic_text": item.get(
                            "semantic_text"
                        ),
                        "embedding": [
                            float(x)
                            for x in embedding
                        ]
                    }

                    out_file.write(
                        json.dumps(
                            output_entry,
                            ensure_ascii=False
                        )
                        + "\n"
                    )

        logging.info(
            f"Embeddings exported to:"
        )

        logging.info(self.output_file)

    def run(self):
        logging.info("=" * 80)

        logging.info(
            "SEMANTIC EMBEDDING PIPELINE"
        )

        logging.info("=" * 80)

        self.load_documents()

        self.generate_embeddings()

        logging.info(
            "Embedding pipeline completed successfully."
        )


def main():
    pipeline = EmbeddingPipeline(
        INPUT_FILE,
        OUTPUT_FILE
    )

    pipeline.run()


if __name__ == "__main__":
    main()