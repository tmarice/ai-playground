#!/usr/bin/env python3
import argparse
import csv
import sys
from pathlib import Path


def validate_csv_file(filepath: Path) -> None:
    """Validate that a file is a valid CSV with a header row."""
    if not filepath.exists():
        raise ValueError(f"File does not exist: {filepath}")

    if not filepath.is_file():
        raise ValueError(f"Not a file: {filepath}")

    if filepath.suffix.lower() != ".csv":
        raise ValueError(f"Not a CSV file: {filepath}")

    try:
        with filepath.open("r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)

            if header is None:
                raise ValueError(f"CSV file is empty (no header row): {filepath}")

            if not header or all(col.strip() == "" for col in header):
                raise ValueError(f"CSV file has empty header row: {filepath}")

    except csv.Error as e:
        raise ValueError(f"Invalid CSV format in {filepath}: {e}")
    except UnicodeDecodeError as e:
        raise ValueError(f"Unable to read {filepath} as UTF-8: {e}")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Process CSV files with header rows.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "csv_files",
        nargs="+",
        type=Path,
        metavar="CSV_FILE",
        help="CSV files to process (must have header rows)",
    )
    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    errors = []
    for filepath in args.csv_files:
        try:
            validate_csv_file(filepath)
        except ValueError as e:
            errors.append(str(e))

    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Successfully validated {len(args.csv_files)} CSV file(s)")
    for filepath in args.csv_files:
        print(f"  - {filepath}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
