"""列出每種策略可選的題目（有標準答案的選擇題、有試卷圖片），寫到 notes/candidates.txt。"""
import csv, sys, random
from pathlib import Path
R = Path(__file__).resolve().parents[1]
SRC = R.parent / "social-literacy"
sys.path.insert(0, str(SRC / "tools"))
from reading_data import build_practice
P = {it[13]: it for it in build_practice(SRC)["items"]}
rows = [r for r in csv.DictReader(open(R / "data/items.csv", encoding="utf-8-sig")) if r["代號"] in P]
out = open(R / "notes/candidates.txt", "w", encoding="utf-8")
random.seed(3)
for code in [f"{s}{i}" for s in "HGC" for i in range(1, 9)]:
    xs = [r for r in rows if r["策略"] == code and len(r["答案"]) == 1]
    out.write(f"\n## {code} ({len(xs)})\n")
    for ex in ("會考社會", "學測社會", "分科測驗"):
        ys = [r for r in xs if r["考試"] == ex]
        for r in random.sample(ys, min(5, len(ys))):
            out.write(f"{r['代號']} [{r['答案']}] {r['資料']} {r['陷阱']} {r['考點'][:20]} | {r['判讀提示'][:60]}\n")
print(len(rows))
