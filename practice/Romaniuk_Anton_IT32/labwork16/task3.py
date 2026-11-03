import json
import math
import sys
from pathlib import Path

NAME = "Anton Romaniuk"
GROUP = "IT-32"
BASE = Path(__file__).resolve().parent
SETTINGS = BASE / "settings.json"
EXPENSES = BASE / "data" / "expenses.json"

DEFAULTS = {
    "owner": "Anton Romaniuk",
    "group": "IT-32",
    "currency": "UAH",
    "monthly_limit": 10000,
    "categories": ["groceries", "transport", "cafe", "books", "clothing", "electronics"],
}


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    print(f"{NAME}, {GROUP}")

    # 1. файлу немає: створюємо зі значеннями за замовчуванням
    if not SETTINGS.exists():
        try:
            with SETTINGS.open("w", encoding="utf-8") as f:
                json.dump(DEFAULTS, f, indent=2, ensure_ascii=False)
        except OSError as e:
            fail(str(e))
        print("settings.json not found, default created")
        return

    # 3. файл пошкоджено: повідомляємо, НЕ перезаписуємо
    try:
        with SETTINGS.open(encoding="utf-8") as f:
            settings = json.load(f)
    except json.JSONDecodeError as e:
        fail(f"settings.json is corrupted: line {e.lineno}, column {e.colno}: {e.msg}")
    except OSError as e:
        fail(str(e))

    missing = [k for k in DEFAULTS if not isinstance(settings, dict) or k not in settings]
    if missing:
        fail(f"settings.json has no keys: {', '.join(missing)}")
    limit = settings["monthly_limit"]
    if isinstance(limit, bool) or not isinstance(limit, (int, float)) or limit < 0:
        fail("monthly_limit must be a non-negative number")

    # 2. файл є: виводимо налаштування і порівнюємо витрати з лімітом
    if not EXPENSES.is_file():
        fail(f"{EXPENSES} not found (run task1.py first)")
    try:
        with EXPENSES.open(encoding="utf-8") as f:
            records = json.load(f)
        spent = math.fsum(r["amount"] for r in records)
    except (json.JSONDecodeError, OSError, KeyError, TypeError) as e:
        fail(f"cannot read expenses.json: {e}")

    cur = settings["currency"]
    left = limit - spent
    print(f"owner: {settings['owner']}, group: {settings['group']}")
    print(f"categories: {', '.join(settings['categories'])}")
    note = " (limit exceeded)" if left < 0 else ""
    print(f"limit: {limit:.2f} {cur}, spent: {spent:.2f} {cur}, left: {left:.2f} {cur}{note}")


if __name__ == "__main__":
    main()
