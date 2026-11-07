#!/usr/bin/env python3
"""エポック社のゲームポケコン（ゲームポケットコンピュータ、1984年発売）のソフト一覧を作る。

出典:
  タイトル・説明     ja.wikipedia「ゲームポケコン」の「ソフトウェア」節（箇条書き。5 本。本文に「ソフトは自社のみからの供給で5本のみ」）
  年・番号・ハッシュ  MAME `gamepock`（年は発売年か著作権表記の年か分からない。serial はカセットの番号とみられ、型番かどうか分からない）
MADB に記録が無く、No-Intro（libretro）にも DAT が無い。MAME の 2010年の個人制作デモは対象外。

出力: data/gamepock/jp_titles.csv、data/gamepock/jp_rom_dumps.csv
使い方: python3 scripts/build_gamepock.py
"""
import re
import sys
import xml.etree.ElementTree as ET

import common as C

DIR = C.ROOT / "data" / "gamepock"
PAGE = "ゲームポケコン"
# Wikipedia の題名 → MAME のソフト名
WIKI_TO_MAME = {"アストロボンバー": "astrobom", "ブロックメイズ": "blockmaz", "ポケコン マージャン": "pokemahj",
                "ポケコン リバーシ": "pokereve", "倉庫番": "sokoban"}


def wiki_text():
    cache = C.CACHE / "wikipedia" / f"{PAGE}.wiki"
    if not cache.exists():
        import fetch_wikipedia_list as F
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(F.fetch_wikitext(PAGE)[0], encoding="utf-8")
    return cache.read_text(encoding="utf-8")


def plain(s):
    s = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>", "", s)
    return re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", s).strip()


def main():
    text = wiki_text()
    sec = text[text.index("== ソフトウェア =="):]
    sec = sec[:sec.index("カートリッジを挿さずに")]   # 本体内蔵の機能の箇条書きは含めない
    items = []
    for m in re.finditer(r"^\*\s*(.+?)(?:\s+-\s+(.*))?$", sec, re.M):
        raw = m.group(1)
        link = re.match(r"\[\[([^|\]]+)", raw)
        items.append({"title": plain(raw), "desc": plain(m.group(2) or ""),
                      "article": link.group(1).split("#")[0] if link and raw.startswith("[[") else ""})
    if [i["title"] for i in items] != list(WIKI_TO_MAME):
        sys.exit(f"ソフトウェア節の題名が想定と違います: {[i['title'] for i in items]}")

    soft = {s.get("name"): s for s in ET.parse(C.mame_xml("gamepock")).getroot().findall("software")}
    info = lambda s, k: next((i.get("value") for i in s.findall("info") if i.get("name") == k), "")
    rows, dumps = [], []
    for it in items:
        s = soft[WIKI_TO_MAME[it["title"]]]
        rows.append({"release_date": (s.findtext("year") or "").strip("?"), "title": it["title"], "publisher": "エポック社",
                     "cassette_no": info(s, "serial"), "model_number": "", "price_yen": "", "price_tax": "",
                     "notes": it["desc"].rstrip("。") if it["desc"] else "", "wikipedia_article": it["article"],
                     "release_date_sources": "MAME（年のみ）", "mame_name": s.get("name"), "_s": s})
    rows.sort(key=lambda r: (r["release_date"], int(r["cassette_no"] or 99)))
    for i, r in enumerate(rows, 1):
        r["id"] = f"gamepock-jp-{i:04d}"
        s = r.pop("_s")
        for x in s.iter("rom"):
            if x.get("crc"):
                dumps.append({"title_id": r["id"], "title": r["title"], "mame_name": s.get("name"),
                              "mame_description": s.findtext("description"), "rom_name": x.get("name"),
                              "size": str(int(x.get("size"), 16) if x.get("size", "").startswith("0x") else x.get("size")),
                              "crc32": x.get("crc"), "sha1": x.get("sha1"), "mame_status": s.get("supported", "yes"),
                              "hash_source": "MAME"})
    fields = ["id", "release_date", "title", "publisher", "cassette_no", "model_number", "price_yen", "price_tax", "notes",
              "wikipedia_article", "release_date_sources", "mame_name"]
    C.write_csv(DIR / "jp_titles.csv", rows, fields)
    C.write_csv(DIR / "jp_rom_dumps.csv", dumps)
    print(f"{len(rows)} 件 / 吸い出し {len(dumps)} 行", file=sys.stderr)


if __name__ == "__main__":
    main()
