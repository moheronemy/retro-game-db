#!/usr/bin/env python3
"""ニンテンドウパワー（書き換えサービス）で提供されたタイトルの別リストを作る。

入力:
  ja.wikipedia「ニンテンドウパワーのゲームタイトル一覧」の該当機種の表（.cache/wikipedia/ に保存して再利用）
  <dir>/jp_titles.csv          通常版との対応づけに使う（enrich.py の後に実行する）

出力:
  <dir>/jp_nintendo_power.csv  1行 = 1書き換えタイトル
      np_only=yes は通常版のカートリッジが発売されなかった書き換え専用タイトル。
      enrich.py はこれらを本リスト（jp_titles.csv）から除く（parse_np を共有）。

実行順: fetch_wikipedia_list.py → enrich.py → build_nintendo_power.py → build_dumps.py

使い方:
  python3 scripts/build_nintendo_power.py gb
"""
import argparse
import re
import sys

import common as C
import fetch_wikipedia_list as F
import platforms as P

COLUMNS = ("np_date", "retail_date", "title", "publisher", "flash_blocks", "save_blocks", "sheet_no",
           "product_no", "notes")


def parse_np(cfg, refresh=False):
    """ニンテンドウパワーの一覧（Wikipedia）の表を読む。"""
    np_cfg = cfg["nintendo_power"]
    cache = C.CACHE / "wikipedia" / f"{np_cfg['page']}.wiki"
    if cache.exists() and not refresh:
        text = cache.read_text(encoding="utf-8")
    else:
        text, _ = F.fetch_wikitext(np_cfg["page"])
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(text, encoding="utf-8")
    table = F.section(text, np_cfg["section"])
    rows = []
    in_table = False
    for block in re.split(r"^\|-.*$", table, flags=re.M):
        lines = []
        for ln in block.splitlines():
            if ln.startswith("{|"):
                in_table = True; continue
            if ln.startswith("|}"):
                in_table = False; continue
            if not in_table or ln.startswith("!") or ln.startswith("|+"):
                continue
            if ln.startswith("|"):
                lines.append(ln[1:])
            elif lines:
                lines[-1] += "\n" + ln
        if not lines:
            continue
        cells = [c for ln in lines for c in F.split_cells(ln)]
        c = dict(zip(COLUMNS, cells))
        retail = F.parse_date(F.plain(c.get("retail_date", "")))
        rows.append({
            "np_date": F.parse_date(F.plain(c.get("np_date", ""))),
            "retail_date": retail,
            "title": F.title_text(c.get("title", "")),
            "publisher": F.plain(c.get("publisher", "")),
            "np_only": "" if retail else "yes",
            "flash_blocks": F.plain(c.get("flash_blocks", "")),
            "save_blocks": F.plain(c.get("save_blocks", "")),
            "sheet_no": F.plain(c.get("sheet_no", "")),
            "product_no": F.plain(c.get("product_no", "")),
            "notes": F.plain(c.get("notes", "")),
            "wikipedia_article": F.link_target(c.get("title", "")),
        })
    return rows


def is_np_only_row(row, np_rows):
    """本リストの行が書き換え専用タイトル（＝本リストに載せないもの）かどうか。
    本リストでの発売日は書き換え開始日になっている（1日ずれている行があるため31日以内で照合）。"""
    def near(n):
        d = C.days(n["np_date"], row["release_date"])
        return d is not None and d <= 31
    return any(n["np_only"] and near(n) and C.sim(n["title"], row["title"]) >= 0.8 for n in np_rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("platform")
    ap.add_argument("--refresh", action="store_true")
    a = ap.parse_args()
    cfg = P.get(a.platform)
    if not cfg.get("nintendo_power"):
        sys.exit(f"{a.platform} にはニンテンドウパワーの設定がありません")
    rows = parse_np(cfg, a.refresh)

    # 通常版との対応: 通常版の発売日が同じで、タイトルが最も近い行
    titles = C.read_csv(cfg["dir"] / "jp_titles.csv")
    for r in rows:
        r["parent_id"] = ""
        if not r["retail_date"]:
            continue
        cands = [(C.sim(r["title"], t["title"]), t) for t in titles if t["release_date"] == r["retail_date"]]
        # 同じ発売日の候補が1件だけならそれ（例: 一覧の「beatmaniaGB」と本リストの「ビートマニアGB」）
        cands = [x for x in cands if x[0] >= 0.5] or (cands if len(cands) == 1 else [])
        if cands:
            r["parent_id"] = max(cands, key=lambda x: x[0])[1]["id"]
    for i, r in enumerate(rows, 1):
        r["id"] = f"{cfg['id_prefix']}-np-{i:04d}"
    fields = ["id", "np_date", "title", "publisher", "np_only", "retail_date", "parent_id", "flash_blocks",
              "save_blocks", "sheet_no", "product_no", "notes", "wikipedia_article"]
    C.write_csv(cfg["dir"] / "jp_nintendo_power.csv", rows, fields)
    print(f"{len(rows)} 件（書き換え専用 {sum(r['np_only'] == 'yes' for r in rows)} 件、"
          f"通常版と対応 {sum(bool(r['parent_id']) for r in rows)} 件）", file=sys.stderr)


if __name__ == "__main__":
    main()
