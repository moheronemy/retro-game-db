#!/usr/bin/env python3
"""カシオ ルーピー（マイシールコンピューター ルーピー、1995年10月発売）のソフト一覧を作る。

出典: ja.wikipedia「ルーピー」の「ソフトウェア」節（定義リスト「; 題名」「: 著作権表記の年/型番/税抜価格」。11 本）。
ハッシュは No-Intro DAT（libretro 収録の Casio - Loopy。多くはバイト順の違う 2 件ずつ。`mame_match` は MAME の CRC との一致）、No-Intro に無い『マジカルショップ』は MAME `casloopy`。
MADB に機種が無く、MAME・No-Intro・4Gamer の記事（「ソフト数わずか11本」）とも本数が合う。

出力: data/loopy/jp_titles.csv、data/loopy/jp_rom_dumps.csv
使い方: python3 scripts/build_loopy.py
"""
import re
import sys
import xml.etree.ElementTree as ET

import common as C

DIR = C.ROOT / "data" / "loopy"
PAGE = "ルーピー"
LAUNCH_DATE = "1995-10"   # 本体の発売（記事の出典は『週刊ファミコン通信』1995年6月30日号）
DEVELOPERS = ("アルファ・システム", "アーマット", "アクシズアートアミューズ")


def wiki_text():
    cache = C.CACHE / "wikipedia" / f"{PAGE}.wiki"
    if not cache.exists():
        import fetch_wikipedia_list as F
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(F.fetch_wikitext(PAGE)[0], encoding="utf-8")
    return cache.read_text(encoding="utf-8")


def plain(s):
    s = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>", "", s)
    s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", s)
    return s.replace("&#x2665;", "♥").strip()


def parse():
    text = wiki_text()
    sec = text[text.index("== ソフトウェア =="):text.index("== 周辺機器 ==")]
    rows, launch = [], False
    for block in re.split(r"\n(?==== )", sec):
        head = re.match(r"=== (.+?) ===", block)
        if head:
            launch = "同時発売" in head.group(1)
        for m in re.finditer(r"^; (.+)\n((?::.*\n?)+)", block, re.M):
            title = plain(m.group(1))
            lines = [plain(l[1:]) for l in m.group(2).strip().split("\n")]
            meta = lines[0].split("/")
            year = re.match(r"(\d{4})年", meta[0]).group(1)
            model = meta[1].strip()
            price = meta[2].replace(",", "").replace("円", "").strip() if len(meta) > 2 else ""
            desc = " ".join(lines[1:])
            notes = []
            for pat in (r"マウス同梱版も発売", r"ルーピーセット[AB・]+に同梱された", r"シーラー同梱",
                        r"マウス(?:、マジカルショップに)?対応", r"マウス対応"):
                hit = re.search(pat, desc)
                if hit and hit.group(0) not in "。".join(notes):
                    notes.append(hit.group(0))
            dev = [d for d in DEVELOPERS if f"開発は{d}" in desc or f"開発は[[{d}" in desc or ("開発は" in desc and d in desc)]
            rows.append({
                "release_date": LAUNCH_DATE if launch else year,
                "release_date_text": ("本体と同時発売（1995年10月）。" if launch else "") + f"著作権表記の年 {year}年",
                "title": title, "publisher": "カシオ計算機", "developer": "・".join(dev),
                "model_number": model, "price_yen": price, "price_tax": "税抜" if price else "",
                "launch_title": "yes" if launch else "",
                "notes": "。".join(notes),
                "release_date_sources": "Wikipedia", "model_number_source": "Wikipedia",
                "price_source": "Wikipedia" if price else "",
                "sources": f"https://ja.wikipedia.org/wiki/{PAGE}",
            })
    return rows


def main():
    rows = parse()
    if len(rows) != 11:
        sys.exit(f"ソフトウェア節の本数が 11 ではありません: {len(rows)}")
    root = ET.parse(C.mame_xml("casloopy")).getroot()
    mame = {}
    for s in root.findall("software"):
        serial = next((i.get("value") for i in s.findall("info") if i.get("name") == "serial"), "")
        mame[serial] = s
    for r in rows:
        if r["model_number"] not in mame:
            sys.exit(f"MAME に型番がありません: {r['model_number']}")
    rows.sort(key=lambda r: (r["release_date"], r["model_number"]))
    for i, r in enumerate(rows, 1):
        r["id"] = f"loopy-jp-{i:04d}"
        r["mame_name"] = mame[r["model_number"]].get("name")
    fields = ["id", "release_date", "release_date_text", "title", "publisher", "developer", "model_number", "price_yen",
              "price_tax", "launch_title", "notes", "release_date_sources", "model_number_source", "price_source",
              "mame_name", "sources"]
    C.write_csv(DIR / "jp_titles.csv", rows, fields)

    # 吸い出し: No-Intro（題名は MAME の description の英字題と同じ） → 無ければ MAME
    dat = C.nointro_dat_text("Casio - Loopy")
    games = []
    for b in dat.split("game (")[1:]:
        n = re.search(r'name "([^"]+)"', b)
        rom = re.search(r"size (\d+) crc ([0-9A-F]+) md5 ([0-9A-F]+) sha1 ([0-9A-F]+)", b)
        if n and rom:
            games.append({"name": n.group(1), "size": rom.group(1), "crc": rom.group(2).lower(),
                          "md5": rom.group(3).lower(), "sha1": rom.group(4).lower()})
    dumps = []
    for r in rows:
        s = mame[r["model_number"]]
        mame_crcs = {x.get("crc") for x in s.iter("rom") if x.get("crc")}
        base = C.norm(re.sub(r"\s*\(.*", "", s.findtext("description")))
        hits = [g for g in games if C.sim(base, re.sub(r"\s*\(.*", "", g["name"])) >= 0.8 or g["crc"] in mame_crcs]
        names = {g["name"] for g in hits if g["crc"] in mame_crcs}
        hits = [g for g in games if g["name"] in names] if names else hits
        if hits:
            for g in hits:
                dumps.append({"title_id": r["id"], "title": r["title"], "game_code": r["model_number"],
                              "dump_name": g["name"], "rom_name": "", "size": g["size"], "crc32": g["crc"],
                              "md5": g["md5"], "sha1": g["sha1"],
                              "mame_match": ("一致" if g["crc"] in mame_crcs else
                                             "比較できない（MAME は ROM 2 個）" if len(mame_crcs) > 1 else "不一致"),
                              "mame_name": s.get("name"), "hash_source": "No-Intro"})
        else:
            for x in s.iter("rom"):
                if x.get("crc"):
                    dumps.append({"title_id": r["id"], "title": r["title"], "game_code": r["model_number"],
                                  "dump_name": s.findtext("description"), "rom_name": x.get("name"),
                                  "size": str(int(x.get("size"), 16)), "crc32": x.get("crc"), "md5": "",
                                  "sha1": x.get("sha1"), "mame_match": "", "mame_name": s.get("name"),
                                  "hash_source": "MAME"})
    C.write_csv(DIR / "jp_rom_dumps.csv", dumps)
    print(f"{len(rows)} 件 / 価格 {sum(bool(r['price_yen']) for r in rows)} / 吸い出し {len(dumps)} 行"
          f"（No-Intro {sum(d['hash_source'] == 'No-Intro' for d in dumps)}・MAME {sum(d['hash_source'] == 'MAME' for d in dumps)}）",
          file=sys.stderr)


if __name__ == "__main__":
    main()
