#!/usr/bin/env python3
"""依 ../social-literacy 的試卷圖片與裁切範圍，產生 picks.py 選用題目的圖片（output/img）與 data/picks_meta.json。

<代號>-q.png：題目；<試卷>-<年度>-g<頁>-<上緣>.png：題組資料（同一題組只產生一次）。
會考的裁切有裁切框與白色遮罩（隱藏同頁的其他題目），學測、分科只有上下範圍。
"""
import json
import sys
from pathlib import Path

from PIL import Image

R = Path(__file__).resolve().parents[1]
SRC = R.parent / "social-literacy"
sys.path.insert(0, str(SRC / "tools"))
sys.path.insert(0, str(R / "tools"))
from picks import PICKS  # noqa: E402
from reading_data import build_practice  # noqa: E402

OUT = R / "output" / "img"
_cache = {}


def page(pre, p):
    f = SRC / "assets" / f"{pre}{p}.webp"
    if f not in _cache:
        _cache[f] = Image.open(f).convert("RGB")
    return _cache[f]


def render(slices, pg):
    W, H, x0, xw, pre = pg
    parts = []
    for p, a, b, clips, masks in slices:
        im = page(pre, p)
        s = im.width / W
        box = [round(v * s) for v in (x0, a, x0 + xw, b)]
        if clips:
            out = Image.new("RGB", (box[2] - box[0], box[3] - box[1]), "white")
            for x, yy, w, h in clips:
                c = [round(v * s) for v in (x, yy, x + w, yy + h)]
                c = [max(c[0], box[0]), max(c[1], box[1]), min(c[2], box[2]), min(c[3], box[3])]
                if c[2] > c[0] and c[3] > c[1]:
                    out.paste(im.crop(c), (c[0] - box[0], c[1] - box[1]))
            for x, yy, w, h in masks:
                out.paste("white", [round(v * s) for v in (x - x0, yy - a, x - x0 + w, yy - a + h)])
        else:
            out = im.crop(box)
        parts.append(out)
    total = Image.new("RGB", (max(p.width for p in parts), sum(p.height for p in parts)), "white")
    yy = 0
    for p in parts:
        total.paste(p, (0, yy))
        yy += p.height
    return total


def main():
    items = {it[13]: it for it in build_practice(SRC)["items"]}
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {}
    for ids in PICKS.values():
        for i in ids:
            it = items[i]
            m = {"opts": it[10], "q": f"{i}-q.png"}
            render(it[8], it[12]).save(OUT / m["q"], optimize=True)
            if it[9]:
                p0, a0 = it[9][0][0], round(it[9][0][1])
                m["g"] = f"{i.rsplit('-', 1)[0]}-g{p0}-{a0}.png"
                if not (OUT / m["g"]).exists():
                    render(it[9], it[12]).save(OUT / m["g"], optimize=True)
            meta[i] = m
    (R / "data" / "picks_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), "utf-8")
    print(len(meta), "題，圖片在", OUT)


if __name__ == "__main__":
    main()
