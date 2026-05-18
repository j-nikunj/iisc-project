from pathlib import Path
import subprocess
import sys


def main() -> None:
    base = Path(__file__).resolve().parent
    root = base.parent / "seed_graph" / "bengaluru"
    output_dir = base / "output"
    reports_dir = base / "reports"

    command = [
        sys.executable,
        str(base / "parser.py"),
        "--root",
        str(root),
        "--output",
        str(output_dir),
        "--reports",
        str(reports_dir),
    ]
    raise SystemExit(subprocess.call(command))


if __name__ == "__main__":
    main()
