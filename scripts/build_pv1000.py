#!/usr/bin/env python3
"""カシオ PV-1000（1983年10月発売）のソフト一覧を作る。

出典:
  タイトル・型番・原作      ja.wikipedia「PV-1000」の「ソフトウェア」節（箇条書き「*GPA-101 [[プーヤン]] - 説明」。13 本、108・113 は欠番）
  発売日・価格              メディア芸術データベース（説明文に「[システム] PV-1000」とある商品。8 本。機種の欄は空）
  ハッシュ                  No-Intro DAT（libretro 収録の Casio - PV-1000。13 本）
MAME `pv1000` は型番の照合に使う（年は原作の年なので使わない。2022年以降の個人制作ソフトは対象外）。

出力: data/pv1000/jp_titles.csv、data/pv1000/jp_rom_dumps.csv、data/pv1000/review/match_report.csv
使い方: python3 scripts/build_pv1000.py
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

import common as C

DIR = C.ROOT / "data" / "pv1000"
PAGE = "PV-1000"
# 原作（Wikipedia の説明文に出てくる会社）
MAKERS = ("コナミ", "ナムコ", "ユニバーサル", "ジャレコ")


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


def madb_items():
    """説明文に「[システム] PV-1000」とある MADB の商品（機種の欄は空）。"""
    out = []
    with zipfile.ZipFile(C.CACHE / "madb_gm301.zip") as z:
        for f in z.namelist():
            for x in json.loads(z.read(f).decode("utf-8", "replace"), strict=False).get("@graph", []):
                if "[システム] PV-1000" in str(x.get("description", "")):
                    out.append(x)
    return out


def main():
    text = wiki_text()
    sec = text[text.index("== ソフトウェア =="):text.index("== 脚注 ==")]
    rows = []
    for m in re.finditer(r"^\*\s*(GPA-\d{3})\s+(.+?)(?:\s+-\s+(.*))?$", sec, re.M):
        model, title_raw, desc = m.group(1), m.group(2), plain(m.group(3) or "")
        title = plain(title_raw)
        if "欠番" in title:
            continue
        link = re.match(r"\[\[([^|\]]+)", title_raw)
        maker = next((k for k in MAKERS if f"{k}のアーケードゲーム" in desc), "")
        origin = (f"{maker}のアーケードゲームの移植" if maker else "カシオのオリジナル" if "カシオオリジナル" in desc else "")
        notes = []
        if "最後に発売" in desc:
            notes.append("記事に「最後に発売された」とある")
        rows.append({"model_number": model, "title": title, "wikipedia_article": link.group(1).split("#")[0].replace("_", " ") if link else "",
                     "original": origin, "notes": notes})
    if len(rows) != 13:
        sys.exit(f"ソフトウェア節の本数が 13 ではありません: {len(rows)}")

    madb = madb_items()
    issues = []
    for r in rows:
        md = max(madb, key=lambda x: C.sim(r["title"], x["label"]), default=None)
        if md is not None and C.sim(r["title"], md["label"]) < 0.8:
            md = None
        r["release_date"] = md["datePublished"] if md else ""
        r["price_yen"] = re.sub(r"\D", "", md.get("price", "")) if md else ""
        r["price_tax"] = "税なし" if r["price_yen"] else ""
        r["madb_id"] = md["identifier"] if md else ""
        if md and md.get("productID") != r["model_number"]:
            issues.append({"title": r["title"], "issues": f"型番不一致 Wikipedia・MAME={r['model_number']} MADB={md.get('productID')}",
                           "madb_id": md["identifier"], "madb_title": md["label"]})
            r["notes"].append(f"MADB の品番は {md.get('productID')}（誤記とみられる）")

    root = ET.parse(C.mame_xml("pv1000")).getroot()
    mame = {next((i.get("value") for i in s.findall("info") if i.get("name") == "serial"), ""): s for s in root.findall("software")}
    for r in rows:
        s = mame.get(r["model_number"])
        if s is None:
            sys.exit(f"MAME に型番がありません: {r['model_number']}")
        r["mame_name"] = s.get("name")
        r["_mame_desc"] = s.findtext("description")

    rows.sort(key=lambda r: r["model_number"])
    for i, r in enumerate(rows, 1):
        r.update({"id": f"pv1000-jp-{i:04d}", "publisher": "カシオ計算機", "notes": "。".join(r["notes"]),
                  "release_date_sources": "MADB" if r["release_date"] else "",
                  "model_number_source": "Wikipedia+MAME", "price_source": "MADB" if r["price_yen"] else ""})
    fields = ["id", "release_date", "title", "publisher", "model_number", "price_yen", "price_tax", "original", "notes",
              "wikipedia_article", "release_date_sources", "model_number_source", "price_source", "madb_id", "mame_name"]
    C.write_csv(DIR / "jp_titles.csv", rows, fields)

    games = []
    for b in C.nointro_dat_text("Casio - PV-1000").split("game (")[1:]:
        n = re.search(r'name "([^"]+)"', b)
        rom = re.search(r"size (\d+) crc ([0-9A-F]+) md5 ([0-9A-F]+) sha1 ([0-9A-F]+)", b)
        if n and rom:
            games.append({"name": n.group(1), "size": rom.group(1), "crc": rom.group(2).lower(),
                          "md5": rom.group(3).lower(), "sha1": rom.group(4).lower()})
    dumps, used = [], set()
    for r in rows:
        base = re.sub(r"\s*\(.*", "", r["_mame_desc"]).replace("&amp;", "&")
        g = max(games, key=lambda g: C.sim(base, re.sub(r"\s*\(.*", "", g["name"])))
        if C.sim(base, re.sub(r"\s*\(.*", "", g["name"])) < 0.8 or g["name"] in used:
            sys.exit(f"No-Intro に対応が見つかりません: {r['title']} / {base}")
        used.add(g["name"])
        dumps.append({"title_id": r["id"], "title": r["title"], "game_code": r["model_number"], "dump_name": g["name"],
                      "size": g["size"], "crc32": g["crc"], "md5": g["md5"], "sha1": g["sha1"], "hash_source": "No-Intro"})
    C.write_csv(DIR / "jp_rom_dumps.csv", dumps)
    C.write_csv(DIR / "review" / "match_report.csv", issues, ["title", "issues", "madb_id", "madb_title"])
    print(f"{len(rows)} 件 / 発売日 {sum(bool(r['release_date']) for r in rows)} / 価格 {sum(bool(r['price_yen']) for r in rows)}"
          f" / 吸い出し {len(dumps)} 行 / 要確認 {len(issues)}", file=sys.stderr)


if __name__ == "__main__":
    main()
