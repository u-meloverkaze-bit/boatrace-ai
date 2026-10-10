from datetime import datetime, timezone, timedelta
from pathlib import Path
import csv

jst = timezone(timedelta(hours=9))
now = datetime.now(jst)

folder = Path("results")
folder.mkdir(exist_ok=True)

with (folder / "status.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["実行日時", "状態"])
    writer.writerow([now.isoformat(), "動作確認成功"])

print("競艇AIの自動実行テスト成功")
print("実行日時:", now.isoformat())
print("※競艇データの取得・AI検証は未実装")
