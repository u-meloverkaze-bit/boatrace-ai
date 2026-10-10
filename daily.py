from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen
import csv

JST = timezone(timedelta(hours=9))
day = (datetime.now(JST) - timedelta(days=1)).date()
folder = Path("data") / day.strftime("%Y%m")
folder.mkdir(parents=True, exist_ok=True)

results = []
for kind in ("B", "K"):
    filename = f"{kind.lower()}{day:%y%m%d}.lzh"
    url = f"https://www1.mbrace.or.jp/od2/{kind}/{day:%Y%m}/{filename}"
    dest = folder / filename
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=45) as response:
            data = response.read()
        if len(data) < 100:
            raise ValueError("Downloaded file is unexpectedly small")
        dest.write_bytes(data)
        status = f"OK ({len(data)} bytes)"
    except Exception as exc:
        status = f"ERROR: {type(exc).__name__}: {exc}"
        print(kind, status)
    results.append([str(day), kind, status])

Path("results").mkdir(exist_ok=True)
with Path("results/status.csv").open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["date", "type", "status"])
    writer.writerows(results)

for row in results:
    print(*row)

if any(not row[2].startswith("OK") for row in results):
    raise RuntimeError("One or more downloads failed")
