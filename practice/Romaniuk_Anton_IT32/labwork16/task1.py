import json
import math
import sys
from datetime import date
from pathlib import Path

NAME = "Anton Romaniuk"
GROUP = "IT-32"
BASE = Path(__file__).resolve().parent
CSV_PATH = BASE / "data" / "expenses.csv"
JSON_PATH = BASE / "data" / "expenses.json"


def read_csv(path):
    """CSV -> список словників. Коментарі, порожні рядки та заголовок пропускаються."""
    records = []
    with path.open(encoding="utf-8-sig") as f:
        for n, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith("#") or line.lower().startswith("date;"):
                continue
            parts = [p.strip() for p in line.split(";")]
            if len(parts) not in (3, 4):
                print(f"line {n}: skipped (expected 4 fields)", file=sys.stderr)
                continue
            try:
                date.fromisoformat(parts[0])
                amount = float(parts[2])
            except ValueError:
                print(f"line {n}: skipped (bad date or amount)", file=sys.stderr)
                continue
            if not math.isfinite(amount):
                print(f"line {n}: skipped (bad amount)", file=sys.stderr)
                continue
            records.append({
                "date": parts[0],
                "category": parts[1],
                "amount": amount,                       # число, а не рядок
                "comment": parts[3] if len(parts) == 4 else "",
            })
    return records


def main():
    print(f"{NAME}, {GROUP}")
    if not CSV_PATH.is_file():
        print(f"error: {CSV_PATH} not found", file=sys.stderr)
        sys.exit(1)
    try:
        records = read_csv(CSV_PATH)
        with JSON_PATH.open("w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    size = JSON_PATH.stat().st_size
    print(f"records: {len(records)}")
    print(f"saved: {JSON_PATH.relative_to(BASE).as_posix()} ({size} bytes)")


if __name__ == "__main__":
    main()
