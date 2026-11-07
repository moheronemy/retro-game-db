#!/usr/bin/env python3
"""バンダイの光速船（1983年7月発売。米国 GCE の Vectrex の日本版）のソフト一覧を作る。

出典は ja.wikipedia「光速船」の「ソフトウェア」節の箇条書きだけ（「などが発売された」とあり全件ではない）。
本体内蔵の『マインストーム』は除く。MAME `vectrex`・No-Intro（GCE - Vectrex）に日本版の項目が無く、MADB にも記録が無いため、
発売日・価格・型番・ハッシュは空欄（米国版と中身が同じかは出典で確かめられない）。

出力: data/vectrex/jp_titles.csv
使い方: python3 scripts/build_vectrex.py
"""
import re
import sys

import common as C

DIR = C.ROOT / "data" / "vectrex"
PAGE = "光速船"


def wiki_text():
    cache = C.CACHE / "wikipedia" / f"{PAGE}.wiki"
    if not cache.exists():
        import fetch_wikipedia_list as F
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(F.fetch_wikitext(PAGE)[0], encoding="utf-8")
    return cache.read_text(encoding="utf-8")


def main():
    text = wiki_text()
    sec = text[text.index("== ソフトウェア =="):text.index("== マーケティング")]
    rows = []
    for m in re.finditer(r"^\*\s*(.+?)(?:\s+-\s+(.*))?$", sec, re.M):
        raw, desc = m.group(1), m.group(2) or ""
        if "本体内蔵" in desc:
            continue
        link = re.match(r"\[\[([^|\]]+)", raw)
        title = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", raw).strip()
        rows.append({"release_date": "", "title": title, "publisher": "バンダイ", "model_number": "", "price_yen": "",
                     "price_tax": "", "notes": "", "wikipedia_article": link.group(1).split("#")[0] if link else "",
                     "release_date_sources": ""})
    if len(rows) != 5:
        sys.exit(f"ソフトウェア節の本数が想定（5）と違います: {[r['title'] for r in rows]}")
    for i, r in enumerate(rows, 1):
        r["id"] = f"vectrex-jp-{i:04d}"
    C.write_csv(DIR / "jp_titles.csv", rows, ["id", "release_date", "title", "publisher", "model_number", "price_yen",
                                              "price_tax", "notes", "wikipedia_article", "release_date_sources"])
    print(f"{len(rows)} 件（全件ではない）", file=sys.stderr)


if __name__ == "__main__":
    main()
