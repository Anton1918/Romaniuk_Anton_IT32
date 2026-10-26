import math
import sys
from datetime import datetime
from pathlib import Path

NAME = "Anton Romaniuk"
GROUP = "IT-32"
USAGE = "usage: python3 task3.py [--dry-run] <dir>"
UNITS = ["B", "KB", "MB", "GB"]


def human_size(size):
    if size <= 0:
        return "0.0 B"
    idx = min(int(math.log(size, 1024)), len(UNITS) - 1)
    return f"{size / 1024 ** idx:.1f} {UNITS[idx]}"


def fail(msg, code=1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def main():
    print(f"{NAME}, {GROUP}")
    args = sys.argv[1:]
    dry = "--dry-run" in args
    rest = [a for a in args if a != "--dry-run"]
    if len(rest) != 1 or len(args) > 2:
        print(USAGE, file=sys.stderr)
        sys.exit(2)

    root = Path(rest[0])
    if not root.is_dir():
        fail(f"{root} is not a directory")

    items = []
    for p in root.iterdir():
        if p.is_file():
            st = p.stat()
            items.append((datetime.fromtimestamp(st.st_mtime), st.st_size, p))
    if not items:
        print("no files to organize")
        return
    items.sort(key=lambda t: t[0])  # від найстарішого

    plan = []
    for mtime, size, p in items:
        folder = mtime.strftime("%Y-%m")
        plan.append((p, size, mtime, folder, root / folder / p.name))

    lines = []
    for p, size, mtime, folder, _ in plan:
        lines.append(f"{p.name:<20}{human_size(size):>10}  {mtime:%d.%m.%Y %H:%M}  -> {folder}/")
    folders = {x[3] for x in plan}
    summary = f"{len(plan)} files, {len(folders)} folders"
    for l in lines:
        print(l)

    if dry:
        print(f"{summary} (dry run, nothing moved)")
        return

    # перевірка ВСІХ конфліктів до переміщення
    conflicts = [x[4] for x in plan if x[4].exists()]
    if conflicts:
        fail(f"{conflicts[0]} already exists, nothing was moved")

    try:
        for p, _, _, folder, dest in plan:
            dest.parent.mkdir(exist_ok=True)
            p.rename(dest)

        reports = Path(__file__).resolve().parent / "reports"
        reports.mkdir(exist_ok=True)
        rep = reports / f"organize_{datetime.now():%Y%m%d_%H%M}.txt"
        rep.write_text("\n".join(lines + [summary]) + "\n", encoding="utf-8")
    except OSError as e:
        fail(str(e))

    print(summary)
    print(f"report saved to: reports/{rep.name}")


if __name__ == "__main__":
    main()
