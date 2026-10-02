"""一次性：由 english-strategy/tools/student.py 改寫成社會科版 tools/student.py（歷史、地理、公民三科各 8 種策略）。"""
from pathlib import Path

R = Path(__file__).resolve().parents[1]
s = (R.parent / "english-strategy" / "tools" / "student.py").read_text("utf-8")


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:90], s.count(a))
    s = s.replace(a, b)


rep('"""產生英文閱讀理解策略的學生版互動網站', '"""產生社會科閱讀策略（歷史、地理、公民）的學生版互動網站')
rep('from content import EXPLAIN, STRATS', 'from content import EXPLAIN, STRATS, SUBJ')
rep('''    x["id"] = ("K" if x["考試"] == "會考英語" else "X") + x["年度"] + "-" + x["題號"]''', '''    x["id"] = x["代號"]''')
rep('''    return "會考" if x["考試"] == "會考英語" else "學測"''', '''    return {"會考社會": "會考", "學測社會": "學測", "分科測驗": "分科"}[x["考試"]]''')
rep('''N = Counter(group(x) for x in ITEMS)''', '''N = Counter((x["科目"], group(x)) for x in ITEMS)''')
rep('''        pct = {g: round(100 * sum(1 for x in xs if group(x) == g) / N[g]) for g in N}''',
    '''        sj = SUBJ[st["subj"]]
        pct = {g: round(100 * sum(1 for x in xs if group(x) == g) / N[(sj, g)]) for g in ("會考", "學測", "分科")}''')
rep('''        strats.append({"code": code, "name": st["name"], "en": st["en"],''', '''        strats.append({"code": code, "subj": st["subj"], "name": st["name"],''')
rep('''            kind = x["考點"].split("：")[0]
            qs[i] = {"src": f"{x['考試']} {x['年度']} 年第 {x['題號']} 題", "kind": kind, "no": x["題號"], "ans": ans,
                     "opts": "ABCDEFGHIJ"[:m["nopt"]],''', '''            no = x["題號"].split()[-1]
            src = f"分科{x['科目']} {x['年度']} 年第 {no} 題" if x["考試"] == "分科測驗" else f"{x['考試']} {x['年度']} 年第 {no} 題"
            qs[i] = {"src": src, "kind": "", "no": no, "ans": ans,
                     "opts": m["opts"],''')
rep('''    return {"strats": strats, "qs": qs}''', '''    return {"strats": strats, "qs": qs, "subj": SUBJ}''')
# 樣式
rep('''.blank{font-weight:700;color:var(--accent)}''', '''.blank{font-weight:700;color:var(--accent)}
.chiprow{display:flex;flex-wrap:wrap;gap:6px;align-items:center;width:100%}
.chiprow .sj{font-size:14px;color:var(--ink-3);min-width:2.6em}
h2.subh{margin-top:28px;padding-bottom:6px;border-bottom:1px solid var(--rule)}''')
rep('''details.passage summary{''', '''details.passage summary{''')
# 共用 JS
rep('''function curCode(){const h=location.hash.slice(1);return D.strats.some(s=>s.code===h)?h:"R1";}
function chips(page){
  const c=curCode();
  $("#chips").innerHTML=D.strats.map(s=>{const done=doneCount(s,page);return `<a class="chip" href="#${s.code}" aria-current="${s.code===c}">${s.code} ${esc(s.name)}${done?'<span class="dot" title="已作答"></span>':""}</a>`;}).join("");
}''', '''function curCode(){const h=location.hash.slice(1);return D.strats.some(s=>s.code===h)?h:"H1";}
function pctText(s){return ["會考","學測","分科"].map(g=>`${g} ${s.pct[g]}%`).join("、");}
function chips(page){
  const c=curCode();
  $("#chips").innerHTML=["H","G","C"].map(sj=>`<div class="chiprow"><b class="sj">${D.subj[sj]}</b>${D.strats.filter(s=>s.subj===sj).map(s=>{const done=doneCount(s,page);return `<a class="chip" href="#${s.code}" aria-current="${s.code===c}">${s.code} ${esc(s.name)}${done?'<span class="dot" title="已作答"></span>':""}</a>`;}).join("")}</div>`).join("");
}''')
rep('''<summary>閱讀文章（題組共用，可收合）</summary><img src="${q.g}" alt="${esc(q.src)} 題組文章"''',
    '''<summary>題組資料（同一題組共用，可收合）</summary><img src="${q.g}" alt="${esc(q.src)} 題組資料"''')
# 首頁：依科目分區
rep('''  $("#grid").innerHTML=D.strats.map(s=>{const d=s.picks.filter(i=>S.a[i]).length,r=s.picks.filter(i=>S.a[i]&&S.a[i].ok).length;
    return `<div class="tile"><p class="kicker">${s.code}・${esc(s.en)}</p><h3>${esc(s.name)}</h3><p>${esc(s.one)}</p>
    <div class="bar" role="img" aria-label="已作答 ${d} / 3 題"><span style="width:${d/3*100}%"></span></div>
    <p class="sub">已作答 ${d} / 3 題・答對 ${r} 題・會考 ${s.pct["會考"]}%、學測 ${s.pct["學測"]}%</p>
    <div class="row"><a class="btn ghost" href="handbook.html#${s.code}">讀手冊</a><a class="btn" href="worksheets.html#${s.code}">做學習單</a></div></div>`;}).join("");''',
    '''  $("#grid").innerHTML=["H","G","C"].map(sj=>{const ss=D.strats.filter(s=>s.subj===sj),ids=ss.flatMap(s=>s.picks),dn=ids.filter(i=>S.a[i]).length;
    return `<h2 class="subh" id="${sj}">${D.subj[sj]}　<span class="sub">已作答 ${dn} / ${ids.length} 題</span></h2><div class="grid">${ss.map(s=>{const d=s.picks.filter(i=>S.a[i]).length,r=s.picks.filter(i=>S.a[i]&&S.a[i].ok).length;
    return `<div class="tile"><p class="kicker">${D.subj[s.subj]}・${s.code}</p><h3>${esc(s.name)}</h3><p>${esc(s.one)}</p>
    <div class="bar" role="img" aria-label="已作答 ${d} / 3 題"><span style="width:${d/3*100}%"></span></div>
    <p class="sub">已作答 ${d} / 3 題・答對 ${r} 題・${pctText(s)}</p>
    <div class="row"><a class="btn ghost" href="handbook.html#${s.code}">讀手冊</a><a class="btn" href="worksheets.html#${s.code}">做學習單</a></div></div>`;}).join("")}</div>`;}).join("");''')
rep('''<p class="kicker">${s.code}・出現 ${s.n} 題（會考 ${s.pct["會考"]}%、學測 ${s.pct["學測"]}%）</p>''',
    '''<p class="kicker">${D.subj[s.subj]}・${s.code}・出現 ${s.n} 題（占${D.subj[s.subj]}題目：${pctText(s)}）</p>''')
rep('''<span class="en">${esc(s.en)}</span>''', '''<span class="en">${D.subj[s.subj]}</span>''', 2)
# 報告
rep('''w:Math.max(s.pct["會考"],s.pct["學測"])''', '''w:Math.max(s.pct["會考"],s.pct["學測"],s.pct["分科"])''')
rep('''<div class="stat"><b>${D_} / 36</b>已作答題數</div>''', '''<div class="stat"><b>${D_} / ${D.strats.length*3}</b>已作答題數</div>''')
rep('''<div class="stat"><b>${full} / 12</b>完成的學習單</div></div>''', '''<div class="stat"><b>${full} / ${D.strats.length}</b>完成的學習單</div></div>
  <p>${["H","G","C"].map(sj=>{const rr=rows.filter(x=>x.s.subj===sj),d=rr.reduce((a,x)=>a+x.d,0),r=rr.reduce((a,x)=>a+x.r,0);return `${D.subj[sj]}：${d?`答對 ${r} / ${d} 題（${Math.round(100*r/d)}%）`:"尚未作答"}`;}).join("　")}</p>''')
rep('''${D_<12?"（目前作答題數還不多''', '''${D_<24?"（目前作答題數還不多''')
rep('''  ${rows.map(x=>`<tr><td><b>${x.s.code}</b> ${esc(x.s.name)}</td>''', '''  ${rows.map(x=>`<tr><td><span class="sub">${D.subj[x.s.subj]}</span> <b>${x.s.code}</b> ${esc(x.s.name)}</td>''')
rep('''<span class="sub">（會考約 ${x.s.pct["會考"]}%、學測約 ${x.s.pct["學測"]}% 的題目用到）</span>''', '''<span class="sub">（${pctText(x.s)}）</span>''')
rep('''<p class="sub">依大考出題比例排序，越前面的策略越常考，越值得先加強。</p>''', '''<p class="sub">依大考出題比例排序（括號內是這種策略占該科會考、學測、分科題目的比例），越前面越常考，越值得先加強。</p>''')
rep('const KEY="english-strategy-v1";', 'const KEY="social-strategy-v1";')
rep('''本站收錄的國中教育會考英語與大學學測英文試題''', '''本站收錄的國中教育會考社會、大學學測社會與分科測驗歷史、地理、公民試題''')
rep('''大考中心・學測歷年試題</a>''', '''大考中心・學測與分科測驗歷年試題</a>''')
# 首頁文字；拿掉「兩種網站怎麼用」（社會科網站不連到其他網站）
i = s.index('\n<section class="card" style="margin-top:28px"><p class="kicker">搭配使用</p>')
j = s.index("</section>", i) + len("</section>")
s = s[:i] + s[j:]
rep('''    page("index.html", "英文閱讀理解策略", \'\'\'<header class="hero"><p class="kicker">會考英語・學測英文</p><h1>英文閱讀理解策略</h1>
<p>把會考英語閱讀和學測英文的題目整理成 12 種閱讀策略。''', '''    page("index.html", "社會科閱讀策略", \'\'\'<header class="hero"><p class="kicker">會考社會・學測社會・分科歷史地理公民</p><h1>社會科閱讀策略</h1>
<p>社會科考的是「讀資料」：史料、統計圖表、地圖、照片和生活情境。這裡把歷屆題目整理成歷史、地理、公民各 8 種閱讀策略。''')
rep('''<p class="sub">題目取自會考英語閱讀 111–115 年與學測英文 107–115 年（共 688 題）。''',
    '''<p class="sub">題目取自會考社會 111–115 年、學測社會與分科測驗歷史、地理、公民 107–115 年（共 2,078 題）。''')
rep('''<p style="margin-top:16px" id="summary"></p><div class="grid" id="grid"></div>''', '''<p style="margin-top:16px" id="summary"></p><div id="grid"></div>''')
rep('''    page("handbook.html", "英文閱讀策略手冊", '<header class="hero"><h1>英文閱讀策略手冊</h1><p>選一種策略''',
    '''    page("handbook.html", "社會科閱讀策略手冊", '<header class="hero"><h1>社會科閱讀策略手冊</h1><p>先選科目和策略''')
rep('''    page("worksheets.html", "英文策略學習單",''', '''    page("worksheets.html", "社會科策略學習單",''')
rep('''    page("report.html", "我的英文閱讀分析報告",''', '''    page("report.html", "我的社會科分析報告",''')
for bad in ("英文", "英語", "s.en"):
    assert bad not in s, [l for l in s.splitlines() if bad in l][:3]
(R / "tools" / "student.py").write_text(s, "utf-8", newline="\n")
print("ok")
