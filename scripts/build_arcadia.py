#!/usr/bin/env python3
"""バンダイのアルカディア（1983年3月25日発売。米国 Emerson の Arcadia 2001 と同じ仕様）のソフト一覧を作る。

出典: ja.wikipedia「アルカディア (ゲーム機)」の「アルカディア (バンダイ)」節。本文に「全19本がバンダイから発売」とあり、
      「発売されたタイトル」に輸入ソフト 15 本・キャラクターソフト 4 本の箇条書き。
      - 輸入ソフト 15 本は本体と同時発売（本文） → 発売日 1983-03-25。価格は本文に幅（2,980〜4,800 円）しか無いので空欄
      - キャラクターソフト 4 本は『月刊コロコロコミック』1983年10月号の時点で 2 本が発売済み・2 本が 1983年9月発売予定（本文）
        → 発売年 1983（元の記述は release_date_text）。価格は 3,800 円（本文）
ハッシュは MAME `arcadia` の日本版（キャラクターソフトの 4 本だけ。輸入ソフトは Emerson 版しか無いので載せない）。
MADB の「[システム] アルカディア」の商品は他機種（クリエイトビジョン版など）なので使わない。

出力: data/arcadia/jp_titles.csv、data/arcadia/jp_rom_dumps.csv
使い方: python3 scripts/build_arcadia.py
"""
import re
import sys
import xml.etree.ElementTree as ET

import common as C

DIR = C.ROOT / "data" / "arcadia"
PAGE = "アルカディア (ゲーム機)"
LAUNCH = "1983-03-25"
CHARACTER_TEXT = {
    "機動戦士ガンダム": "『月刊コロコロコミック』1983年10月号の時点で発売済み",
    "ドラえもん": "『月刊コロコロコミック』1983年10月号の時点で発売済み",
    "超時空要塞マクロス": "『月刊コロコロコミック』1983年10月号に1983年9月発売予定とある",
    "Dr.スランプ アラレちゃん": "『月刊コロコロコミック』1983年10月号に1983年9月発売予定とある",
}
CHARACTER_MAME = {"機動戦士ガンダム": "gundam", "超時空要塞マクロス": "macross",
                  "Dr.スランプ アラレちゃん": "drslump", "ドラえもん": "doraemon"}


def wiki_text():
    cache = C.CACHE / "wikipedia" / f"{PAGE}.wiki"
    if not cache.exists():
        import fetch_wikipedia_list as F
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(F.fetch_wikitext(PAGE)[0], encoding="utf-8")
    return cache.read_text(encoding="utf-8")


def items(block):
    out = []
    for m in re.finditer(r"^\*\s*(.+?)\s*$", block, re.M):
        raw = m.group(1)
        link = re.match(r"\[\[([^|\]]+)", raw)
        title = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", raw).strip()
        out.append({"title": title, "article": link.group(1).split("#")[0] if link else ""})
    return out


def main():
    text = wiki_text()
    sec = text[text.index("=== 発売されたタイトル ==="):text.index("== Arcadia 2001")]
    imports = items(sec[sec.index("==== 輸入ソフト"):sec.index("==== キャラクターソフト")])
    chars = items(sec[sec.index("==== キャラクターソフト"):])
    if len(imports) != 15 or [c["title"] for c in chars] != list(CHARACTER_MAME):
        sys.exit(f"一覧が想定と違います: 輸入 {len(imports)} 本 / キャラクター {[c['title'] for c in chars]}")

    soft = {s.get("name"): s for s in ET.parse(C.mame_xml("arcadia")).getroot().findall("software")}
    rows, dumps = [], []
    for it in imports:
        rows.append({"release_date": LAUNCH, "release_date_text": "本体と同時発売（本文）", "title": it["title"],
                     "publisher": "バンダイ", "category": "import", "model_number": "", "price_yen": "", "price_tax": "",
                     "notes": "輸入ソフト。価格は本文に 2,980〜4,800 円とあるだけ。日本版の吸い出しの記録が無い",
                     "wikipedia_article": it["article"], "release_date_sources": "Wikipedia", "mame_name": ""})
    for it in chars:
        rows.append({"release_date": "1983", "release_date_text": CHARACTER_TEXT[it["title"]], "title": it["title"],
                     "publisher": "バンダイ", "category": "character", "model_number": "", "price_yen": "3800",
                     "price_tax": "税なし", "notes": "キャラクターソフト（バンダイと科学技研の共同開発）",
                     "wikipedia_article": it["article"], "release_date_sources": "Wikipedia",
                     "mame_name": CHARACTER_MAME[it["title"]]})
    for i, r in enumerate(rows, 1):
        r["id"] = f"arcadia-jp-{i:04d}"
        if r["mame_name"]:
            s = soft[r["mame_name"]]
            for x in s.iter("rom"):
                if x.get("crc"):
                    dumps.append({"title_id": r["id"], "title": r["title"], "mame_name": s.get("name"),
                                  "mame_description": s.findtext("description"), "rom_name": x.get("name"),
                                  "size": str(int(x.get("size"), 16)) if x.get("size", "").startswith("0x") else x.get("size"),
                                  "crc32": x.get("crc"), "sha1": x.get("sha1"), "mame_status": s.get("supported", "yes"),
                                  "hash_source": "MAME"})
    C.write_csv(DIR / "jp_titles.csv", rows,
                ["id", "release_date", "release_date_text", "title", "publisher", "category", "model_number", "price_yen",
                 "price_tax", "notes", "wikipedia_article", "release_date_sources", "mame_name"])
    C.write_csv(DIR / "jp_rom_dumps.csv", dumps)
    print(f"{len(rows)} 件（輸入 {len(imports)}・キャラクター {len(chars)}）/ 吸い出し {len(dumps)} 行", file=sys.stderr)


if __name__ == "__main__":
    main()
