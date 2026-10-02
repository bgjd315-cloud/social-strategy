"""把選用題目的題目文字與題組文字寫到 notes/picks_text.txt，方便撰寫解析。"""
import csv, sys, json
from pathlib import Path
R = Path(__file__).resolve().parents[1]
SRC = R.parent / "social-literacy"
sys.path.insert(0, str(SRC / "tools")); sys.path.insert(0, str(R / "tools"))
from reading_data import _rows, _clean
from picks import PICKS
rows = {r["代號"]: r for r in csv.DictReader(open(R / "data/items.csv", encoding="utf-8-sig"))}
full = {}
for t, y, q, g, lab, a, args, shown, sub, kind, page in _rows(SRC):
    full[f"{t}-{args.replace(',', '-')}"] = (_clean(q.get("t")), _clean(g["t"]) if g else "")
out = open(R / "notes/picks_text.txt", "w", encoding="utf-8")
for s, ids in PICKS.items():
    for i in ids:
        r = rows[i]; qt, gt = full[i]
        out.write(f"\n### {s} {i} 答案 {r['答案']} | {r['考點']} | {r['資料']} {r['陷阱']} {r['判讀提示']}\nQ: {qt[:900]}\n" + (f"G: {gt[:900]}\n" if gt else ""))
