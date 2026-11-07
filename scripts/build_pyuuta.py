#!/usr/bin/env python3
"""トミーのぴゅう太（1982年発売。後継機のぴゅう太Jr.・ぴゅう太mk2 を含む）のソフト一覧を作る。

出典:
  タイトル・番号・説明    ja.wikipedia「ぴゅう太」の「ソフトウェア」節（ROM の表 № 1〜26、TAPE の箇条書き 8 本）
  発売時期・価格          メディア芸術データベース。説明文に「[システム] ぴゅう太」とある商品には他機種の商品（PV-1000・PV-2000・ソード M5 など）が
                          混じっているので、題名でぴゅう太の作品と確かめた 8 件（MADB_IDS）だけ使う
  年・serial・ハッシュ    MAME `tutor`（年は MADB と食い違う例がある。serial〈001E など〉は型番かどうか分からない）
No-Intro（libretro）に DAT は無い。デモカートリッジ・未発売・米国版（TUTOR）は対象外。

出力: data/pyuuta/jp_titles.csv（ROM）、jp_tape.csv（TAPE）、jp_rom_dumps.csv
使い方: python3 scripts/build_pyuuta.py
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

import common as C

DIR = C.ROOT / "data" / "pyuuta"
PAGE = "ぴゅう太"
# 表の № → MAME のソフト名（serial に番号の無いもの・米国版と同じ項目のもの）
NO_TO_MAME = {10: "trafjam", 14: "pooyan", 15: "jungler", 16: "locomotn", 18: "tron"}
# MADB の商品（題名 → ID）。ぴゅう太の作品と確かめたものだけ
MADB_IDS = {"フロッガー": "M729769", "ザウルスランド": "M732186", "スクランブル": "M732198", "ターピン": "M733437",
            "ナイトフライト": "M731356", "バミューダトライアングル": "M728719", "ベースボール": "M728600",
            "算数教室/数の学校": "M732178"}


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
    want = set(MADB_IDS.values())
    out = {}
    with zipfile.ZipFile(C.CACHE / "madb_gm301.zip") as z:
        for f in z.namelist():
            for x in json.loads(z.read(f).decode("utf-8", "replace"), strict=False).get("@graph", []):
                if x.get("identifier") in want:
                    out[x["identifier"]] = x
    return out


def main():
    text = wiki_text()
    rom = text[text.index("=== ROM ==="):text.index("=== デモカートリッジ ===")]
    tape = text[text.index("=== TAPE ==="):text.index("== 発売後の評価 ==")]
    roms = []
    for cells in re.findall(r"^\|[ \t]*(\d+)[ \t]*\|\|[ \t]*(●?)[ \t]*\|\|[ \t]*(.+?)(?:[ \t]*\|\|[ \t]*(.*))?$", rom, re.M):
        no, mark, title, note = cells
        link = re.match(r"\[\[([^|\]]+)", title)
        roms.append({"no": int(no), "adapter": "yes" if mark else "", "title": plain(title), "desc": plain(note or ""),
                     "article": link.group(1).split("#")[0] if link else ""})
    if [r["no"] for r in roms] != list(range(1, 27)):
        sys.exit(f"ROM の表の番号が 1〜26 ではありません: {[r['no'] for r in roms]}")
    tapes = []
    for m in re.finditer(r"^\*\s*(?:(K-\d+)\s+)?(.+?)\s*$", tape, re.M):
        tapes.append({"tape_no": m.group(1) or "", "title": plain(m.group(2))})

    soft = {s.get("name"): s for s in ET.parse(C.mame_xml("tutor")).getroot().findall("software")}
    info = lambda s, k: next((i.get("value") for i in s.findall("info") if i.get("name") == k), "")
    by_no = {}
    for name, s in soft.items():
        m = re.search(r"\b0(\d\d)E\b", info(s, "serial"))
        if m:
            by_no.setdefault(int(m.group(1)), name)
    madb = madb_items()

    def madb_fields(title):
        x = madb.get(MADB_IDS.get(title, ""))
        if not x:
            return "", "", "", ""
        return x.get("datePublished") or "", re.sub(r"\D", "", x.get("price", "")), "MADB", x["identifier"]

    rows, dumps = [], []
    for r in roms:
        name = NO_TO_MAME.get(r["no"]) or by_no.get(r["no"])
        if not name:
            sys.exit(f"MAME に № {r['no']} がありません")
        s = soft[name]
        date, yen, src, mid = madb_fields(r["title"])
        notes = [r["desc"].rstrip("。")] if r["desc"] else []
        year = (s.findtext("year") or "").strip()
        if not date and re.fullmatch(r"\d{4}", year):
            date, src = year, "MAME（年のみ）"
        desc = s.findtext("description")
        if "Japan" not in desc:
            notes.append(f"MAME の項目は「{desc}」（日本版の吸い出しかどうかは記載が無い）")
        elif "USA" in desc or s.get("cloneof"):
            notes.append(f"MAME の項目は「{desc}」{'（米国版の別版）' if s.get('cloneof') else ''}")
        rows.append({"release_date": date, "title": r["title"], "publisher": "トミー", "cassette_no": r["no"],
                     "game_adapter": r["adapter"], "model_number": "", "mame_serial": info(s, "serial"),
                     "price_yen": yen, "price_tax": "税なし" if yen else "", "notes": "。".join(notes),
                     "wikipedia_article": r["article"], "release_date_sources": src,
                     "price_source": "MADB" if yen else "", "madb_id": mid, "mame_name": name})
    for i, r in enumerate(rows, 1):   # № の順（発売順とは限らない）
        r["id"] = f"pyuuta-jp-{i:04d}"
        s = soft[r["mame_name"]]
        for x in s.iter("rom"):
            if x.get("crc"):
                dumps.append({"title_id": r["id"], "title": r["title"], "mame_name": s.get("name"),
                              "mame_description": s.findtext("description"), "mame_serial": r["mame_serial"],
                              "rom_name": x.get("name"), "size": str(int(x.get("size"), 16)) if x.get("size", "").startswith("0x") else x.get("size"),
                              "crc32": x.get("crc"), "sha1": x.get("sha1"), "mame_status": s.get("supported", "yes"),
                              "hash_source": "MAME"})
    C.write_csv(DIR / "jp_titles.csv", rows,
                ["id", "release_date", "title", "publisher", "cassette_no", "game_adapter", "model_number", "mame_serial",
                 "price_yen", "price_tax", "notes", "wikipedia_article", "release_date_sources", "price_source", "madb_id", "mame_name"])
    C.write_csv(DIR / "jp_rom_dumps.csv", dumps)

    trows = []
    for i, t in enumerate(tapes, 1):
        date, yen, src, mid = madb_fields(t["title"])
        trows.append({"id": f"pyuuta-jp-tape-{i:04d}", "release_date": date, "title": t["title"], "publisher": "トミー",
                      "tape_no": t["tape_no"], "price_yen": yen, "price_tax": "税なし" if yen else "",
                      "release_date_sources": src, "price_source": "MADB" if yen else "", "madb_id": mid})
    C.write_csv(DIR / "jp_tape.csv", trows,
                ["id", "release_date", "title", "publisher", "tape_no", "price_yen", "price_tax", "release_date_sources", "price_source", "madb_id"])
    print(f"ROM {len(rows)} 件（発売時期 {sum(bool(r['release_date']) for r in rows)}・価格 {sum(bool(r['price_yen']) for r in rows)}）"
          f" / 吸い出し {len(dumps)} 行 / TAPE {len(trows)} 件", file=sys.stderr)


if __name__ == "__main__":
    main()
