#!/usr/bin/env python3
"""ピピンアットマーク（1996年、バンダイ・デジタル・エンタテインメント／Apple）の日本のソフト一覧を作る。

MADB に機種が無く、Wikipedia の「対応ソフト」も一部（「ほか」）しか無いため、MAME のソフトウェアリスト `pippin` を骨格にして
Wikipedia の記載を合わせる。発売日は MAME の年だけ、価格は出典が無いので空欄。

  本リスト jp_titles.csv           製品版（型番 BDE-…〈バンダイ〉・BDS-…〈他社〉）＋ Wikipedia にだけあるもの
  jp_system_discs.csv              BDB-… の系列（Navigator CD・Network CD・TV Works・Internet Kit などの本体同梱・通信用ディスク）
  jp_rom_dumps.csv / jp_system_discs_rom_dumps.csv   MAME の CHD の sha1（別版〈alt・Ver.〉は行を分けて載せる）

載せないもの: 米国版・試作品・SDK、MUJ-…（『Mac Bin』。雑誌付録とみられるが出典で確認できない）、
PEASE…（MAKI Enterprise。販売経路が分からない）。

使い方: python3 scripts/build_pippin.py
"""
import re
import sys
import xml.etree.ElementTree as ET

import common as C

DIR = C.ROOT / "data" / "pippin"
WIKI_PAGE = "ピピンアットマーク"

# Wikipedia の「対応ソフト」の項目 → MAME のソフト名（None は MAME に無いもの）
WIKI_TO_MAME = {
    "たまごっち CD-ROM Pippin/Macintosh版": "tamagotc",
    "Racing Days for Pippin": "racingd",
    "GUNDAM VIRTUAL MODELER LIGHT": "gundamvm",
    "GUNDAM TACTICS MOBILITY FLEET0079": "gundtact",
    "GUNDAM 0079 THE WAR FOR EARTH": "gundamwe",
    "機動戦士ガンダム 第13独立部隊 ホワイトベース": "gundamwb",
    "SDガンダム外伝": "atcard",
    "ジオン軍ミリタリーファイル": "gundamzd",
    "SDガンダム ウォーズ": "sdgundam",
    "森高千里CD-ROM 渡良瀬橋": "chisatom",
    "EGWORD PURE for Pippin": "egwordp",
    "Tunin'Glue": "tunglue",
    "アニメデザイナードラゴンボールZ": "animedbz",
    "Victorian Park": "victorp",
    "AI将棋": "aishogi",
    "ごきげんママのおまかせダイアリー": None,
    "SeesawC1": "seesawc1",
    "LULU": None,
    "アンパンマンとあそぼう!1": "anpanas1",
    "アンパンマンとあそぼう!2": "anpanas2",
    "アンパンマンのあいうえお～ん": "anpanain",
    "ウルトラマン デジタルボードゲーム": "ultraman",
    "ウルトラマンクイズ王": "ultramaq",
}
# MAME の発売元（英字）→ 日本語の社名。社名が明らかなものだけ（ほかは MAME の表記のまま）
PUBLISHER_JA = {
    "Bandai": "バンダイ", "Voyager": "ボイジャー", "Amuse": "アミューズ", "Ask Kodansha": "アスク講談社",
    "Electronic Arts Victor": "エレクトロニック・アーツ・ビクター", "Synergy Ikunangaku": "シナジー幾何学",
    "Digitalogue": "デジタローグ", "Media Five": "メディアファイブ",
}


def wiki_items():
    cache = C.CACHE / "wikipedia" / f"{WIKI_PAGE}.wiki"
    if not cache.exists():
        import fetch_wikipedia_list as F
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(F.fetch_wikitext(WIKI_PAGE)[0], encoding="utf-8")
    text = cache.read_text(encoding="utf-8")
    sec = text[text.index("== 対応ソフト =="):text.index("== 脚注 ==")]
    items = []
    for line in sec.split("\n"):
        if not line.startswith("* "):
            continue
        body = line[2:]
        m = re.match(r"(.*?)（([^（）]*)）\s*$", body)
        title, genre = (m.group(1), m.group(2)) if m else (body, "")
        link = re.search(r"\[\[([^|\]]*)(?:\|[^\]]*)?\]\]", title)
        plain = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", title)
        plain = re.sub(r"\s+", " ", plain).strip()
        genre = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", genre)
        if genre == "キング":   # 『ウルトラマンクイズ王（キング）』の読み
            genre = ""
        article = link.group(1).strip() if link and title.strip().startswith("[[") else ""
        items.append({"title": plain, "genre": genre, "article": article})
    return items


def main():
    root = ET.parse(C.mame_xml("pippin")).getroot()
    soft = {s.get("name"): s for s in root.findall("software")}
    info = lambda s, k: next((i.get("value") for i in s.findall("info") if i.get("name") == k), "")
    year = lambda s: (s.findtext("year") or "").strip("?")

    wiki = {w["title"]: w for w in wiki_items()}
    unknown = set(wiki) - set(WIKI_TO_MAME)
    if unknown:
        sys.exit(f"WIKI_TO_MAME に無い Wikipedia の項目: {sorted(unknown)}")
    wiki_by_mame = {WIKI_TO_MAME[t]: w for t, w in wiki.items() if WIKI_TO_MAME[t]}

    titles, system = [], []
    for name, s in soft.items():
        desc = s.findtext("description")
        serial = info(s, "serial")
        if s.get("cloneof") or "(Japan" not in desc:
            continue
        base = re.sub(r"\s*\(Japan[^)]*\)", "", desc).replace("&amp;", "&")
        ver = re.search(r"\(Japan, (Ver\. [^)]+)\)", desc)
        pub = (s.findtext("publisher") or "").replace("<unknown>", "")
        row = {"mame_name": name, "serial": serial, "year": year(s), "publisher": PUBLISHER_JA.get(pub, pub),
               "alt": info(s, "alt_title").replace("　", " "), "base": base, "ver": ver.group(1) if ver else "",
               "release": info(s, "release")}
        if serial.startswith(("BDE-", "BDS-")):
            titles.append(row)
        elif serial.startswith("BDB-"):
            system.append(row)
        # MUJ-…（Mac Bin）・PEASE…・SDK は載せない

    out = []
    for r in titles:
        w = wiki_by_mame.get(r["mame_name"])
        title = r["alt"] or (w["title"] if w else r["base"])
        notes = []
        if not r["alt"] and not w:
            notes.append("日本語の題名が出典に無いので MAME の題名")
        if r["release"]:
            notes.append(f"MAME の発売日の記載は {r['release'][:4]}-{r['release'][4:6]}-{r['release'][6:8]}（「?」付き）")
        model = r["serial"].split(",")[0].strip()
        if "," in r["serial"]:
            notes.append(f"{r['serial'].count(',') + 1} 枚組（{r['serial']}）")
        out.append({"release_date": r["year"], "title": title, "publisher": r["publisher"],
                    "genre": w["genre"] if w else "", "model_number": model, "price_yen": "", "price_tax": "",
                    "notes": "。".join(notes), "wikipedia_article": w["article"] if w else "",
                    "release_date_sources": "MAME（年のみ）", "model_number_source": "MAME",
                    "title_source": "MAME" if r["alt"] or not w else "Wikipedia",
                    "in_wikipedia": "yes" if w else "", "mame_name": r["mame_name"]})
    for t, name in WIKI_TO_MAME.items():
        if name is None:
            w = wiki[t]
            out.append({"release_date": "", "title": t, "publisher": "", "genre": w["genre"], "model_number": "",
                        "price_yen": "", "price_tax": "", "notes": "Wikipedia にだけ記載（MAME に無い）。発売日・型番は出典に無い",
                        "wikipedia_article": w["article"], "release_date_sources": "", "model_number_source": "",
                        "title_source": "Wikipedia", "in_wikipedia": "yes", "mame_name": ""})
    # 並びは発売年 → 型番（発売日の分からないものは最後）
    out.sort(key=lambda r: (r["release_date"] or "9999", r["model_number"] or "~", r["title"]))
    for i, r in enumerate(out, 1):
        r["id"] = f"pippin-jp-{i:04d}"
    fields = ["id", "release_date", "title", "publisher", "genre", "model_number", "price_yen", "price_tax", "notes",
              "wikipedia_article", "release_date_sources", "model_number_source", "title_source", "in_wikipedia", "mame_name"]
    C.write_csv(DIR / "jp_titles.csv", out, fields)

    sysrows = []
    for r in sorted(system, key=lambda r: r["serial"]):
        title = r["base"] + (f"（{r['ver']}）" if r["ver"] else "")
        if r["alt"]:
            title = r["alt"] + (f"（{r['ver']}）" if r["ver"] else "")
        sysrows.append({"release_date": r["year"], "title": title, "publisher": r["publisher"],
                        "model_number": re.sub(r"\s*\(.*", "", r["serial"]), "mame_serial": r["serial"],
                        "release_date_sources": "MAME（年のみ）", "mame_name": r["mame_name"]})
    for i, r in enumerate(sysrows, 1):
        r["id"] = f"pippin-jp-sys-{i:04d}"
    C.write_csv(DIR / "jp_system_discs.csv", sysrows,
                ["id", "release_date", "title", "publisher", "model_number", "mame_serial", "release_date_sources", "mame_name"])

    def dumps(rows):
        res = []
        for r in rows:
            if not r["mame_name"]:
                continue
            parent = soft[r["mame_name"]]
            for s in [parent] + [x for x in soft.values() if x.get("cloneof") == r["mame_name"]]:
                for d in s.iter("disk"):
                    res.append({"title_id": r["id"], "title": r["title"], "mame_name": s.get("name"),
                                "mame_description": s.findtext("description"), "mame_serial": info(s, "serial"),
                                "disk_name": d.get("name"), "sha1": d.get("sha1"),
                                "mame_status": s.get("supported", "yes"), "hash_source": "MAME (CHD)"})
        return res
    d1, d2 = dumps(out), dumps(sysrows)
    C.write_csv(DIR / "jp_rom_dumps.csv", d1)
    C.write_csv(DIR / "jp_system_discs_rom_dumps.csv", d2)
    print(f"本リスト {len(out)} 件（MAME {sum(bool(r['mame_name']) for r in out)}・Wikipedia のみ "
          f"{sum(not r['mame_name'] for r in out)}）/ 吸い出し {len(d1)} 行；"
          f"本体同梱・通信用ディスク {len(sysrows)} 件 / 吸い出し {len(d2)} 行", file=sys.stderr)


if __name__ == "__main__":
    main()
