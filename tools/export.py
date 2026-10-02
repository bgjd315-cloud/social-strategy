#!/usr/bin/env python3
"""由 ../social-literacy 的題目與逐題判讀，依科目標上社會科閱讀策略（歷史 H1–H8、地理 G1–G8、公民 C1–C8），輸出 data/items.csv。

策略由判讀的能力（K/D/R/E）、資料類型（S0–S6）、陷阱與判讀提示的關鍵詞推得（規則見 strategy()），不是官方分類。
"""
import csv
import re
import sys
from collections import Counter
from pathlib import Path

R = Path(__file__).resolve().parents[1]
SRC = R.parent / "social-literacy"
sys.path.insert(0, str(SRC / "tools"))
from reading_data import build_reading  # noqa: E402

EXAM = ["會考社會", "學測社會", "分科測驗"]


def has(pat, t):
    return re.search(pat, t) is not None


def strategy(sub, abil, src, trap, text):
    if sub == "H":
        if src == "S3":
            return "H7"
        if src == "S4":
            return "H3"
        if trap in ("T2", "T7"):
            return "H8"
        if has(r"觀點|立場|作者|史料性質|可信|角度|看法|史家|解釋|詮釋", text):
            return "H6"
        if trap == "T1" or has(r"時代|年代|時期|朝代|先後|時序|順序|哪一年|世紀", text):
            return "H1"
        if trap == "T3" or has(r"原因|導致|影響|結果|背景|因而|目的", text):
            return "H4"
        if src == "S2" or has(r"比較|異同|變化|轉變|演變|差異|相同|不同", text):
            return "H5"
        if abil == "E" or has(r"觀點|立場|作者|史料性質|可信|角度|看法|評價|史家", text):
            return "H6"
        if src == "S1":
            return "H2"
        return "H8"
    if sub == "G":
        if has(r"GIS|遙測|圖層|環域|疊圖|衛星|座標|比例尺|等高線|經緯|時區|地理資訊|定位", text):
            return "G6"
        if src == "S4":
            return "G7"
        if src == "S3":
            return "G1"
        if has(r"氣候|降雨|雨量|氣溫|季風|地形|侵蝕|堆積|板塊|洋流|土壤|植被|冰河|颱風|河川|海岸", text):
            return "G3"
        if src == "S2":
            return "G2"
        if trap == "T3" or has(r"原因|導致|影響|災|永續|環境|開發|汙染|污染", text):
            return "G5"
        if abil == "E" or src == "S5":
            return "G8"
        return "G4"
    # 公民
    if src == "S2":
        return "C5"
    if has(r"需求|供給|價格|成本|市場|外部|貿易|匯率|稅|GDP|通膨|通貨|利率|消費|生產|廠商|所得", text):
        return "C4"
    if has(r"法|契約|侵權|訴訟|權利|處分|違憲|罰|告訴|判決|法院|檢察", text):
        return "C2"
    if has(r"選舉|總統|立法院|行政院|國會|政黨|內閣|地方自治|政府|權力分立|國際組織|聯合國|民主|公投", text):
        return "C3"
    if has(r"社會化|文化|團體|性別|族群|媒體|家庭|社區|多元|偏見|歧視", text):
        return "C7"
    if abil == "E" and src in ("S1", "S6") or has(r"觀點|價值|正義|倫理|立場|主張", text):
        return "C6"
    if abil == "K" or trap == "T2":
        return "C1"
    return "C8"


def main():
    rows = []
    for it in build_reading(SRC)["items"]:
        ei, y, no, lab, ans, abil, trap, hint, text, src, test, args, sub = it
        rows.append({"考試": EXAM[ei], "試卷": test, "年度": y, "題號": no, "科目": {"H": "歷史", "G": "地理", "C": "公民"}[sub],
                     "考點": lab, "答案": ans, "能力": abil, "資料": src, "陷阱": trap,
                     "策略": strategy(sub, abil, src, trap, f"{lab} {hint}"), "判讀提示": hint, "題目文字": text, "代號": f"{test}-{args.replace(',', '-')}"})
    out = R / "data" / "items.csv"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "題 →", out)
    for sub in ("歷史", "地理", "公民"):
        c = Counter(r["策略"] for r in rows if r["科目"] == sub)
        print(sub, sorted(c.items()))


if __name__ == "__main__":
    main()
