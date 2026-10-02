#!/usr/bin/env python3
"""產生社會科閱讀策略（歷史、地理、公民）的學生版互動網站（output/student/）：點選作答、立即回饋、按鍵看解析、寫下步驟與線索、記錄進度、產出分析報告。

頁面：index.html（12 種策略與我的進度）、handbook.html（策略手冊與例題）、worksheets.html（學習單）、report.html（我的分析報告）。
作答紀錄只存在使用者的瀏覽器（localStorage）。
"""
import csv
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / "tools"))
from content import EXPLAIN, STRATS, SUBJ  # noqa: E402
from picks import PICKS  # noqa: E402

OUT = R / "output" / "student"
ITEMS = list(csv.DictReader(open(R / "data" / "items.csv", encoding="utf-8-sig")))
for x in ITEMS:
    x["id"] = x["代號"]
BYID = {x["id"]: x for x in ITEMS}


def group(x):
    return {"會考社會": "會考", "學測社會": "學測", "分科測驗": "分科"}[x["考試"]]


N = Counter((x["科目"], group(x)) for x in ITEMS)
META = json.loads((R / "data" / "picks_meta.json").read_text("utf-8"))


def data():
    strats = []
    for code, st in STRATS.items():
        xs = [x for x in ITEMS if x["策略"] == code]
        sj = SUBJ[st["subj"]]
        pct = {g: round(100 * sum(1 for x in xs if group(x) == g) / N[(sj, g)]) for g in ("會考", "學測", "分科")}
        strats.append({"code": code, "subj": st["subj"], "name": st["name"], "one": st["one"], "signals": st["signals"], "steps": st["steps"],
                       "traps": st["traps"], "check": st["check"], "n": len(xs), "pct": pct, "picks": PICKS[code]})
    qs = {}
    for ids in PICKS.values():
        for i in ids:
            x = BYID[i]
            ans = x["答案"]
            multi = len(ans) > 1
            m = META[i]
            no = x["題號"].split()[-1]
            src = f"分科{x['科目']} {x['年度']} 年第 {no} 題" if x["考試"] == "分科測驗" else f"{x['考試']} {x['年度']} 年第 {no} 題"
            qs[i] = {"src": src, "kind": "", "no": no, "ans": ans,
                     "opts": m["opts"], "multi": multi, "why": EXPLAIN[i]["why"], "demo": EXPLAIN[i].get("demo", []),
                     "img": f"img/{webp(m['q'])}" if m.get("q") else "", "g": f"img/{webp(m['g'])}" if m.get("g") else ""}
    return {"strats": strats, "qs": qs, "subj": SUBJ}


def webp(name):
    return name.rsplit(".", 1)[0] + ".webp"


CSS = """
:root{color-scheme:light;--paper:#FAF9F6;--surface:#fff;--ink:#1E2227;--ink-2:#4A515A;--ink-3:#6F767F;--rule:#E3E1DB;--rule-2:#EFEDE8;
--accent:#C23B4E;--accent-soft:#F7E3E6;--ok:#2E9384;--ok-soft:#DDF0ED;--focus:#2F6DB5}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){color-scheme:dark;--paper:#16181B;--surface:#1E2125;--ink:#ECEDEF;--ink-2:#B9BEC5;
--ink-3:#8C929A;--rule:#33373D;--rule-2:#2A2E33;--accent:#E8687A;--accent-soft:#3A2227;--ok:#3FB3A2;--ok-soft:#18302D;--focus:#8FB3E0}}
*{box-sizing:border-box}
[hidden]{display:none!important}
body{margin:0;background:var(--paper);color:var(--ink);font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",system-ui,sans-serif;font-size:16px;line-height:1.8;padding:0 16px 72px}
.wrap{max-width:860px;margin:0 auto}
h1,h2,h3{font-family:"LXGW WenKai TC","Kaiti TC","DFKai-SB",serif;line-height:1.3;margin:0;text-wrap:balance}
h1{font-size:clamp(28px,5vw,40px)}h2{font-size:24px}h3{font-size:19px}
p{margin:0}a{color:var(--focus)}
:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
nav.top{display:flex;flex-wrap:wrap;gap:6px 18px;padding:14px 0;border-bottom:1px solid var(--rule);font-size:15px}
nav.top a{color:var(--ink-2);text-decoration:none}nav.top a[aria-current]{color:var(--accent);font-weight:700}
header.hero{padding:32px 0 20px;display:grid;gap:10px;border-bottom:2px solid var(--ink)}
.sub{color:var(--ink-3);font-size:14px}
.chips{display:flex;flex-wrap:wrap;gap:6px;padding:14px 0}
.chip{font:inherit;font-size:14px;padding:4px 12px;border:1px solid var(--rule);border-radius:999px;background:var(--surface);color:var(--ink-2);cursor:pointer;text-decoration:none}
.chip[aria-current="true"]{border-color:var(--ink);background:var(--ink);color:var(--paper);font-weight:700}
.chip .dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--ok);margin-left:6px;vertical-align:middle}
section.card{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:18px 20px;margin:16px 0;display:grid;gap:12px}
.kicker{font-size:12.5px;letter-spacing:.1em;color:var(--accent);font-weight:700}
ul,ol{margin:0;padding-left:1.4em;display:grid;gap:4px}
.q{display:grid;gap:10px}
details.passage{border:1px solid var(--rule);border-radius:8px;padding:8px 10px;background:var(--paper)}
details.passage summary{cursor:pointer;font-weight:700;font-size:15px}
details.passage img{margin-top:8px}
.blank{font-weight:700;color:var(--accent)}
.chiprow{display:flex;flex-wrap:wrap;gap:6px;align-items:center;width:100%}
.chiprow .sj{font-size:14px;color:var(--ink-3);min-width:2.6em}
h2.subh{margin-top:28px;padding-bottom:6px;border-bottom:1px solid var(--rule)}
.en{font-family:Georgia,"Times New Roman",serif;font-style:italic;color:var(--ink-3);font-weight:400}
.q img{display:block;max-width:100%;height:auto;background:#fff;border:1px solid var(--rule);border-radius:6px;padding:4px}
.opts{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.opt{font:inherit;font-size:18px;font-weight:700;width:48px;height:46px;border:1.5px solid var(--ink-3);border-radius:8px;background:var(--surface);color:var(--ink);cursor:pointer}
.opt[aria-pressed="true"]{border-color:var(--ink);background:var(--ink);color:var(--paper)}
.opt.right{border-color:var(--ok);background:var(--ok);color:#fff}.opt.wrong{border-color:var(--accent);background:var(--accent);color:#fff}
.opt:disabled{cursor:default}
.btn{text-decoration:none;display:inline-block;font:inherit;font-weight:700;font-size:15px;padding:8px 16px;border-radius:7px;border:0;background:var(--ink);color:var(--paper);cursor:pointer}
.btn.ghost{background:transparent;color:var(--ink);border:1.5px solid var(--ink)}
.btn:disabled{opacity:.4;cursor:default}
.row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.fb{border-radius:8px;padding:10px 14px;font-weight:700}
.fb.ok{background:var(--ok-soft);color:var(--ok)}.fb.ng{background:var(--accent-soft);color:var(--accent)}
.reveal{border-left:3px solid var(--accent);background:var(--rule-2);border-radius:4px;padding:10px 14px;display:grid;gap:8px}
textarea{font:inherit;font-size:15px;width:100%;min-height:64px;padding:8px 10px;border:1.5px solid var(--rule);border-radius:7px;background:var(--paper);color:var(--ink);resize:vertical}
textarea:focus{outline:none;border-color:var(--ink)}
label.ck{display:flex;gap:8px;align-items:flex-start;cursor:pointer}
label.ck input{width:18px;height:18px;margin-top:5px}
.step{display:grid;gap:6px;padding:10px 0;border-top:1px dashed var(--rule)}
.step b{font-size:15px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px;margin-top:16px}
.tile{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:14px 16px;display:grid;gap:8px;align-content:start}
.tile h3{font-size:18px}
section.card a{overflow-wrap:anywhere}
.bar{height:8px;border-radius:4px;background:var(--rule-2);overflow:hidden}.bar span{display:block;height:100%;background:var(--ok)}
.pager{display:flex;justify-content:space-between;gap:8px;margin-top:8px}
footer{margin-top:48px;padding-top:14px;border-top:1px solid var(--rule);font-size:12.5px;color:var(--ink-3);line-height:1.75}
footer a{color:inherit}
table{width:100%;border-collapse:collapse;font-size:15px}
th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--rule);vertical-align:middle}
th{font-size:13px;color:var(--ink-3);font-weight:700}
.tbl{overflow-x:auto;min-width:0}
.nw{white-space:nowrap}
section.card>*{min-width:0}
@media (max-width:520px){th,td{padding:6px 4px;font-size:14px}}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px}
.stat{border:1px solid var(--rule);border-radius:8px;padding:10px 12px}.stat b{display:block;font-size:26px;line-height:1.2}
.lv{font-size:13px;font-weight:700;padding:1px 8px;border-radius:999px;white-space:nowrap}
.lv.good{background:var(--ok-soft);color:var(--ok)}.lv.weak{background:var(--accent-soft);color:var(--accent)}.lv.none{background:var(--rule-2);color:var(--ink-3)}
.me{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px}
.me label{display:grid;gap:2px;font-size:14px;color:var(--ink-3)}
.me input{width:100%;min-width:0;font:inherit;font-size:16px;padding:6px 10px;border:1.5px solid var(--rule);border-radius:7px;background:var(--paper);color:var(--ink)}
@media print{nav.top,.chips,.pager,.no-print,footer{display:none}body{background:#fff}section.card{break-inside:avoid;border-color:#ccc}}
"""

FOOTER = ('<footer><p><b>著作權與來源說明</b>　本站收錄的國中教育會考社會、大學學測社會與分科測驗歷史、地理、公民試題，依著作權法第 9 條第 1 項第 5 款，屬依法令舉行之考試試題，'
          '不得為著作權之標的；但試題中引用的文章、詩文、圖片等，著作權仍屬原作者所有。本站僅供非營利之教學與研究使用。題目圖片裁切自官方公布的試卷，'
          '答案以官方公布為準；閱讀策略分類與解析為本站自行撰寫，並非官方解析。作答紀錄只存在你自己的裝置上。</p>'
          '<p>官方來源：<a href="https://cap.rcpet.edu.tw/examination.html" target="_blank" rel="noopener">國中教育會考・歷屆試題</a>｜'
          '<a href="https://www.ceec.edu.tw/xmfile?xsmsid=0J052424829869345634" target="_blank" rel="noopener">大考中心・學測與分科測驗歷年試題</a></p></footer>')

NAV = [("index.html", "首頁"), ("handbook.html", "閱讀策略手冊"), ("worksheets.html", "學習單"), ("report.html", "我的分析報告")]

# 共用程式：狀態儲存、作答元件
JS_CORE = r"""
const KEY="social-strategy-v1";
function load(){try{return JSON.parse(localStorage.getItem(KEY))||{a:{},n:{},c:{}};}catch(e){return {a:{},n:{},c:{}};}}
let S=load();
function save(){try{localStorage.setItem(KEY,JSON.stringify(S));}catch(e){}}
const $=s=>document.querySelector(s);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const strat=code=>D.strats.find(s=>s.code===code);
function curCode(){const h=location.hash.slice(1);return D.strats.some(s=>s.code===h)?h:"H1";}
function pctText(s){return ["會考","學測","分科"].map(g=>`${g} ${s.pct[g]}%`).join("、");}
function chips(page){
  const c=curCode();
  $("#chips").innerHTML=["H","G","C"].map(sj=>`<div class="chiprow"><b class="sj">${D.subj[sj]}</b>${D.strats.filter(s=>s.subj===sj).map(s=>{const done=doneCount(s,page);return `<a class="chip" href="#${s.code}" aria-current="${s.code===c}">${s.code} ${esc(s.name)}${done?'<span class="dot" title="已作答"></span>':""}</a>`;}).join("")}</div>`).join("");
}
function doneCount(s,page){const ids=page==="handbook"?s.picks.slice(0,2):s.picks;return ids.filter(i=>S.a[i]).length;}
function note(key,ph,rows){return `<textarea data-note="${key}" rows="${rows||2}" placeholder="${esc(ph)}">${esc(S.n[key]||"")}</textarea>`;}
function check(key,text){return `<label class="ck"><input type="checkbox" data-check="${key}" ${S.c[key]?"checked":""}><span>${esc(text)}</span></label>`;}
function wire(root){
  root.querySelectorAll("textarea[data-note]").forEach(t=>t.oninput=()=>{S.n[t.dataset.note]=t.value;save();});
  root.querySelectorAll("input[data-check]").forEach(c=>c.onchange=()=>{S.c[c.dataset.check]=c.checked;save();});
}
// 作答元件：選項、確認、回饋、看答案與解析（解析收在按鍵裡）
function question(id,opt){
  opt=opt||{};
  const q=D.qs[id];
  const passage=q.g?`<details class="passage" open><summary>題組資料（同一題組共用，可收合）</summary><img src="${q.g}" alt="${esc(q.src)} 題組資料" loading="lazy"></details>`:"";
  const stem=q.img?`<img src="${q.img}" alt="${esc(q.src)}" loading="lazy">`:`<p>請作答文章中的第 <span class="blank">${q.no}</span> 題空格（${esc(q.kind)}）。</p>`;
  return `<div class="q" data-q="${id}">${passage}${stem}${opt.mid||""}
  <p class="sub">${q.multi?"多選題：選出所有正確的選項，再按「確認答案」。":q.opts.length>5?"從文章下方的 (A)–(J) 選一個字，再按「確認答案」。":"單選題：選一個答案，再按「確認答案」。"}</p>
  <div class="opts">${q.opts.split("").map(o=>`<button type="button" class="opt" data-o="${o}" aria-pressed="false">${o}</button>`).join("")}
  <button type="button" class="btn" data-act="ok" disabled>確認答案</button></div>
  <div data-fb></div>
  <div class="row no-print"><button type="button" class="btn ghost" data-act="show" hidden>看答案與解析</button><button type="button" class="btn ghost" data-act="retry" hidden>重新作答</button></div>
  <div class="reveal" data-rev hidden>${opt.demo&&q.demo.length?`<p><b>解題步驟</b></p><ol>${q.demo.map(s=>`<li>${esc(s)}</li>`).join("")}</ol>`:""}<p><b>答案：${q.ans}</b>　${esc(q.why)}</p></div></div>`;
}
function wireQuestions(root,onChange){
  root.querySelectorAll("[data-q]").forEach(box=>{
    const id=box.dataset.q,q=D.qs[id],sel=new Set();
    const opts=[...box.querySelectorAll(".opt")],ok=box.querySelector('[data-act="ok"]'),show=box.querySelector('[data-act="show"]'),
          retry=box.querySelector('[data-act="retry"]'),fb=box.querySelector("[data-fb]"),rev=box.querySelector("[data-rev]");
    function judged(r){
      opts.forEach(b=>{b.disabled=true;const o=b.dataset.o;b.classList.toggle("right",r.ok&&q.ans.includes(o));b.classList.toggle("wrong",r.pick.includes(o)&&!q.ans.includes(o));b.setAttribute("aria-pressed",r.pick.includes(o));});
      ok.disabled=true;ok.hidden=true;
      fb.innerHTML=r.ok?`<div class="fb ok">答對了！你選 ${r.pick}</div>`:`<div class="fb ng">還不對喔，你選 ${r.pick}。可以回頭用策略步驟再檢查一次，或看答案與解析。</div>`;
      show.hidden=false;retry.hidden=false;
    }
    function reset(){sel.clear();opts.forEach(b=>{b.disabled=false;b.classList.remove("right","wrong");b.setAttribute("aria-pressed","false");});ok.hidden=false;ok.disabled=true;fb.innerHTML="";show.hidden=true;retry.hidden=true;rev.hidden=true;show.textContent="看答案與解析";}
    opts.forEach(b=>b.onclick=()=>{const o=b.dataset.o;if(!q.multi)sel.clear();sel.has(o)?sel.delete(o):sel.add(o);opts.forEach(x=>x.setAttribute("aria-pressed",sel.has(x.dataset.o)));ok.disabled=!sel.size;});
    ok.onclick=()=>{const pick=[...sel].sort().join("");const r={pick,ok:pick===q.ans};S.a[id]=r;save();judged(r);onChange&&onChange();};
    show.onclick=()=>{rev.hidden=!rev.hidden;show.textContent=rev.hidden?"看答案與解析":"收起解析";};
    retry.onclick=()=>{delete S.a[id];save();reset();onChange&&onChange();};
    if(S.a[id])judged(S.a[id]);
  });
}
"""

JS_INDEX = r"""
function render(){
  const all=D.strats.flatMap(s=>s.picks),done=all.filter(i=>S.a[i]),right=done.filter(i=>S.a[i].ok);
  $("#summary").innerHTML=`已作答 <b>${done.length}</b> / ${all.length} 題，答對 <b>${right.length}</b> 題。`;
  $("#grid").innerHTML=["H","G","C"].map(sj=>{const ss=D.strats.filter(s=>s.subj===sj),ids=ss.flatMap(s=>s.picks),dn=ids.filter(i=>S.a[i]).length;
    return `<h2 class="subh" id="${sj}">${D.subj[sj]}　<span class="sub">已作答 ${dn} / ${ids.length} 題</span></h2><div class="grid">${ss.map(s=>{const d=s.picks.filter(i=>S.a[i]).length,r=s.picks.filter(i=>S.a[i]&&S.a[i].ok).length;
    return `<div class="tile"><p class="kicker">${D.subj[s.subj]}・${s.code}</p><h3>${esc(s.name)}</h3><p>${esc(s.one)}</p>
    <div class="bar" role="img" aria-label="已作答 ${d} / 3 題"><span style="width:${d/3*100}%"></span></div>
    <p class="sub">已作答 ${d} / 3 題・答對 ${r} 題・${pctText(s)}</p>
    <div class="row"><a class="btn ghost" href="handbook.html#${s.code}">讀手冊</a><a class="btn" href="worksheets.html#${s.code}">做學習單</a></div></div>`;}).join("")}</div>`;}).join("");
}
$("#reset").onclick=()=>{if(confirm("確定要清除這台裝置上的所有作答與筆記嗎？")){S={a:{},n:{},c:{}};save();render();}};
render();
"""

JS_HANDBOOK = r"""
function render(){
  const s=strat(curCode());chips("handbook");
  const i=D.strats.indexOf(s),prev=D.strats[i-1],next=D.strats[i+1];
  $("#main").innerHTML=`<section class="card"><p class="kicker">${D.subj[s.subj]}・${s.code}・出現 ${s.n} 題（占${D.subj[s.subj]}題目：${pctText(s)}）</p>
  <h2>${esc(s.name)} <span class="en">${D.subj[s.subj]}</span></h2><p><b>${esc(s.one)}</b></p>
  <h3>看到這些就用它</h3><ul>${s.signals.map(x=>`<li>${esc(x)}</li>`).join("")}</ul>
  <h3>操作步驟</h3><ol>${s.steps.map(x=>`<li>${esc(x)}</li>`).join("")}</ol>
  <h3>常見陷阱</h3><p>${esc(s.traps)}</p></section>
  ${s.picks.slice(0,2).map((id,k)=>`<section class="card"><p class="kicker">例題 ${k+1}</p><h3>${esc(D.qs[id].src)}</h3>${question(id)}</section>`).join("")}
  <section class="card"><h3>自我檢核</h3>${s.check.map((c,k)=>check(`hb-${s.code}-${k}`,c)).join("")}</section>
  <div class="pager">${prev?`<a class="btn ghost" href="#${prev.code}">← ${prev.code} ${esc(prev.name)}</a>`:"<span></span>"}
  <a class="btn" href="worksheets.html#${s.code}">做這個策略的學習單 →</a>
  ${next?`<a class="btn ghost" href="#${next.code}">${next.code} ${esc(next.name)} →</a>`:"<span></span>"}</div>`;
  wire($("#main"));wireQuestions($("#main"),()=>chips("handbook"));
  window.scrollTo(0,0);
}
addEventListener("hashchange",render);render();
"""

JS_WORKSHEETS = r"""
function render(){
  const s=strat(curCode());chips("worksheets");
  const [demo,p1,p2]=s.picks,i=D.strats.indexOf(s),prev=D.strats[i-1],next=D.strats[i+1];
  $("#main").innerHTML=`<section class="card"><p class="kicker">學習單 ${i+1}</p><h2>${s.code} ${esc(s.name)} <span class="en">${D.subj[s.subj]}</span></h2>
  <p><b>策略卡：</b>${esc(s.one)}</p><ol>${s.steps.map(x=>`<li>${esc(x)}</li>`).join("")}</ol></section>
  <section class="card"><p class="kicker">一、示範題</p><h3>${esc(D.qs[demo].src)}</h3>
  <p>先讀題目，再跟著策略步驟想一想，把每一步的發現寫下來，最後作答。</p>
  ${question(demo,{demo:true,mid:`<div>${s.steps.map((st,k)=>`<div class="step"><b>步驟 ${k+1}：${esc(st)}</b>${note(`ws-${s.code}-d${k}`,"我的發現……")}</div>`).join("")}</div>`})}</section>
  ${[p1,p2].map((id,k)=>`<section class="card"><p class="kicker">${k?"三":"二"}、練習 ${k+1}</p><h3>${esc(D.qs[id].src)}</h3>
  <p>先讀題目，寫下你找到的證據或線索，再作答。</p>${question(id,{mid:`<div class="step"><b>我找到的證據或線索</b>${note(`ws-${s.code}-p${k}`,"寫下原文中支持你答案的句子或線索……",3)}</div>`})}</section>`).join("")}
  <section class="card"><p class="kicker">四、反思</p><div id="score"></div>${s.check.map((c,k)=>check(`ws-${s.code}-c${k}`,c)).join("")}
  <p>這次最容易出錯的地方是：</p>${note(`ws-${s.code}-r`,"寫下你的反思……",3)}</section>
  <div class="pager">${prev?`<a class="btn ghost" href="#${prev.code}">← ${prev.code} ${esc(prev.name)}</a>`:"<span></span>"}
  <button type="button" class="btn ghost no-print" onclick="print()">列印這份學習單</button>
  ${next?`<a class="btn ghost" href="#${next.code}">${next.code} ${esc(next.name)} →</a>`:"<span></span>"}</div>`;
  const score=()=>{const d=s.picks.filter(x=>S.a[x]),r=d.filter(x=>S.a[x].ok);$("#score").innerHTML=`<p><b>本份學習單：已作答 ${d.length} / 3 題，答對 ${r.length} 題。</b></p>`;chips("worksheets");};
  wire($("#main"));wireQuestions($("#main"),score);score();
  window.scrollTo(0,0);
}
addEventListener("hashchange",render);render();
"""


JS_REPORT = r"""
const ME=[["me-name","姓名"],["me-class","班級"],["me-no","座號"]];
function level(d,r){if(!d)return["未作答","none"];if(r<d)return["需要加強","weak"];return d===3?["精熟","good"]:["目前全對（未做完）","good"];}
function render(){
  const rows=D.strats.map(s=>{const done=s.picks.filter(i=>S.a[i]),right=done.filter(i=>S.a[i].ok);
    return {s,d:done.length,r:right.length,wrong:done.filter(i=>!S.a[i].ok),w:Math.max(s.pct["會考"],s.pct["學測"],s.pct["分科"]),lv:level(done.length,right.length)};});
  const D_=rows.reduce((a,x)=>a+x.d,0),R_=rows.reduce((a,x)=>a+x.r,0),rate=D_?Math.round(100*R_/D_):0,full=rows.filter(x=>x.d===3).length;
  const today=new Date().toLocaleDateString("zh-TW");
  let html=`<section class="card"><p class="kicker">基本資料</p><div class="me">${ME.map(([k,t])=>`<label>${t}<input data-me="${k}" value="${esc(S.n[k]||"")}"></label>`).join("")}
  <label>產出日期<input value="${today}" readonly></label></div></section>`;
  if(!D_){$("#main").innerHTML=html+`<section class="card"><p>你還沒有作答紀錄。先到<a href="worksheets.html">學習單</a>做題目，做完再回來看報告。</p></section>`;wireMe();return;}
  const comment=rate>=85?"整體表現很好，大部分策略都能正確運用。接下來可以挑戰還沒做完的策略，並試著向同學說明你的解題步驟。":
    rate>=60?"大致掌握了閱讀策略，但有幾種策略還不穩定。先從下面「優先加強」的策略開始，回到手冊複習步驟，再重做一次學習單。":
    "閱讀策略的基礎還需要加強。建議一次只練一種策略：先讀手冊、照步驟做示範題，答錯時把原因寫進反思，再做練習題。";
  html+=`<section class="card"><p class="kicker">整體表現</p><div class="stats">
  <div class="stat"><b>${D_} / ${D.strats.length*3}</b>已作答題數</div><div class="stat"><b>${R_}</b>答對題數</div>
  <div class="stat"><b>${rate}%</b>正確率</div><div class="stat"><b>${full} / ${D.strats.length}</b>完成的學習單</div></div>
  <p>${["H","G","C"].map(sj=>{const rr=rows.filter(x=>x.s.subj===sj),d=rr.reduce((a,x)=>a+x.d,0),r=rr.reduce((a,x)=>a+x.r,0);return `${D.subj[sj]}：${d?`答對 ${r} / ${d} 題（${Math.round(100*r/d)}%）`:"尚未作答"}`;}).join("　")}</p>
  <p>${comment}${D_<24?"（目前作答題數還不多，這份報告只反映部分情況。）":""}</p></section>`;
  html+=`<section class="card"><p class="kicker">各策略表現</p><div class="tbl"><table><thead><tr><th>策略</th><th>答對</th><th style="min-width:80px">正確率</th><th>判定</th></tr></thead><tbody>
  ${rows.map(x=>`<tr><td><span class="sub">${D.subj[x.s.subj]}</span> <b>${x.s.code}</b> ${esc(x.s.name)}</td><td class="nw">${x.d?`${x.r} / ${x.d}`:"—"}</td>
  <td>${x.d?`<div class="bar"><span style="width:${100*x.r/x.d}%"></span></div><span class="sub">${Math.round(100*x.r/x.d)}%</span>`:"—"}</td>
  <td><span class="lv ${x.lv[1]}">${x.lv[0]}</span></td></tr>`).join("")}</tbody></table></div></section>`;
  const good=rows.filter(x=>x.d&&x.r===x.d),weak=rows.filter(x=>x.r<x.d).sort((a,b)=>b.w-a.w),none=rows.filter(x=>!x.d).sort((a,b)=>b.w-a.w);
  html+=`<section class="card"><p class="kicker">我的優勢</p>${good.length?`<ul>${good.map(x=>`<li><b>${x.s.code} ${esc(x.s.name)}</b>：${esc(x.s.one)}${x.d<3?`（還有 ${3-x.d} 題沒做）`:""}</li>`).join("")}</ul>`:"<p>目前還沒有全部答對的策略，繼續加油！</p>"}</section>`;
  html+=`<section class="card"><p class="kicker">優先加強</p>${weak.length?`<p class="sub">依大考出題比例排序（括號內是這種策略占該科會考、學測、分科題目的比例），越前面越常考，越值得先加強。</p>`+weak.map(x=>`<div class="step">
  <b>${x.s.code} ${esc(x.s.name)}　答對 ${x.r} / ${x.d}　<span class="sub">（${pctText(x.s)}）</span></b>
  <p>答錯的題目：${x.wrong.map(i=>`${esc(D.qs[i].src)}（你選 ${S.a[i].pick}）`).join("；")}</p>
  <p><b>要注意：</b>${esc(x.s.traps)}</p>
  <p><b>下次照這個步驟：</b>${x.s.steps.map((t,k)=>`${k+1}. ${esc(t)}`).join("　")}</p>
  <p class="no-print"><a href="handbook.html#${x.s.code}">複習手冊</a>　<a href="worksheets.html#${x.s.code}">重做學習單</a></p></div>`).join(""):"<p>目前沒有答錯的策略。</p>"}</section>`;
  if(none.length)html+=`<section class="card"><p class="kicker">還沒練習的策略</p><p>${none.map(x=>`<a href="worksheets.html#${x.s.code}">${x.s.code} ${esc(x.s.name)}</a>`).join("、")}</p>
  <p class="sub">排在前面的策略在大考比較常出現，建議先練。</p></section>`;
  const refl=rows.filter(x=>(S.n[`ws-${x.s.code}-r`]||"").trim());
  const ck=rows.map(x=>x.s.check.filter((c,k)=>S.c[`ws-${x.s.code}-c${k}`]||S.c[`hb-${x.s.code}-${k}`]).length),ckAll=rows.reduce((a,x)=>a+x.s.check.length,0);
  html+=`<section class="card"><p class="kicker">我的反思</p><p>自我檢核：勾選了 ${ck.reduce((a,b)=>a+b,0)} / ${ckAll} 項。</p>
  ${refl.length?refl.map(x=>`<div class="step"><b>${x.s.code} ${esc(x.s.name)}</b><p>${esc(S.n[`ws-${x.s.code}-r`])}</p></div>`).join(""):"<p class=\"sub\">還沒有寫反思。學習單最後的反思欄位寫下答錯的原因，會出現在這裡。</p>"}</section>`;
  html+=`<div class="row no-print"><button type="button" class="btn" onclick="print()">列印或存成 PDF</button>
  <span class="sub">要存成 PDF：按下後在「目的地」選「另存為 PDF」。</span></div>`;
  $("#main").innerHTML=html;wireMe();
}
function wireMe(){document.querySelectorAll("input[data-me]").forEach(t=>t.oninput=()=>{S.n[t.dataset.me]=t.value;save();});}
render();
"""

def page(fname, title, body, js):
    nav = "".join(f'<a href="{f}"{" aria-current=page" if f == fname else ""}>{t}</a>' for f, t in NAV)
    html = (f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="robots" content="noindex,nofollow"><title>{title}</title>'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=LXGW+WenKai+TC:wght@400;700&family=Noto+Sans+TC:wght@400;500;700&display=swap">'
            f'<style>{CSS}</style></head><body><div class="wrap"><nav class="top">{nav}</nav>{body}{FOOTER}</div>'
            f'<script src="data.js"></script><script>{JS_CORE}{js}</script></body></html>')
    (OUT / fname).write_text(html, "utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    (OUT / "img").mkdir()
    for f in sorted((R / "output" / "img").glob("*.png")):
        Image.open(f).save(OUT / "img" / webp(f.name), "WEBP", quality=80, method=6)
    (OUT / "data.js").write_text("const D=" + json.dumps(data(), ensure_ascii=False) + ";\n", "utf-8")
    page("index.html", "社會科閱讀策略", '''<header class="hero"><p class="kicker">會考社會・學測社會・分科歷史地理公民</p><h1>社會科閱讀策略</h1>
<p>社會科考的是「讀資料」：史料、統計圖表、地圖、照片和生活情境。這裡把歷屆題目整理成歷史、地理、公民各 8 種閱讀策略。先讀<a href="handbook.html">閱讀策略手冊</a>學方法，再用<a href="worksheets.html">學習單</a>練習：
點選答案、按「確認答案」看對錯，想看解析再按「看答案與解析」。</p>
<p class="sub">題目取自會考社會 111–115 年、學測社會與分科測驗歷史、地理、公民 107–115 年（共 2,078 題）。你的作答、筆記與勾選會自動存在這台裝置上。</p></header>
<p style="margin-top:16px" id="summary"></p><div id="grid"></div>
<div class="row no-print" style="margin-top:20px"><a class="btn" href="report.html">看我的分析報告</a>
<button type="button" class="btn ghost" id="reset">清除我的作答紀錄</button></div>
<section class="card" style="margin-top:28px"><p class="kicker">搭配使用</p><h2>兩種網站怎麼用？</h2>
<p>老師準備了兩種網站，用的都是會考、學測和分科測驗的歷屆題目，但用途不一樣。</p>
<h3>閱讀策略網站：學方法</h3>
<ul><li>社會：<a href="https://bgjd315-cloud.github.io/social-strategy/">https://bgjd315-cloud.github.io/social-strategy/</a>（就是這個網站）</li></ul>
<p>把史料、圖表、地圖和生活情境的讀法，整理成歷史、地理、公民各 8 種閱讀策略：先讀手冊學方法，再做學習單練習（答案與解析按鍵才出現），最後看分析報告，了解自己的強項和需要加強的地方。</p>
<h3>判讀網站：大量練習</h3>
<ul><li>社會：<a href="https://bgjd315-cloud.github.io/social-literacy/">https://bgjd315-cloud.github.io/social-literacy/</a></li></ul>
<p>收錄全部 2,078 題歷屆題目，每一題都標出在考什麼能力、用了哪種資料、陷阱在哪裡，還可以依科目抽題練習。學會方法以後，到這裡多做題目，看看自己能不能把策略用出來。</p>
<p><b>建議的順序：</b>先到策略網站學方法、打好基本功，再到判讀網站多練習。</p></section>''', JS_INDEX)
    page("handbook.html", "社會科閱讀策略手冊", '<header class="hero"><h1>社會科閱讀策略手冊</h1><p>先選科目和策略，讀懂它的用法，再做兩題歷屆例題。</p></header>'
         '<div class="chips" id="chips"></div><div id="main"></div>', JS_HANDBOOK)
    page("worksheets.html", "社會科策略學習單", '<header class="hero"><h1>學習單</h1><p>每份學習單練一種策略：先跟著步驟做示範題，再做兩題練習，最後寫反思。</p></header>'
         '<div class="chips" id="chips"></div><div id="main"></div>', JS_WORKSHEETS)
    page("report.html", "我的社會科分析報告", '<header class="hero"><h1>我的分析報告</h1><p>根據你在學習單和手冊例題的作答、筆記與反思，自動整理出你的閱讀策略表現。'
         '填好姓名，就可以列印或存成 PDF 交給老師。</p></header><div id="main"></div>', JS_REPORT)
    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n", "utf-8")
    (OUT / ".nojekyll").write_text("", "utf-8")
    print("學生版網站：", OUT)


if __name__ == "__main__":
    main()
