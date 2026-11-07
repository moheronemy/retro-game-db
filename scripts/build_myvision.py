#!/usr/bin/env python3
"""日本物産のマイビジョン（1983年発売。販売は中央産業・のち関東電子も）のソフト一覧を作る。

出典:
  タイトル・開発元・価格  ja.wikipedia「マイビジョン」の「ソフトウェア」節（6 本。「全ゲームソフト定価4,500円」。価格の出典は海外のサイト Video Game Kraken）
  年・ラベル・ハッシュ    MAME `myvision`（製品版 4 本。2022年以降の個人制作ソフトは対象外）
記事の会社名は本文の「ゲームソフトの開発は日本物産と…ロジテックが…担当」から開発元として developer に置く。
No-Intro（libretro）に DAT は無い。MADB の「[システム] マイビジョン」の商品は他機種のもので使わない。

出力: data/myvision/jp_titles.csv、data/myvision/jp_rom_dumps.csv
使い方: python3 scripts/build_myvision.py
"""
import re
import sys
import xml.etree.ElementTree as ET

import common as C

DIR = C.ROOT / "data" / "myvision"
PAGE = "マイビジョン"
WIKI_TO_MAME = {"マージャン": "mahjong", "連珠《五目ならべ》": "gomoku", "花合わせ《花札》": "hanafuda",
                "マスターマインド": None, "詰将棋": "tsumesho", "リバーシ": None}
COMPANY = {"日本物産": "日本物産", "ロジテック": "ロジテック"}


def wiki_text():
    cache = C.CACHE / "wikipedia" / f"{PAGE}.wiki"
    if not cache.exists():
        import fetch_wikipedia_list as F
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(F.fetch_wikitext(PAGE)[0], encoding="utf-8")
    return cache.read_text(encoding="utf-8")


def main():
    text = wiki_text()
    sec = text[text.index("== ソフトウェア =="):text.index("== 周辺機器 ==")]
    price = re.search(r"全ゲームソフト定価([\d,]+)円", sec)
    yen = price.group(1).replace(",", "") if price else ""
    items = []
    for m in re.finditer(r"^\*\s*(.+?)\s+-\s+(\S+)\s*$", sec, re.M):
        raw = m.group(1)
        link = re.match(r"\[\[([^|\]]+)", raw)
        title = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", raw).strip()
        items.append({"title": title, "developer": COMPANY.get(m.group(2), m.group(2)),
                      "article": link.group(1).split("#")[0].replace("_", " ") if link else ""})
    if [i["title"] for i in items] != list(WIKI_TO_MAME):
        sys.exit(f"ソフトウェア節の題名が想定と違います: {[i['title'] for i in items]}")

    soft = {s.get("name"): s for s in ET.parse(C.mame_xml("myvision")).getroot().findall("software")}
    info = lambda s, k: next((i.get("value") for i in s.findall("info") if i.get("name") == k), "")
    rows, dumps = [], []
    for i, it in enumerate(items, 1):
        name = WIKI_TO_MAME[it["title"]]
        s = soft[name] if name else None
        year = (s.findtext("year") or "").strip() if s is not None else ""
        r = {"id": f"myvision-jp-{i:04d}", "release_date": year if re.fullmatch(r"\d{4}", year) else "",
             "title": it["title"], "publisher": "", "developer": it["developer"], "model_number": "",
             "mame_label": re.sub(r"^CORTRIDGE\s+", "", info(s, "label")) if s is not None else "",
             "price_yen": yen, "price_tax": "税なし" if yen else "",
             "notes": "" if s is not None else "MAME に記録が無い（吸い出しなし）",
             "wikipedia_article": it["article"],
             "release_date_sources": "MAME（年のみ）" if s is not None and year else "",
             "price_source": "Wikipedia（全ゲームソフト定価）" if yen else "", "mame_name": name or ""}
        rows.append(r)
        if s is not None:
            for x in s.iter("rom"):
                if x.get("crc"):
                    dumps.append({"title_id": r["id"], "title": r["title"], "mame_name": name,
                                  "mame_description": s.findtext("description"), "rom_name": x.get("name"),
                                  "size": str(int(x.get("size"), 16)) if x.get("size", "").startswith("0x") else x.get("size"),
                                  "crc32": x.get("crc"), "sha1": x.get("sha1"), "mame_status": s.get("supported", "yes"),
                                  "hash_source": "MAME"})
    C.write_csv(DIR / "jp_titles.csv", rows,
                ["id", "release_date", "title", "publisher", "developer", "model_number", "mame_label", "price_yen", "price_tax",
                 "notes", "wikipedia_article", "release_date_sources", "price_source", "mame_name"])
    C.write_csv(DIR / "jp_rom_dumps.csv", dumps)
    print(f"{len(rows)} 件 / 吸い出し {len(dumps)} 行", file=sys.stderr)


if __name__ == "__main__":
    main()
