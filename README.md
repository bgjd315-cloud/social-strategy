# 社會科閱讀策略・學生版

用會考社會（111–115 年）、學測社會與分科測驗歷史、地理、公民（107–115 年）共 2,078 題，整理成歷史、地理、公民各 8 種閱讀策略的互動練習網站。只有學生版，沒有教師資料。

## 資料夾

| 路徑 | 內容 |
|---|---|
| `data/items.csv` | 2,078 題：考試、試卷、年度、題號、科目、考點、答案、能力、資料類型、陷阱、策略、判讀提示、題目文字、代號（UTF-8，可用 Excel 開啟） |
| `data/picks_meta.json` | 選用題目的選項與圖片檔名（由 crop.py 產生） |
| `tools/export.py` | 由 ../social-literacy 的題目與逐題判讀，依規則標上策略，輸出 items.csv |
| `tools/picks.py` | 每種策略選用的三題（第一題是學習單的示範題） |
| `tools/content.py` | 24 種策略的說明與 72 題的解析 |
| `tools/crop.py` | 從 ../social-literacy 的試卷圖片裁切題目與題組資料（output/img，不提交） |
| `tools/student.py` | 產生學生版互動網站（output/student） |
| `tools/candidates.py`、`tools/dump_picks.py` | 挑選例題、撰寫解析時用的清單 |

## 24 種策略

- 歷史：H1 時代定位、H2 文字史料解讀、H3 圖像與文物解讀、H4 因果與影響推論、H5 比較與變遷、H6 觀點與史料性質、H7 歷史地圖與空間、H8 概念與名詞辨析
- 地理：G1 地圖與區位判讀、G2 統計圖表判讀、G3 氣候與自然環境推論、G4 區域特色與比較、G5 人地互動與因果、G6 地理資訊與技術、G7 照片與景觀判讀、G8 情境應用與規劃
- 公民：C1 概念辨析、C2 法律案例判斷、C3 政府與政治制度、C4 經濟原理推論、C5 統計圖表判讀、C6 觀點與價值評估、C7 社會與文化現象、C8 生活情境應用

策略由 social-literacy 的逐題判讀（能力 K/D/R/E、資料類型 S0–S6、陷阱 T1–T7、判讀提示關鍵詞）依規則推得，規則見 `tools/export.py`。分類與解析為本站判讀，不是官方分類。

## 重新產生網站

```bash
python tools/export.py    # 需要 ../social-literacy
python tools/crop.py      # 需要 ../social-literacy/assets
python tools/student.py
```

推送到 GitHub 後，由 GitHub Actions 把 `output/student/` 發布到 GitHub Pages。這個 repo 是公開的，只放學生看得到的內容。網站不連到其他網站。
