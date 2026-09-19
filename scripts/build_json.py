"""Build JSON copies of every CSV in data/ and sanity-check the numbers.

Usage:  python scripts/build_json.py
Run it after every edit to a CSV so the JSON files stay in sync.
"""
import csv
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
NUMERIC_SUFFIXES = ("_usd", "_usd_per_month")


def convert(value: str, key: str):
    if value == "":
        return None
    if key.endswith(NUMERIC_SUFFIXES):
        try:
            number = float(value)
            return int(number) if number.is_integer() else number
        except ValueError:
            return value  # e.g. "undisclosed"
    return value


def check_ranges(rows, name):
    errors = []
    for i, row in enumerate(rows, start=2):
        for lo, hi in (("cost_min_usd", "cost_max_usd"), ("budget_min_usd", "budget_max_usd")):
            a, b = row.get(lo), row.get(hi)
            if isinstance(a, (int, float)) and isinstance(b, (int, float)) and a > b:
                errors.append(f"{name} line {i}: {lo} ({a}) > {hi} ({b})")
    return errors


def main():
    errors = []
    for csv_path in sorted(DATA.glob("*.csv")):
        with csv_path.open(newline="", encoding="utf-8") as f:
            rows = [{k: convert(v, k) for k, v in r.items()} for r in csv.DictReader(f)]
        errors += check_ranges(rows, csv_path.name)
        out = csv_path.with_suffix(".json")
        out.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{csv_path.name}: {len(rows)} rows -> {out.name}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
