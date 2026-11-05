#!/usr/bin/env python3
"""GBA国内タイトルごとの ROM 吸い出し（ハッシュ・リビジョン）一覧を作る。

入力:
  data/gba/jp_titles.csv                     タイトル一覧（型番 = ゲームコードで照合する）
  No-Intro DB Export（GBA）                  ハッシュ・リビジョン・吸い出し情報（主たる出典）
      DAT-o-MATIC (https://datomatic.no-intro.org/) の Download → "Nintendo - Game Boy Advance"
      → op=db の "Prepare" → "Download!!" で得られる zip。利用規約への同意が必要なため自動取得はしない。
      .cache/nointro-db/ に置くか、--export で zip / xml のパスを渡す。
  No-Intro DAT（libretro-database 収録）     ゲームコードの補完（DB Export はシリアル移行中で欠けがあるため）
  MAME ソフトウェアリスト hash/gba.xml        同じ CRC の MAME エントリと baddump 表記
  data/gba/overrides/dump_matches.csv         自動で結びつかない吸い出しの手動対応

  data/gba/jp_not_for_sale.csv               非売品の本リスト（手で管理。nointro_name / mame_name で吸い出しに結びつける）
  data/gba/overrides/non_retail_parents.csv  体験版・試作品の対応する製品版（ゲームコードで決まらないもの）

出力:
  data/gba/jp_rom_dumps.csv                  1吸い出し = 1行（製品版・非売品・体験版・試作品）
  data/gba/jp_non_retail.csv                 店頭体験版・試作品・開発版の別リスト（No-Intro から生成）

使い方:
  python3 scripts/build_gba_dumps.py [--export PATH]
"""
import argparse
import csv
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enrich_gba as E  # noqa: E402  (fetch / キャッシュ / URL を共有)

DATA = E.DATA

# 別の製品として扱うもの（試作・体験版・販促品・非公式など）。非売品は別途まとめる
EXCLUDE = re.compile(r"^(Proto|Proto \d+|Beta|Beta \d+|Demo|Sample|Kiosk|Promo|Pirate|Unl|Aftermarket|Debug"
                     r"|Tech Demo|SDK.*|Hot Mario Campaign|Rewritable Cartridge|DS Expansion Cartridge)$")
VIRTUAL_CONSOLE = re.compile(r"Virtual Console|Switch Online")
COLLECTION = re.compile(r"Collection$|^Pokemon Box$")
VERIFICATION = [("Trusted Dump", "trusted_dump"), ("Trusted Modification", "trusted_modification"),
                ("Third Party", "third_party")]


def load_export(path):
    if path is None:
        found = sorted((E.CACHE / "nointro-db").glob("*GBA*") or []) + \
            sorted((E.CACHE / "nointro-db").glob("*Game Boy Advance*"))
        if not found:
            sys.exit("No-Intro DB Export が見つかりません。.cache/nointro-db/ に置くか --export で指定してください")
        path = found[-1]
    path = Path(path)
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as z:
            text = z.read(z.namelist()[0]).decode("utf-8")
    else:
        text = path.read_text(encoding="utf-8")
    version = re.search(r"<version>([^<]+)</version>", text)
    # <header> と <datafile> の2つのルート要素が並んでいるので包んで読む
    root = ET.fromstring("<root>" + text.split("?>", 1)[1] + "</root>")
    return root, version.group(1) if version else ""


def load_nointro_dat():
    """libretro 版 DAT: 名前 → (ゲームコード, サイズ, CRC, MD5, SHA1)。"""
    text = E.fetch(E.NOINTRO_URL, E.CACHE / "nointro_gba.dat").read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r'game \(\n(.*?)\n\)\n', text, re.S):
        b = m.group(1)
        name = re.search(r'name "([^"]+)"', b).group(1)
        rom = re.search(r'rom \( (.*?) \)', b).group(1)
        g = lambda k: (re.search(k + r' "?([^" ]+)"?', rom) or [None, ""])[1]
        out[name] = dict(serial=g("serial"), size=g("size"), crc=g("crc").lower(),
                         md5=g("md5").lower(), sha1=g("sha1").lower())
    return out


def load_mame_crcs():
    path = E.fetch(E.MAME_URL, E.CACHE / "mame_gba.xml")
    out = {}
    for s in ET.parse(path).getroot().findall("software"):
        for rom in s.iter("rom"):
            if rom.get("crc"):
                out.setdefault(rom.get("crc").lower(), []).append((s.get("name"), rom.get("status") or "good"))
    return out


def dump_kind(tags):
    if any(VIRTUAL_CONSOLE.search(t) for t in tags):
        return "virtual_console"
    if any(COLLECTION.search(t) for t in tags):
        return "collection"
    return "retail"


def non_retail_category(name, tags):
    """別リスト（A2〜A4）の区分。対象外は None。

    - store_demo: No-Intro が店頭試遊用（Kiosk）と記録したもの。配布経路の記録がない体験版は含めない
    - beta / prototype / tech_demo: 開発中の版・試作品・開発キット付属の技術デモ
    非公式品（Unl / Pirate / Aftermarket）、販促品（Promo。非売品の本リストで扱う）は対象外。
    """
    if any(re.match(r"^(Unl|Pirate|Aftermarket)$", t) for t in tags):
        return None
    if any(t.startswith("Kiosk") for t in tags):
        return "store_demo"
    if any(re.fullmatch(r"Beta( \d+)?", t) for t in tags):
        return "beta"
    if any(re.fullmatch(r"Proto( \d+)?", t) for t in tags):
        return "prototype"
    if "Tech Demo" in tags:
        return "tech_demo"
    return None


def tags_of(name):
    return [t for grp in re.findall(r"\(([^)]*)\)", name) for t in grp.split(", ")]


def game_codes(g, ref):
    files = [f for s in g.findall("source") for f in s.findall("file")]
    codes = {f.get("serial") for f in files if f.get("serial")}
    if ref and ref["serial"]:
        codes.add(ref["serial"])
    # 日米共通カートリッジはROM内のコード末尾が A（例: B85A）。パッケージ型番は J（AGB-B85J-JPN）
    codes = {c[:3] + "J" if c.endswith("A") else c for c in codes}
    return {c for c in codes if re.fullmatch(r"[A-Z0-9]{3}J", c)}


def dump_info(g, ref, mame):
    """No-Intro の1エントリから、吸い出し一覧の1行分（タイトル列以外）を作る。"""
    arch = g.find("archive")
    name = g.get("name")
    tags = tags_of(name)
    sources = g.findall("source")
    files = [s.find("file") for s in sources if s.find("file") is not None]
    # 代表ハッシュ: libretro DAT（= No-Intro の現行 DAT）と同じ CRC のファイル
    main_file = None
    if ref:
        main_file = next((f for f in files if (f.get("crc32") or "").lower() == ref["crc"]), None)
    if main_file is None and files:
        main_file = files[0]
    if main_file is not None:
        h = dict(size=main_file.get("size"), crc=main_file.get("crc32"), md5=main_file.get("md5"),
                 sha1=main_file.get("sha1"), sha256=main_file.get("sha256") or "")
    elif ref:
        h = dict(size=ref["size"], crc=ref["crc"], md5=ref["md5"], sha1=ref["sha1"], sha256="")
    else:
        return None
    sections = {s.find("details").get("section") for s in sources if s.find("details") is not None}
    serials = [s.find("serials") for s in sources if s.find("serials") is not None]
    pick = lambda *keys: ";".join(sorted({se.get(k) for se in serials for k in keys if se.get(k)}))
    dates = sorted(s.find("details").get("d_date") for s in sources
                   if s.find("details") is not None and s.find("details").get("d_date"))
    rev = next((m.group(1) for t in tags for m in [re.fullmatch(r"Rev (\d+)", t)] if m), None)
    ver = next((t for t in tags if re.fullmatch(r"v\d+(\.\d+)*", t)), None)
    save = re.search(r'"Save Type":"([^"]*)"', arch.get("details") or "")
    mm = mame.get((h["crc"] or "").lower(), [])
    return {
        "dump_name": name, "revision": rev or ver or "0",
        "size": h["size"], "crc32": (h["crc"] or "").lower(), "md5": (h["md5"] or "").lower(),
        "sha1": (h["sha1"] or "").lower(), "sha256": (h["sha256"] or "").lower(),
        "verification": next((v for k, v in VERIFICATION if k in sections), "undocumented"),
        "source_count": len(sources), "first_dump_date": dates[0] if dates else "",
        "rom_chip": pick("romchip_serial1", "romchip_serial2", "chip_serial", "chip_serial1", "chip_serial2"),
        "label_serial": pick("media_serial1", "media_serial2"), "pcb": pick("pcb_serial"),
        "save_type": save.group(1) if save else "", "nointro_number": arch.get("number"),
        "mame_name": ";".join(n for n, _ in mm), "mame_status": ";".join(st for _, st in mm),
        "hash_source": "No-Intro",
    }


def mame_dump(mame_xml_root, mame_name):
    """No-Intro に無いものを MAME ソフトウェアリストから作る（MD5・SHA256 は無い）。"""
    s = next((x for x in mame_xml_root.findall("software") if x.get("name") == mame_name), None)
    if s is None:
        return None
    rom = next(s.iter("rom"))
    return {
        "dump_name": rom.get("name"), "revision": "0", "size": rom.get("size"),
        "crc32": rom.get("crc"), "md5": "", "sha1": rom.get("sha1"), "sha256": "",
        "verification": "mame_only", "source_count": "", "first_dump_date": "", "rom_chip": "",
        "label_serial": "", "pcb": "", "save_type": "", "nointro_number": "",
        "mame_name": mame_name, "mame_status": rom.get("status") or "good", "hash_source": "MAME",
    }


def write_csv(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", help="No-Intro DB Export の zip / xml")
    a = ap.parse_args()

    titles = E.read_csv(DATA / "jp_titles.csv")
    title_by_id = {t["id"]: t for t in titles}
    by_code = {}
    for t in titles:
        if t["model_number"]:
            by_code.setdefault(t["model_number"][4:8], []).append(t)
    root, version = load_export(a.export)
    games = {g.get("name"): g for g in root.iter("game")}
    dat = load_nointro_dat()
    mame = load_mame_crcs()
    mame_root = ET.parse(E.CACHE / "mame_gba.xml").getroot()
    # 自動で結びつかない吸い出しの手動対応（dump_name → title_id）
    manual = {m["dump_name"]: m["title_id"] for m in E.read_csv(DATA / "overrides" / "dump_matches.csv")}
    nr_parents = {m["nointro_name"]: m["parent_id"]
                  for m in E.read_csv(DATA / "overrides" / "non_retail_parents.csv")}

    rows, non_retail, pending = [], [], []
    for name, g in games.items():
        arch = g.find("archive")
        if "Japan" not in (arch.get("region") or ""):
            continue
        tags = tags_of(name)
        ref = dat.get(name)
        codes = game_codes(g, ref)

        # ---- 別リスト（A2〜A4）。対応する製品版は製品版の処理後に決める
        cat = non_retail_category(name, tags)
        if cat:
            pending.append((name, g, ref, codes, cat))
            continue

        # ---- 製品版（jp_titles.csv）
        if any(EXCLUDE.match(t) for t in tags) or "Taikenban" in name:
            continue
        targets = [t for c in sorted(codes) for t in by_code.get(c, [])]
        if not targets and ref:
            # コードがどこにも無い場合は、同じ CRC を持つ MAME エントリ経由でタイトルに結びつける
            names = {n for n, _ in mame.get(ref["crc"], [])}
            targets = [t for t in titles if t["mame_name"] and t["mame_name"] in names]
            codes = {t["model_number"][4:8] for t in targets}
        if not targets and name in manual:
            targets = [title_by_id[manual[name]]]
            codes = {t["model_number"][4:8] for t in targets}
        info = dump_info(g, ref, mame) if targets else None
        for t in targets if info else []:
            rows.append({"title_id": t["id"], "title": t["title"], "game_code": "/".join(sorted(codes)),
                         "dump_kind": dump_kind(tags), **info})

    # ---- 別リスト（A2〜A4）
    # 開発版・試作品はゲームコードを別作品と共有していることがある（例: 烈火の剣の開発版が封印の剣のコード）ため、
    # コードではなく No-Intro 名の本体（括弧より前）が製品版の吸い出し名と一致するもので対応づける
    base = lambda n: n.split(" (")[0]
    retail_by_base = {}
    for r in rows:
        if r["dump_kind"] == "retail":
            retail_by_base.setdefault(base(r["dump_name"]), set()).add(r["title_id"])
    labels = {"store_demo": "店頭体験版", "beta": "開発版", "prototype": "試作品", "tech_demo": "技術デモ"}
    for name, g, ref, codes, cat in pending:
        parent = nr_parents.get(name)
        if parent is None:
            cands = retail_by_base.get(base(name), set())
            parent = next(iter(cands)) if len(cands) == 1 else ""
        info = dump_info(g, ref, mame)
        nr_id = f"gba-jp-nr-{g.find('archive').get('number')}"
        title = f"{title_by_id[parent]['title']}（{labels[cat]}）" if parent else name
        non_retail.append({
            "id": nr_id, "title": title, "category": cat,
            "media": "gc_download" if any("GameCube" in t for t in tags_of(name)) else "cartridge",
            "parent_id": parent, "game_code": "/".join(sorted(codes)), "nointro_name": name,
            "evidence": "No-Intro: " + ", ".join(t for t in tags_of(name)
                                                 if re.match(r"Demo|Kiosk|GameCube|Beta|Proto|Debug|Tech Demo|SDK", t)),
            "verification": info["verification"] if info else "",
        })
        if info:
            rows.append({"title_id": nr_id, "title": title, "game_code": "/".join(sorted(codes)),
                         "dump_kind": cat, **info})

    # ---- 非売品の本リスト（A1）
    for n in E.read_csv(DATA / "jp_not_for_sale.csv"):
        info = None
        if n["nointro_name"]:
            g = games.get(n["nointro_name"])
            if g is None:
                sys.exit(f"jp_not_for_sale.csv の nointro_name が No-Intro に見つかりません: {n['nointro_name']}")
            info = dump_info(g, dat.get(n["nointro_name"]), mame)
        elif n["mame_name"]:
            info = mame_dump(mame_root, n["mame_name"])
        if info:
            rows.append({"title_id": n["id"], "title": n["title"], "game_code": n["model_number"][4:8],
                         "dump_kind": "not_for_sale", **info})

    kind_order = {"retail": 0, "collection": 1, "virtual_console": 2, "not_for_sale": 3,
                  "store_demo": 4, "beta": 5, "prototype": 6, "tech_demo": 7}
    rows.sort(key=lambda r: (r["title_id"], kind_order[r["dump_kind"]], r["revision"], r["dump_name"]))
    cols = ["title_id", "title", "game_code", "dump_name", "revision", "dump_kind"]
    rows = [{**{c: r[c] for c in cols}, **{k: v for k, v in r.items() if k not in cols}} for r in rows]
    write_csv(DATA / "jp_rom_dumps.csv", rows)
    non_retail.sort(key=lambda r: (["store_demo", "beta", "prototype", "tech_demo"].index(r["category"]),
                                   r["parent_id"] or "~", r["nointro_name"]))
    write_csv(DATA / "jp_non_retail.csv", non_retail)

    covered = {r["title_id"] for r in rows if r["dump_kind"] == "retail"}
    print(f"No-Intro DB Export {version}: 吸い出し {len(rows)} 行 / 製品版の吸い出しがあるタイトル "
          f"{len(covered)}/{len(titles)} / 別リスト {len(non_retail)} 件", file=sys.stderr)


if __name__ == "__main__":
    main()
