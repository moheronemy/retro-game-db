#!/usr/bin/env python3
"""配信専用などの別リスト（DSiウェア・Wiiウェア・PSN・PSP / Xbox 360 のダウンロード専売）に CERO の年齢区分を付ける。

別リストは MADB と照合しないので、CERO 公式サイトのタイトル検索（scripts/fetch_cero.py で .cache/cero/ に取得）だけを使う。
照合の規則は本リスト（enrich.py）と同じ（cero.official_lookup: 題名の一致か類似度 0.9 以上で番号が同じもの。
同じ題名で区分の違う審査が複数あるものは採らない）。platforms.py の extra_lists に cero_official のあるリストが対象。
fetch_wikipedia_list.py --list で別リストを作り直したら、そのあとに実行する。

使い方: python3 scripts/cero_extra_lists.py            # 全機種
        python3 scripts/cero_extra_lists.py ds wii     # 指定した機種だけ
"""
import csv
import sys

import cero as CR
import common as C
import platforms as P

COLS = ["cero", "cero_descriptors", "cero_source", "cero_descriptors_source"]


def main():
    keys = sys.argv[1:] or list(P.PLATFORMS)
    for key in keys:
        cfg = P.get(key)
        for name, lcfg in cfg.get("extra_lists", {}).items():
            if not lcfg.get("cero_official"):
                continue
            path = cfg["dir"] / lcfg["out"]
            raw = path.read_bytes()
            eol = "\r\n" if b"\r\n" in raw[:2000] else "\n"
            rows = C.read_csv(path)
            fields = [f for f in rows[0].keys() if f not in COLS] if rows else []
            at = fields.index("publisher") + 1 if "publisher" in fields else len(fields)
            fields = fields[:at] + COLS + fields[at:]
            official = CR.load_official(lcfg["cero_official"])
            got = conflict = 0
            for r in rows:
                val = descs = src = ""
                if r.get("release_date", "") >= CR.CERO_START or not r.get("release_date"):
                    off = CR.official_lookup(official, r["title"], C.sim, date=r.get("release_date", ""))
                    if off and off[0] == "conflict":
                        conflict += 1
                    elif off:
                        val, descs, src = off[0], ";".join(off[1]), "CERO公式"
                        got += 1
                r.update({"cero": val, "cero_descriptors": descs, "cero_source": src,
                          "cero_descriptors_source": "CERO公式" if descs else ""})
            with open(path, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator=eol)
                w.writeheader()
                w.writerows(rows)
            print(f"{key} {lcfg['out']}: {got}/{len(rows)} 件に区分（CERO 公式で食い違い {conflict} 件は空欄）", file=sys.stderr)


if __name__ == "__main__":
    main()
