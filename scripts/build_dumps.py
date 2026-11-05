#!/usr/bin/env python3
"""国内タイトルごとの ROM 吸い出し（ハッシュ・リビジョン）一覧と、体験版・試作品の別リストを作る。

入力:
  <dir>/jp_titles.csv                     タイトル一覧（型番 = ゲームコードで照合する）
  No-Intro DB Export                  ハッシュ・リビジョン・吸い出し情報（主たる出典）
      DAT-o-MATIC (https://datomatic.no-intro.org/) の Download → "Nintendo - Game Boy Advance"
      → op=db の "Prepare" → "Download!!" で得られる zip。利用規約への同意が必要なため自動取得はしない。
      .cache/nointro-db/ に置くか、--export で zip / xml のパスを渡す。
  No-Intro DAT（libretro-database 収録）     ゲームコードの補完（DB Export はシリアル移行中で欠けがあるため）
  MAME ソフトウェアリスト                   同じ CRC の MAME エントリと baddump 表記
  <dir>/overrides/dump_matches.csv         自動で結びつかない吸い出しの手動対応

  <dir>/jp_not_for_sale.csv               非売品の本リスト（手で管理。nointro_name / mame_name で吸い出しに結びつける）
  <dir>/overrides/non_retail_parents.csv  体験版・試作品の対応する製品版（ゲームコードで決まらないもの）

出力:
  <dir>/jp_rom_dumps.csv                  1吸い出し = 1行（製品版・非売品・体験版・試作品）
  <dir>/jp_non_retail.csv                 店頭体験版・試作品・開発版の別リスト（No-Intro から生成）

使い方:
  python3 scripts/build_dumps.py gba [--export PATH]
"""
import argparse
import csv
import hashlib
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402
import platforms as P  # noqa: E402

# 別の製品として扱うもの（試作・体験版・販促品・非公式など）。非売品は別途まとめる
EXCLUDE = re.compile(r"^(Proto|Proto \d+|Beta|Beta \d+|Demo|Sample|Kiosk|Promo|Pirate|Unl|Aftermarket|Debug"
                     r"|Tech Demo|SDK.*|Hot Mario Campaign|Rewritable Cartridge|DS Expansion Cartridge"
                     r"|Possible Proto|Test Program|Special Version( \d+)?|NP"
                     r"|Club Nintendo|Not for Resale|Multiplayer|Save Data|Nintendo Game Seminar.*|DS Broadcast"
                     r"|Taikenban|Tentou Taikenban|Jitsuen-you Sample|Special Taiken Disc|Movie Demo Disc|Demo Eizou"
                     r"|Club Nintendo Genteiban|Auto Demo|Enhancement Chip"
                     # FC: ファミコンボックス（ホテル等の業務用）、ファミリーベーシックのプログラム、景品・業務用ディスク、
                     # 非公式品（Hacker）、後年の書籍付録・配信版など
                     r"|FamicomBox|Family BASIC|Menu Cart|EPROM|Digital|Disc|Sansai Mook|Ending Credits Program"
                     r"|Not For Resale|Shouhin Golf Tournament US Course|Hacker|SA-0\d+( \d+)? PCB"
                     r"|Prize Card|Developer Card|National Tax Agency Demo|Lock-On|Hibaihin|Demo \d+|Java Tea Original)$")
VIRTUAL_CONSOLE = re.compile(r"Virtual Console|Switch Online")
COLLECTION = re.compile(r"Collection$|^Pokemon Box$|^GameCube$|^Capcom Town$|^Columbus Circle$"
                        r"|^Animal Crossing$|^Retro-Bit Generations$|^Toaplan Arcade Garage$|^Steam$|^PS5$|^Switch$"
                        r"|^XBOX$|^Classic Mini$|^Namco Anthology \d$|^Project EGG$|^Collector's Edition$"
                        r"|^Game & Watch - Super Mario Bros\.$|^Evercade$|^Retro-Bit$|^Disney Classic Games$"
                        r"|^(Mega Drive|Genesis) Mini( 2)?$|^Game no Kanzume.*|^Sega Ages$|^Mega 6$|^PC Engine Mini$|^Satakore$"
                        r"|^PlayStation the Best.*|^PSone Books$|^Major Wave$|^Artdink Best Choice$|^Honkakuha de 1300$"
                        r"|^GameVillage The Best$|^Culture Publishers$|^Fukyuuban$")
# GameCube: GC 用ソフトに収録された ROM（N64）
ONLINE = re.compile(r"^(Sega Game Toshokan|Sega Channel)$")   # MD の通信配信版（ゲーム図書館・セガチャンネル）
VERIFICATION = [("Trusted Dump", "trusted_dump"), ("Trusted Modification", "trusted_modification"),
                ("Third Party", "third_party"), ("DAT", "dat_only")]


def dump_kind(tags):
    if any(ONLINE.match(t) for t in tags):
        return "online"
    if any(VIRTUAL_CONSOLE.search(t) for t in tags):
        return "virtual_console"
    if any(COLLECTION.search(t) for t in tags):
        return "collection"
    return "retail"


def non_retail_category(name, tags):
    """別リスト（A2〜A4）の区分。対象外は None。

    - store_demo: No-Intro が店頭試遊用（Kiosk）と記録したもの。配布経路の記録がない体験版は含めない
    - event_demo: 展示会（Spaceworld など）用と記録された体験版
    - beta / prototype / tech_demo: 開発中の版・試作品・開発キット付属の技術デモ
    非公式品（Unl / Pirate / Aftermarket）、販促品（Promo。非売品の本リストで扱う）は対象外。
    """
    if any(re.match(r"^(Unl|Pirate|Aftermarket)$", t) for t in tags):
        return None
    if any(t.startswith("Kiosk") for t in tags) or "DS Broadcast" in tags:
        return "store_demo"   # DS Broadcast は店頭の DS ステーションで配信された体験版
    if {"Jitsuen-you Sample", "Tentou Taikenban"} & set(tags) or name.startswith("Gekkan Nintendo Tentou Demo"):
        return "store_demo"   # GC の店頭実演用サンプル・店頭体験版・月刊任天堂店頭デモ
    if "Demo" in tags and any(t.startswith("Spaceworld") for t in tags):
        return "event_demo"   # 任天堂スペースワールド等の展示会用
    if any(re.fullmatch(r"Beta( \d+)?", t) for t in tags):
        return "beta"
    if any(re.fullmatch(r"Proto( \d+)?", t) for t in tags):
        return "prototype"
    if "Tech Demo" in tags:
        return "tech_demo"
    return None


def japanese_title(name):
    """対応する製品版が無い別リストの行の表示名。月刊任天堂店頭デモは日本語にする。"""
    m = re.match(r"Gekkan Nintendo Tentou Demo (\d{4})\.(\d{1,2})\.(\d{1,2})( Zoukangou)?", name)
    if m:
        return f"月刊任天堂店頭デモ {m.group(1)}年{int(m.group(2))}月{int(m.group(3))}日号" + ("（増刊号）" if m.group(4) else "")
    m = re.match(r"Gekkan Nintendo Tentou Demo (\d{4})-(\d{4}) Nenmatsunenshigou", name)
    if m:
        return f"月刊任天堂店頭デモ {m.group(1)}-{m.group(2)} 年末年始号"
    return name


def merge_discs(rows):
    """複数枚組（No-Intro / Redump 名の '(Disc 1)' '(Disc A)' など）を1行にまとめる。
    サイズ・ハッシュ・確認区分などはディスク順に ';' でつなぎ、discs 列に枚数を入れる。"""
    disc_re = re.compile(r" \(Dis[ck] [0-9A-Z]+\)")
    # 組の判定では、ディスクごとの呼び名（'(Game Disc)'、'(Omake Disc)'、'(Portrait CD)'）と
    # マスタリングの印（サターンの '(1M)'、'(1M, 4M)'）も除く
    label_re = re.compile(r" \([^()]*(?:Disc|CD)\)| \(\d+[A-Z](?:, \d+[A-Z])*\)")
    groups, order = {}, []
    for r in rows:
        name = disc_re.sub("", r["dump_name"])
        key = (r["title_id"], r["dump_kind"], label_re.sub("", name) if disc_re.search(r["dump_name"]) else name)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(r)
    out = []
    for key in order:
        g = groups[key]
        discs_no = [disc_re.search(r["dump_name"]).group(0) for r in g if disc_re.search(r["dump_name"])]
        if len(g) == 1 or len(discs_no) != len(g) or len(set(discs_no)) != len(g):
            # 1枚だけ・ディスク番号の無いものが混ざる・同じ番号のディスクが複数（マスタリング違い）なら、まとめない
            for r in g:
                out.append({**r, "discs": "1"})
            continue
        g.sort(key=lambda r: disc_re.search(r["dump_name"]).group(0))
        merged = dict(g[0])
        merged["dump_name"] = key[2]
        for col in ("size", "crc32", "md5", "sha1", "sha256", "verification", "rom_chip", "label_serial",
                    "first_dump_date", "nointro_number", "mame_name", "mame_status"):
            vals = [r.get(col, "") for r in g]
            merged[col] = ";".join(vals) if len(set(vals)) > 1 or col in ("size", "crc32", "md5", "sha1", "sha256") \
                else vals[0]
        merged["discs"] = str(len(g))
        out.append(merged)
    return out


def tags_of(name):
    return [t for grp in re.findall(r"\(([^)]*)\)", name) for t in grp.split(", ")]


def game_codes(g, ref, cfg):
    files = [f for s in g.findall("source") for f in s.findall("file")]
    codes = {c for f in files if f.get("serial") for c in f.get("serial").split(";")}
    if ref and ref["serial"]:
        codes.update(ref["serial"].split(";"))
    return {c2 for c in codes for c2 in [cfg["normalize_code"](c)] if c2}


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
    dv = re.search(r"\((DV [\d, ]+)\)", name)   # ディスクシステムのディスクの版（例: DV 2）
    ver = ver or (dv.group(1) if dv else None)
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


def mame_dump(software, key):
    """No-Intro に無いものを MAME ソフトウェアリストから作る（MD5・SHA256 は無い）。"""
    s = software.get(key)
    if s is None:
        return None
    rom = next(s.iter("rom"))
    return {
        "dump_name": rom.get("name"), "revision": "0", "size": rom.get("size"),
        "crc32": rom.get("crc"), "md5": "", "sha1": rom.get("sha1"), "sha256": "",
        "verification": "mame_only", "source_count": "", "first_dump_date": "", "rom_chip": "",
        "label_serial": "", "pcb": "", "save_type": "", "nointro_number": "",
        "mame_name": key, "mame_status": rom.get("status") or "good", "hash_source": "MAME",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("platform")
    ap.add_argument("--export", help="No-Intro DB Export の zip / xml")
    a = ap.parse_args()
    cfg = P.get(a.platform)
    DATA = cfg["dir"]
    code_of = cfg["code_of"]

    titles = C.read_csv(DATA / "jp_titles.csv")
    title_by_id = {t["id"]: t for t in titles}
    by_code = {}
    for t in titles:
        if t["model_number"]:
            by_code.setdefault(code_of(t["model_number"]), []).append(t)
    exports = cfg["nointro_export"] if isinstance(cfg["nointro_export"], list) else [cfg["nointro_export"]]
    games, versions = {}, []
    for pattern in exports:  # GB/GBC のように複数の DB Export を合わせる機種がある
        fb = cfg.get("nointro_export_fallback", {}).get(pattern)
        root, ver = C.load_nointro_export(pattern, a.export if len(exports) == 1 else None, fb)
        versions.append(ver)
        for g in root.iter("game"):
            name = g.get("name")
            if name in games and fb and fb.startswith("redump:") and games[name] is not g:
                # 別の DAT に同名の吸い出しがある（PCE の HuCARD 版と CD 版の『ドラえもん のび太のドラビアンナイト』）。
                # 名前に [2] などを付けて両方残す
                n = 2
                while f"{name} [{n}]" in games:
                    n += 1
                name = f"{name} [{n}]"
                g.set("name", name)
            games.setdefault(name, g)
    version = " / ".join(versions)
    dat = C.load_nointro_dat(cfg["nointro_dats"])
    mame = C.mame_crcs(cfg["mame_lists"])
    mame_sw = C.mame_software(cfg["mame_lists"])
    # 自動で結びつかない吸い出しの手動対応（dump_name → title_id。'-' は製品版に結びつけない）
    manual = {m["dump_name"]: m["title_id"] for m in C.read_csv(DATA / "overrides" / "dump_matches.csv")}
    nr_parents = {m["nointro_name"]: m["parent_id"]
                  for m in C.read_csv(DATA / "overrides" / "non_retail_parents.csv")}

    rows, non_retail, pending, unmatched, np_games = [], [], [], [], []
    for name, g in games.items():
        arch = g.find("archive")
        region = arch.get("region") or ""
        if "Japan" not in region and not (cfg.get("dump_world") and ("World" in region or "(World)" in name)):
            continue   # FC は日米共通の '(World)' も対象（例: Super Mario Bros. (World)）
        tags = tags_of(name)
        ref = dat.get(name)
        codes = game_codes(g, ref, cfg)
        world_only = "Japan" not in region

        # ---- 別リスト（A2〜A4）。対応する製品版は製品版の処理後に決める
        cat = non_retail_category(name, tags)
        if cat and world_only:
            continue   # '(World)' の試作品などは日本のものと限らない（自主制作ソフトが多い）
        if cat:
            pending.append((name, g, ref, codes, cat))
            continue

        # ---- ニンテンドウパワー版（No-Intro の (NP)）は別リストに結びつける
        if "NP" in tags:
            if not any(re.match(r"Proto|Possible Proto|Beta|Demo", t) for t in tags):
                np_games.append((name, g, ref, codes, tags))
            continue

        # ---- 製品版（jp_titles.csv）
        if any(EXCLUDE.match(t) for t in tags) or "Taikenban" in name:
            continue
        targets = [t for c in sorted(codes) for t in by_code.get(c, [])]
        if manual.get(name) == "-":
            continue   # 製品版に結びつけない（非売品の付録が製品版と同じシリアルを持つ場合など）
        if name in manual:   # 手動の対応はゲームコードより優先（同じコードの別作品がある場合）
            targets = [title_by_id[manual[name]]]
            codes = codes or {code_of(t["model_number"]) for t in targets} - {""}
        if not targets and ref:
            # コードがどこにも無い場合は、同じ CRC を持つ MAME エントリ経由でタイトルに結びつける
            names = {n for n, _ in mame.get(ref["crc"], [])}
            targets = [t for t in titles if t["mame_name"] and t["mame_name"] in names]
            codes = {code_of(t["model_number"]) for t in targets}
        if not targets:
            unmatched.append((name, g, ref, codes, tags))
            continue
        info = dump_info(g, ref, mame)
        for t in targets if info else []:
            rows.append({"title_id": t["id"], "title": t["title"], "game_code": "/".join(sorted(codes)),
                         "dump_kind": dump_kind(tags), **info})

    # ---- 製品版の2段目: ゲームコードも CRC も合わない吸い出し（別リビジョン・VC 版など）を、
    # No-Intro 名の本体（括弧より前）で結びつける。対応先は
    #   (1) 照合済みの吸い出しと本体が同じタイトル
    #   (2) 照合済みの MAME エントリの英語名（description の括弧より前）と本体が同じタイトル
    # のうち、ただ1つに決まるものだけ。GB のように ROM にゲームコードが無い機種で効く。
    base = lambda n: n.split(" (")[0]
    title_by_base = {}
    for r in rows:
        if r["dump_kind"] == "retail":
            title_by_base.setdefault(base(r["dump_name"]), set()).add(r["title_id"])
    for t in titles:
        sw = mame_sw.get(t["mame_name"]) if t["mame_name"] else None
        if sw is not None:
            title_by_base.setdefault(base(sw.findtext("description") or ""), set()).add(t["id"])
    for name, g, ref, codes, tags in unmatched:
        cands = title_by_base.get(base(name), set())
        if len(cands) != 1:
            continue
        t = title_by_id[next(iter(cands))]
        info = dump_info(g, ref, mame)
        if info:
            rows.append({"title_id": t["id"], "title": t["title"], "game_code": "/".join(sorted(codes)),
                         "dump_kind": dump_kind(tags), **info})

    # ---- ニンテンドウパワー版: No-Intro 名の本体が製品版と同じなら、その製品版を parent_id に持つ行へ。
    # 書き換え専用タイトルは overrides/np_dump_matches.csv（dump_name → np の id）で対応づける
    np_list = C.read_csv(DATA / "jp_nintendo_power.csv")
    np_by_parent = {}
    for n in np_list:
        if n["parent_id"]:
            np_by_parent.setdefault(n["parent_id"], []).append(n)
    np_manual = {m["dump_name"]: m["np_id"] for m in C.read_csv(DATA / "overrides" / "np_dump_matches.csv")}
    np_by_id = {n["id"]: n for n in np_list}
    np_linked = 0
    for name, g, ref, codes, tags in np_games:
        targets = []
        if name in np_manual:
            targets = [np_by_id[np_manual[name]]]
        else:
            cands = title_by_base.get(base(name), set())
            if len(cands) == 1:
                targets = np_by_parent.get(next(iter(cands)), [])
        info = dump_info(g, ref, mame) if len(targets) == 1 else None
        if info:
            n = targets[0]
            rows.append({"title_id": n["id"], "title": n["title"], "game_code": "/".join(sorted(codes)),
                         "dump_kind": "nintendo_power", **info})
            np_linked += 1
    if np_games:
        print(f"ニンテンドウパワー版の吸い出し: {np_linked}/{len(np_games)} 件を別リストに対応", file=sys.stderr)

    # ---- 別リスト（A2〜A4）
    # 開発版・試作品はゲームコードを別作品と共有していることがある（例: 烈火の剣の開発版が封印の剣のコード）ため、
    # コードではなく No-Intro 名の本体（括弧より前）が製品版の吸い出し名と一致するもので対応づける
    retail_by_base = {}
    for r in rows:
        if r["dump_kind"] == "retail":
            retail_by_base.setdefault(base(r["dump_name"]), set()).add(r["title_id"])
    labels = {"store_demo": "店頭体験版", "event_demo": "イベント体験版", "beta": "開発版", "prototype": "試作品",
              "tech_demo": "技術デモ", "business": "業務用"}
    disc_re = re.compile(r" \(Dis[ck] [0-9A-Z]+\)")
    seen_nr = set()
    for name, g, ref, codes, cat in pending:
        parent = nr_parents.get(name)
        if parent is None:
            cands = retail_by_base.get(base(name), set())
            parent = next(iter(cands)) if len(cands) == 1 else ""
        info = dump_info(g, ref, mame)
        number = g.find("archive").get("number")
        if not number:
            # libretro DAT から組み立てた場合はアーカイブ番号が無いので、名前（ディスク番号を除く）のハッシュを使う
            number = "h" + hashlib.sha1(disc_re.sub("", name).encode("utf-8")).hexdigest()[:8]
        nr_id = f"{cfg['id_prefix']}-nr-{number}"
        title = f"{title_by_id[parent]['title']}（{labels[cat]}）" if parent else japanese_title(name)
        if disc_re.search(name):  # 複数枚組は1行（吸い出しは merge_discs でまとめる）
            key = disc_re.sub("", name)
            if key in seen_nr:
                info = dump_info(g, ref, mame)
                if info:
                    rows.append({"title_id": nr_id, "title": title, "game_code": "/".join(sorted(codes)),
                                 "dump_kind": cat, **info})
                continue
            seen_nr.add(key)
            name = key
        non_retail.append({
            "id": nr_id, "title": title, "category": cat,
            "media": "gc_download" if any("GameCube" in t for t in tags_of(name)) else cfg.get("media", "cartridge"),
            "parent_id": parent, "game_code": "/".join(sorted(codes)), "nointro_name": name,
            "evidence": "No-Intro: " + ", ".join(t for t in tags_of(name)
                                                 if re.match(r"Demo|Kiosk|GameCube|Spaceworld|Beta|Proto|Debug|Tech Demo|SDK", t)),
            "verification": info["verification"] if info else "",
        })
        if info:
            rows.append({"title_id": nr_id, "title": title, "game_code": "/".join(sorted(codes)),
                         "dump_kind": cat, **info})

    # ---- 別リストの手動追加分（No-Intro の印では拾えないイベント体験版・業務用ソフトなど）
    for m in C.read_csv(DATA / "overrides" / "non_retail_manual.csv"):
        non_retail.append({"id": m["id"], "title": m["title"], "category": m["category"], "media": m["media"],
                           "parent_id": m["parent_id"], "game_code": "", "nointro_name": m["nointro_name"],
                           "evidence": m["evidence"], "verification": ""})
        g = games.get(m["nointro_name"]) if m["nointro_name"] else None
        if g is not None:
            ref = dat.get(m["nointro_name"])
            info = dump_info(g, ref, mame)
            codes = game_codes(g, ref, cfg)
            non_retail[-1]["game_code"] = "/".join(sorted(codes))
            non_retail[-1]["verification"] = info["verification"] if info else ""
            if info:
                rows.append({"title_id": m["id"], "title": m["title"], "game_code": "/".join(sorted(codes)),
                             "dump_kind": m["category"], **info})

    # ---- 非売品の本リスト（A1）
    for n in C.read_csv(DATA / "jp_not_for_sale.csv"):
        info = None
        if n["nointro_name"]:
            g = games.get(n["nointro_name"])
            if g is None:
                sys.exit(f"jp_not_for_sale.csv の nointro_name が No-Intro に見つかりません: {n['nointro_name']}")
            info = dump_info(g, dat.get(n["nointro_name"]), mame)
        elif n["mame_name"]:
            info = mame_dump(mame_sw, n["mame_name"])
        if info:
            rows.append({"title_id": n["id"], "title": n["title"], "game_code": code_of(n["model_number"]),
                         "dump_kind": "not_for_sale", **info})

    rows = merge_discs(rows)
    if cfg.get("hash_source"):
        for r in rows:
            if r["hash_source"] == "No-Intro":
                r["hash_source"] = cfg["hash_source"]

    kind_order = {"retail": 0, "collection": 1, "online": 1.5, "virtual_console": 2, "not_for_sale": 3, "nintendo_power": 4,
                  "store_demo": 5, "event_demo": 6, "beta": 7, "prototype": 8, "tech_demo": 9, "business": 10}
    rows.sort(key=lambda r: (r["title_id"], kind_order[r["dump_kind"]], r["revision"], r["dump_name"]))
    cols = ["title_id", "title", "game_code", "dump_name", "revision", "dump_kind"]
    rows = [{**{c: r[c] for c in cols}, **{k: v for k, v in r.items() if k not in cols}} for r in rows]
    C.write_csv(DATA / "jp_rom_dumps.csv", rows)
    non_retail.sort(key=lambda r: (["store_demo", "event_demo", "beta", "prototype", "tech_demo", "business"]
                                   .index(r["category"]),
                                   r["parent_id"] or "~", r["nointro_name"]))
    C.write_csv(DATA / "jp_non_retail.csv", non_retail)

    covered = {r["title_id"] for r in rows if r["dump_kind"] == "retail"}
    print(f"No-Intro DB Export {version}: 吸い出し {len(rows)} 行 / 製品版の吸い出しがあるタイトル "
          f"{len(covered)}/{len(titles)} / 別リスト {len(non_retail)} 件", file=sys.stderr)


if __name__ == "__main__":
    main()
