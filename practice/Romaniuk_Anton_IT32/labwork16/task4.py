import json
import re
import sys
from datetime import date
from pathlib import Path

NAME = "Anton Romaniuk"
GROUP = "IT-32"
BASE = Path(__file__).resolve().parent
CSV_PATH = BASE / "data" / "expenses.csv"
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load_data():
    """Словник із об'єктами date: мої реальні витрати."""
    records = []
    with CSV_PATH.open(encoding="utf-8-sig") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or line.lower().startswith("date;"):
                continue
            parts = [p.strip() for p in line.split(";")]
            records.append({
                "date": date.fromisoformat(parts[0]),
                "category": parts[1],
                "amount": float(parts[2]),
                "comment": parts[3] if len(parts) > 3 else "",
            })
    return {"owner": NAME, "created": date.today(), "records": records}


# --- спосіб 1: параметр default= ---
def date_default(obj):
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


# --- спосіб 2: власні функції туди й назад ---
def dates_to_str(obj):
    """Рекурсивно замінює всі date на рядки ISO."""
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: dates_to_str(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [dates_to_str(v) for v in obj]
    return obj


def str_to_dates(obj):
    """Рекурсивно замінює рядки формату YYYY-MM-DD назад на date."""
    if isinstance(obj, str) and ISO_DATE.match(obj):
        try:
            return date.fromisoformat(obj)
        except ValueError:
            return obj
    if isinstance(obj, dict):
        return {k: str_to_dates(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [str_to_dates(v) for v in obj]
    return obj


def main():
    print(f"{NAME}, {GROUP}")
    if not CSV_PATH.is_file():
        print(f"error: {CSV_PATH} not found", file=sys.stderr)
        sys.exit(1)
    try:
        data = load_data()
    except (ValueError, IndexError) as e:
        print(f"error: bad data in {CSV_PATH.name}: {e}", file=sys.stderr)
        sys.exit(1)

    # 0. проблема
    try:
        json.dumps(data)
    except TypeError as e:
        print(f"TypeError: {e}")

    # 1. default=
    text1 = json.dumps(data, default=date_default, ensure_ascii=False)
    back1 = json.loads(text1)
    print()
    print("method 1: default=")
    print(f"  json length:       {len(text1)} chars")
    print(f"  type after read:   {type(back1['created']).__name__}")
    print(f"  back == original:  {back1 == data}")

    # 2. власні функції
    text2 = json.dumps(dates_to_str(data), ensure_ascii=False)
    back2 = str_to_dates(json.loads(text2))
    print()
    print("method 2: own functions")
    print(f"  json length:       {len(text2)} chars")
    print(f"  type after read:   {type(back2['created']).__name__}")
    print(f"  type in record:    {type(back2['records'][0]['date']).__name__}")
    print(f"  back == original:  {back2 == data}")


if __name__ == "__main__":
    main()
