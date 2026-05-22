from pathlib import Path
import pandas as pd
import yaml

from gtfs_normalizer import GTFSNormalizer
from graph_builder import GraphBuilder
from graph_exporter import GraphExporter

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"
ONTOLOGY_CONFIG_PATH = PROJECT_ROOT / "gtfs_ontology_config.yaml"


REQUIRED_FILES = [
    "stops.txt",
    "routes.txt",
    "trips.txt",
    "stop_times.txt"
]

OPTIONAL_FILES = [
    "pathways.txt",
    "transfers.txt",
    "facilities.txt",
    "areas.txt",
    "route_patterns.txt",
    "calendar.txt",
    "shapes.txt"
]



class GTFSLoader:
    def __init__(self, data_dir: Path, ontology_config_path: Path):
        self.data_dir = data_dir
        self.ontology_config_path = ontology_config_path

        self.loaded_data = {}
        self.ontology_config = {}

    def validate_required_files(self) -> bool:
        print("\nValidating required GTFS files...\n")

        missing_files = []

        for file_name in REQUIRED_FILES:
            file_path = self.data_dir / file_name

            if file_path.exists():
                print(f"[FOUND] {file_name}")
            else:
                print(f"[MISSING] {file_name}")
                missing_files.append(file_name)

        if missing_files:
            print("\nValidation failed.")
            return False

        print("\nAll required GTFS files found.")
        return True

    def load_csv(self, file_name: str) -> pd.DataFrame:
        file_path = self.data_dir / file_name

        print(f"\nLoading {file_name}...")

        try:
            df = pd.read_csv(
                file_path,
                encoding="utf-8",
                low_memory=False
            )

            print(f"[LOADED] {file_name} | Rows: {len(df)}")

            return df

        except Exception as e:
            print(f"[ERROR] Failed loading {file_name}: {e}")
            return pd.DataFrame()

    def load_all_files(self):
        print("\nLoading GTFS datasets...\n")

        all_files = REQUIRED_FILES + OPTIONAL_FILES

        for file_name in all_files:
            file_path = self.data_dir / file_name

            if file_path.exists():
                df = self.load_csv(file_name)

                if not df.empty:
                    self.loaded_data[file_name] = df

    def load_ontology_config(self) -> dict:
        print("\nLoading ontology configuration...\n")

        try:
            with open(ONTOLOGY_CONFIG_PATH, "r", encoding="utf-8") as f:
                self.ontology_config = yaml.safe_load(f)

            print("[LOADED] gtfs_ontology_config.yaml")

            return self.ontology_config

        except Exception as e:
            print(f"[ERROR] Failed loading ontology config: {e}")
            return {}

    def summarize_dataframe(self, file_name: str, df: pd.DataFrame):
        print("\n" + "=" * 80)
        print(f"DATASET: {file_name}")
        print("=" * 80)

        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")

        print("\nColumn Names:")
        for column in df.columns:
            print(f" - {column}")

        print("\nSample Rows:")
        print(df.head(3).to_string())

    def summarize_loaded_data(self):
        print("\nGenerating GTFS dataset summaries...\n")

        for file_name, df in self.loaded_data.items():
            self.summarize_dataframe(file_name, df)

    def run(self):
        print("\n" + "=" * 80)
        print("GTFS INGESTION PIPELINE")
        print("=" * 80)

        if not self.validate_required_files():
            return

        self.load_ontology_config()

        self.load_all_files()

        self.summarize_loaded_data()

        print("\nGTFS ingestion completed successfully.\n")


def main():
    loader = GTFSLoader(DATA_DIR, ONTOLOGY_CONFIG_PATH)

    loader.run()

    normalizer = GTFSNormalizer(
        loader.loaded_data,
        loader.ontology_config
    )

    normalizer.run()

    graph_builder = GraphBuilder(
    normalizer.normalized_entities
    )

    graph_builder.run()

    graph_exporter = GraphExporter(
    graph_builder.graph
    )

    graph_exporter.run()

if __name__ == "__main__":
    main()