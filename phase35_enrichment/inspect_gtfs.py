from pathlib import Path
import pandas as pd

GTFS_PATH = Path("phase35_enrichment/data")

REQUIRED_FILES = [
    "agency.txt",
    "routes.txt",
    "trips.txt",
    "stop_times.txt",
    "stops.txt"
]

OPTIONAL_FILES = [
    "calendar.txt",
    "shapes.txt",
    "transfers.txt",
    "facilities.txt",
    "pathways.txt",
    "route_patterns.txt"
]


def inspect_file(file_name):
    file_path = GTFS_PATH / file_name

    if not file_path.exists():
        print(f"[MISSING] {file_name}")
        return

    try:
        df = pd.read_csv(file_path)

        print("\n" + "=" * 80)
        print(f"FILE: {file_name}")
        print("=" * 80)

        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")

        print("\nColumns:")
        for col in df.columns:
            print(f" - {col}")

        print("\nSample Rows:")
        print(df.head(3).to_string())

    except Exception as e:
        print(f"[ERROR] {file_name}: {e}")


def main():
    print("\nREQUIRED FILES")
    for file_name in REQUIRED_FILES:
        inspect_file(file_name)

    print("\nOPTIONAL FILES")
    for file_name in OPTIONAL_FILES:
        inspect_file(file_name)


if __name__ == "__main__":
    main()