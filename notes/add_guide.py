"""一次性：在社會科策略網站首頁加上「兩種網站怎麼用」的說明，連到社會判讀網站（題庫）。"""
from pathlib import Path

U = "https://bgjd315-cloud.github.io/"
GUIDE = f'''
<section class="card" style="margin-top:28px"><p class="kicker">搭配使用</p><h2>兩種網站怎麼用？</h2>
<p>老師準備了兩種網站，用的都是會考、學測和分科測驗的歷屆題目，但用途不一樣。</p>
<h3>閱讀策略網站：學方法</h3>
<ul><li>社會：<a href="{U}social-strategy/">{U}social-strategy/</a>（就是這個網站）</li></ul>
<p>把史料、圖表、地圖和生活情境的讀法，整理成歷史、地理、公民各 8 種閱讀策略：先讀手冊學方法，再做學習單練習（答案與解析按鍵才出現），最後看分析報告，了解自己的強項和需要加強的地方。</p>
<h3>判讀網站：大量練習</h3>
<ul><li>社會：<a href="{U}social-literacy/">{U}social-literacy/</a></li></ul>
<p>收錄全部 2,078 題歷屆題目，每一題都標出在考什麼能力、用了哪種資料、陷阱在哪裡，還可以依科目抽題練習。學會方法以後，到這裡多做題目，看看自己能不能把策略用出來。</p>
<p><b>建議的順序：</b>先到策略網站學方法、打好基本功，再到判讀網站多練習。</p></section>'''
ANCHOR = '<button type="button" class="btn ghost" id="reset">清除我的作答紀錄</button></div>'

p = Path(__file__).resolve().parents[1] / "tools" / "student.py"
s = p.read_text("utf-8")
assert s.count(ANCHOR) == 1 and "兩種網站怎麼用" not in s
s = s.replace(ANCHOR, ANCHOR + GUIDE)
if "section.card a{overflow-wrap:anywhere}" not in s:
    s = s.replace(".tile h3{font-size:18px}", ".tile h3{font-size:18px}\nsection.card a{overflow-wrap:anywhere}")
p.write_text(s, "utf-8", newline="\n")
print("ok")
