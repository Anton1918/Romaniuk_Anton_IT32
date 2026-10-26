import math
import random
import sys
from datetime import datetime
from pathlib import Path

NAME = "Anton Romaniuk"
GROUP = "IT-32"
YEAR = 2008
HISTORY = Path(__file__).resolve().parent / "results" / "history.csv"
HEADER = "# datetime;score;seconds"


def make_examples():
    random.seed(YEAR)
    r = random.randint(5, 25)
    n = random.randint(3, 8)
    a, b = random.randint(10, 60), random.randint(10, 60)
    cn = random.randint(5, 10)
    ck = random.randint(2, 4)
    pct = random.choice([5, 10, 15, 20, 25])
    base = random.randint(5, 50) * 20
    return [
        (f"sqrt({r * r})", math.isqrt(r * r)),
        (f"{n}!", math.factorial(n)),
        (f"gcd({a}, {b})", math.gcd(a, b)),
        (f"comb({cn}, {ck})", math.comb(cn, ck)),
        (f"{pct}% of {base}", base * pct // 100),
    ]


def read_history():
    rows = []
    if not HISTORY.is_file():
        return rows
    with HISTORY.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                dt, score, secs = line.split(";")
                rows.append((dt, int(score), float(secs)))
            except ValueError:
                print(f"bad history line skipped: {line}", file=sys.stderr)
    return rows


def main():
    print(f"{NAME}, {GROUP}")
    examples = make_examples()
    start = datetime.now()
    score = 0
    for i, (text, answer) in enumerate(examples, 1):
        try:
            given = int(input(f"{i}) {text} = ").strip())
        except (ValueError, EOFError):
            given = None
        if given == answer:
            score += 1
            print("   correct")
        else:
            print(f"   wrong, answer: {answer}")
    seconds = (datetime.now() - start).total_seconds()
    print(f"score: {score}/{len(examples)}, time: {seconds:.1f} s")

    try:
        HISTORY.parent.mkdir(exist_ok=True)
        new = not HISTORY.exists()
        with HISTORY.open("a", encoding="utf-8") as f:
            if new:
                f.write(HEADER + "\n")
            f.write(f"{start:%Y-%m-%d %H:%M};{score};{seconds:.1f}\n")
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    rows = read_history()
    best = max(rows, key=lambda r: (r[1], -r[2]))
    print(f"attempts: {len(rows)}, best: {best[1]}/{len(examples)} in {best[2]:.1f} s ({best[0]})")


if __name__ == "__main__":
    main()
