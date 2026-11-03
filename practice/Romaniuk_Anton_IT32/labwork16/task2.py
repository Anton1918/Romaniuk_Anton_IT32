import json
import sys
from datetime import date
from pathlib import Path

NAME = "Anton Romaniuk"
GROUP = "IT-32"
BASE = Path(__file__).resolve().parent
SRC = BASE / "data" / "expenses.json"
DST = BASE / "data" / "expenses_updated.json"
MIN_AMOUNT = 10


def new_record():
    """Мій новий запис із сьогоднішньою датою."""
    return {
        "date": date.today().isoformat(),
        "category": "books",
        "amount": 250.0,
        "comment": "added by task2.py",
    }


def is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def main():
    print(f"{NAME}, {GROUP}")
    if not SRC.is_file():
        print(f"error: {SRC} not found (run task1.py first)", file=sys.stderr)
        sys.exit(1)

    # 1. читаємо
    try:
        with SRC.open(encoding="utf-8") as f:
            records = json.load(f)
    except json.JSONDecodeError as e:
        print(f"error: {SRC.name} is corrupted: line {e.lineno}, column {e.colno}: {e.msg}",
              file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(records, list) or not all(
            isinstance(r, dict) and is_number(r.get("amount")) for r in records):
        print(f"error: {SRC.name} must contain a list of records with numeric amount",
              file=sys.stderr)
        sys.exit(1)

    before = len(records)

    # 2. додаємо запис
    records.append(new_record())
    added = 1

    # 3. видаляємо записи з сумою менше 10
    kept = [r for r in records if r["amount"] >= MIN_AMOUNT]
    removed = len(records) - len(kept)

    # 4. записуємо в НОВИЙ файл (вихідний не змінюється)
    try:
        with DST.open("w", encoding="utf-8") as f:
            json.dump(kept, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"records before: {before}")
    print(f"added: {added}, removed: {removed}")
    print(f"records after: {len(kept)}")
    print(f"saved: {DST.relative_to(BASE).as_posix()}")


if __name__ == "__main__":
    main()
