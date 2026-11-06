#!/usr/bin/env python3
"""No-Intro に無いソフトの別リストに、MAME ソフトウェアリストの型番（serial）とハッシュを付ける。

SG-1000 の BASIC・教育用ソフト（SC-3000 専用）は No-Intro に無いので、MAME の `sc3000_cart` を使う。
MAME には発売日が無く、日本語の題名の書き方も違う（「中学必修英単語 (中学一年)」）ため、対応は手で決める。

入力:
  <dir>/<list>.csv                       fetch_wikipedia_list.py --list の出力（例: data/sg1000/jp_non_game.csv）
  <dir>/overrides/<list key>_mame.csv    題名 → MAME のソフト名（親だけ。別版〈alt・40k map〉は吸い出し一覧に含める）
出力:
  <list>.csv に model_number・mame_name 列を加えて書き直す
  <list>_rom_dumps.csv                   吸い出し（MAME のハッシュ。hash_source = MAME）

使い方:
  python3 scripts/build_mame_list.py sg1000 non_game sc3000_cart
"""
import argparse
import sys
import xml.etree.ElementTree as ET

import common as C
import platforms as P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("platform")
    ap.add_argument("list")
    ap.add_argument("mame_list")
    a = ap.parse_args()
    cfg = P.get(a.platform)
    lcfg = cfg["extra_lists"][a.list]
    path = cfg["dir"] / lcfg["out"]
    rows = C.read_csv(path)
    mapping = {m["title"]: m["mame_name"] for m in C.read_csv(cfg["dir"] / "overrides" / f"{a.list}_mame.csv")}
    soft = {}
    for s in ET.parse(C.mame_xml(a.mame_list)).getroot().findall("software"):
        soft[s.get("name")] = s
    dumps = []
    for r in rows:
        name = mapping.pop(r["title"], "")
        r["mame_name"], r["model_number"] = name, ""
        if not name:
            continue
        if name not in soft:
            sys.exit(f"MAME {a.mame_list} にありません: {name}")
        info = {i.get("name"): i.get("value") for i in soft[name].findall("info")}
        r["model_number"] = info.get("serial", "")
        # 親と、その別版（clone）をすべて載せる
        for s in [soft[name]] + [x for x in soft.values() if x.get("cloneof") == name]:
            for rom in s.iter("rom"):
                if rom.get("crc"):
                    dumps.append({"title_id": r["id"], "title": r["title"], "mame_name": s.get("name"),
                                  "mame_description": s.findtext("description"), "rom_name": rom.get("name"),
                                  "size": rom.get("size"), "crc32": rom.get("crc"), "sha1": rom.get("sha1"),
                                  "mame_status": s.get("supported", "yes"), "hash_source": "MAME"})
    if mapping:
        sys.exit(f"{a.list}_mame.csv の題名がリストにありません: {list(mapping)}")
    fields = list(rows[0].keys())
    C.write_csv(path, rows, fields)
    C.write_csv(path.with_name(path.stem + "_rom_dumps.csv"), dumps)
    print(f"{len(rows)} 件: 型番 {sum(bool(r['model_number']) for r in rows)} / 吸い出し {len(dumps)} 行", file=sys.stderr)


if __name__ == "__main__":
    main()
