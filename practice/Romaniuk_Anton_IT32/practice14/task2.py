import sys
from pathlib import Path

from tabulate import tabulate

NAME = "Anton Romaniuk"
GROUP = "IT-32"
DATA = Path(__file__).resolve().parent / "data" / "expenses.csv"


def main():
    print(f"{NAME}, {GROUP}")
    if not DATA.is_file():
        print(f"error: {DATA} not found", file=sys.stderr)
        sys.exit(1)

    stats = {}  # category -> [count, total]
    with DATA.open(encoding="utf-8") as f:
        for n, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(";")
            try:
                category = parts[1].strip()
                amount = float(parts[2].strip().replace(",", "."))
            except (IndexError, ValueError):
                print(f"line {n}: skipped (bad row)", file=sys.stderr)
                continue
            item = stats.setdefault(category, [0, 0.0])
            item[0] += 1
            item[1] += amount

    if not stats:
        print("error: no valid expenses in file", file=sys.stderr)
        sys.exit(1)

    rows = [[cat, c, t] for cat, (c, t) in stats.items()]
    rows.append(["TOTAL", sum(r[1] for r in rows), sum(r[2] for r in rows)])
    print(tabulate(rows, headers=["category", "count", "total"],
                   tablefmt="github", floatfmt=".2f"))


if __name__ == "__main__":
    main()