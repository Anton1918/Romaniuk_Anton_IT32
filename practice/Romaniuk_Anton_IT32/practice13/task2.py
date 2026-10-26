import math
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

NAME = "Anton Romaniuk"
GROUP = "IT-32"
DATA = Path(__file__).resolve().parent / "data" / "expenses.csv"


def days_in_month(d):
    """Кількість днів у місяці дати d — через різницю дат."""
    first = d.replace(day=1)
    nxt = (first + timedelta(days=32)).replace(day=1)
    return (nxt - first).days


def load(path):
    """Повертає словник {date: сума}. Погані рядки йдуть у stderr."""
    totals = {}
    with path.open(encoding="utf-8") as f:
        for n, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(";")
            if len(parts) < 3:
                print(f"line {n}: skipped (expected date;category;amount)", file=sys.stderr)
                continue
            try:
                d = datetime.strptime(parts[0].strip(), "%Y-%m-%d").date()
                amount = float(parts[2].strip().replace(",", "."))
            except ValueError:
                print(f"line {n}: skipped (bad date or amount)", file=sys.stderr)
                continue
            if not math.isfinite(amount) or amount < 0:
                print(f"line {n}: skipped (bad amount)", file=sys.stderr)
                continue
            totals[d] = totals.get(d, 0.0) + amount
    return totals


def main():
    print(f"{NAME}, {GROUP}")
    if not DATA.is_file():
        print(f"error: {DATA} not found", file=sys.stderr)
        sys.exit(1)
    try:
        totals = load(DATA)
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
    if not totals:
        print("error: no valid expenses in file", file=sys.stderr)
        sys.exit(1)

    first, last = min(totals), max(totals)
    span = (last - first).days + 1
    print(f"period: {first:%d.%m.%Y} ({first:%A}) - {last:%d.%m.%Y} ({last:%A}), {span} days")
    print()

    # 2. суми за днями тижня (Monday..Sunday)
    by_wd = [0.0] * 7
    for d, s in totals.items():
        by_wd[d.weekday()] += s
    monday = date(2026, 9, 21)  # будь-який понеділок — лише для назв
    print("weekday      total")
    for i in range(7):
        name = (monday + timedelta(days=i)).strftime("%A")
        print(f"{name:<12}{by_wd[i]:>8.2f}")
    print()

    # 3. загальна статистика (дні без витрат = 0)
    daily = [totals.get(first + timedelta(days=i), 0.0) for i in range(span)]
    total = math.fsum(daily)
    mean = total / span
    std = math.sqrt(math.fsum((x - mean) ** 2 for x in daily) / span)
    print(f"total:        {total:.2f}")
    print(f"per day:      {mean:.2f} +- {std:.2f}")

    # 4. найбільший день і дні без витрат
    top = max(totals, key=totals.get)
    print(f"top day:      {top:%d.%m.%Y} ({top:%A}), {totals[top]:.2f}")
    print(f"no-spend days: {daily.count(0.0)}")

    # 5. місяць
    dim = days_in_month(last)
    left = dim - last.day
    print(f"days in {last:%B}: {dim}, left after {last:%d.%m}: {left}")
    print(f"month forecast: {mean * dim:.2f}")


if __name__ == "__main__":
    main()
