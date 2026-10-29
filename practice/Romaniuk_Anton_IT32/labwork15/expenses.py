import math
from datetime import datetime
from pathlib import Path


def parse_line(line):
    parts = [p.strip() for p in line.strip().split(";")]
    if len(parts) != 4:
        raise ValueError(f"expected 4 fields, got {len(parts)}: {line!r}")
    date, category, amount_text, comment = parts
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"bad date: {date!r}") from None
    try:
        amount = float(amount_text)
    except ValueError:
        raise ValueError(f"bad amount: {amount_text!r}") from None
    if not math.isfinite(amount):
        raise ValueError(f"bad amount: {amount_text!r}")
    return {"date": date, "category": category, "amount": amount, "comment": comment}


def total_by_category(records):
    amounts = {}
    for rec in records:
        amounts.setdefault(rec["category"], []).append(rec["amount"])
    return {cat: round(math.fsum(values), 2) for cat, values in amounts.items()}


def load_expenses(path):
    records = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.lower().startswith("date;"):
            continue
        records.append(parse_line(stripped))
    return records