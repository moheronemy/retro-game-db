#!/usr/bin/env python3
"""国内タイトル一覧に型番・価格を付与し、発売日を照合する。

入力（<dir> は機種ごとのデータディレクトリ。例: data/gba）:
  <dir>/wikipedia_titles.csv            fetch_wikipedia_list.py の出力（発売順の基礎リスト）
  <dir>/overrides/group_expansions.csv  まとめ行を個別タイトルに展開する表（任意）
  <dir>/overrides/matches.csv           自動照合の手動補正（任意）
  メディア芸術データベース(MADB) gm301 … 価格・型番
  MAME ソフトウェアリスト            … 型番・発売日
  No-Intro DAT（libretro 収録）      … 型番の検証
  maru-chang.com（GBA のみ）          … 型番・価格の補完と照合、発売日の照合

出力:
  <dir>/jp_titles.csv
  <dir>/review/match_report.csv         要確認の照合結果

使い方:
  python3 scripts/enrich.py gba         # ソースは .cache/ にダウンロードして再利用
"""
import argparse
import re
import sys

import common as C
import platforms as P

BASE_FIELDS = ["id", "release_date", "title", "publisher", "model_number", "price_yen", "price_tax",
               "notes", "wikipedia_article", "release_date_sources", "model_number_source", "price_source",
               "price_package", "madb_id", "mame_name"]


def expand_groups(rows, path):
    groups = {}
    for g in C.read_csv(path):
        groups.setdefault((g["group_release_date"], g["group_title"]), []).append(g["title"])
    out = []
    for r in rows:
        titles = groups.pop((r["release_date"], r["title"]), None)
        if titles:
            for t in titles:
                out.append({**r, "title": t, "notes": f"『{r['title']}』として同時発売"})
        else:
            out.append(r)
    if groups:
        sys.exit(f"group_expansions.csv に未使用の行があります: {list(groups)}")
    return out


def nointro_models(cfg):
    """No-Intro DAT のシリアルから、型番の集合を得る（型番の検証用）。"""
    out = set()
    for name in cfg["nointro_dats"]:
        for serial in re.findall(r'serial "([^"]+)"', C.nointro_dat_text(name)):
            out.update(cfg["models_from_serial"](serial))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("platform")
    a = ap.parse_args()
    cfg = P.get(a.platform)
    data = cfg["dir"]

    rows = expand_groups(C.read_csv(data / "wikipedia_titles.csv"), data / "overrides" / "group_expansions.csv")
    for i, r in enumerate(rows):
        r["_i"] = i
    overrides = {}
    for o in C.read_csv(data / "overrides" / "matches.csv"):
        d = overrides.setdefault((o["release_date"], o["title"]), {})
        for col in ("madb_id", "mame_name", "maru_code", "model_number", "price_yen", "price_tax",
                    "release_date_fix"):
            if o.get(col):
                d[col] = o[col]

    madb = C.load_madb(cfg["madb_platforms"])
    mame = C.load_mame(cfg["mame_lists"])
    nointro = nointro_models(cfg)
    maru = C.load_maru(cfg["maru"]) if cfg.get("maru") else None
    print(f"MADB: {len(madb)} 件 / MAME 日本版: {len(mame)} 件"
          + (f" / maru-chang: {len(maru)} 件" if maru is not None else ""), file=sys.stderr)
    m_madb = C.match(rows, madb, overrides, "madb_id")
    m_mame = C.match(rows, mame, overrides, "mame_name")
    models_from = cfg["models_from"]

    for r in rows:
        i = r["_i"]
        md, md_sc, md_how = m_madb.get(i, (None, 0, ""))
        mm, mm_sc, mm_how = m_mame.get(i, (None, 0, ""))
        ov = overrides.get((r["release_date"], r["title"]), {})

        mame_codes = models_from(mm["serial"]) if mm else []
        madb_codes = models_from(md["product_id"]) if md else []
        # 型番の優先順位: 手動 > MAME（ROMのゲームコード） > MADB（パッケージ表記。誤記あり）
        model = ov.get("model_number") or (mame_codes or madb_codes or [""])[0]
        srcs = []
        if ov.get("model_number"):
            srcs.append("manual")
        if model and model in mame_codes:
            srcs.append("MAME")
        if model and model in madb_codes:
            srcs.append("MADB")
        r.update({"model_number": model, "_model_srcs": srcs, "_md": md, "_mm": mm,
                  "madb_id": md["key"] if md else "", "mame_name": mm["key"] if mm else ""})

        issues = []
        if md_how == "auto" and md_sc < C.REVIEW_SIM:
            issues.append(f"MADB低スコア{md_sc:.2f}")
        if mm_how == "auto" and mm_sc < C.REVIEW_SIM:
            issues.append(f"MAME低スコア{mm_sc:.2f}")
        if not md and md_how != "manual":
            issues.append("MADB未照合")
        if not mm and mm_how != "manual":
            issues.append("MAME未照合")
        if md and md_how == "auto" and C.VARIANT.search(md["label"]) and not C.VARIANT.search(r["title"]):
            issues.append("MADBが通常版以外の可能性")
        if mame_codes and madb_codes and mame_codes[0] not in madb_codes:
            issues.append(f"型番不一致 MAME={mame_codes[0]} MADB={'/'.join(madb_codes)}")
        r["_issues"] = issues

    m_maru = C.match_maru(rows, maru, overrides) if maru is not None else {}
    report = []
    for r in rows:
        md, mm, ma = r["_md"], r["_mm"], m_maru.get(r["_i"])
        ov = overrides.get((r["release_date"], r["title"]), {})
        issues = r["_issues"]

        # ---- 型番: 既存の出典で決まらなければ maru-chang で補う
        model, srcs = r["model_number"], r["_model_srcs"]
        if not model and ma and ma["model"]:
            model = ma["model"]
        if model and ma and ma["model"] == model:
            srcs.append("maru-chang")
        if model and model in nointro:
            srcs.append("No-Intro")
        if model and nointro and model not in nointro:
            issues.append("型番がNo-Introに無い")
        if ma and ma["model"] and model and ma["model"] != model:
            issues.append(f"型番不一致 maru-chang={ma['model']}")

        # ---- 価格: MADB を基本に、maru-chang で補完・訂正する
        date0 = r["release_date"]
        yen, tax = C.parse_price(md["price"]) if md else ("", "")
        price_src, package = ("MADB", md["label"]) if yen else ("", "")
        my, mt = (ma["yen"], ma["tax"]) if ma and ma["yen"] else ("", "")
        if ov.get("price_yen"):
            yen, tax, price_src, package = ov["price_yen"], ov.get("price_tax", ""), "manual", ""
        elif my and not yen:
            yen, tax, price_src, package = my, mt, "maru-chang", ""
        elif my and yen:
            if abs(C.net_price(yen, tax, date0) - C.net_price(my, mt, date0)) <= 1:
                price_src = "MADB+maru-chang"
            elif C.VARIANT.search(package) and not C.VARIANT.search(r["title"]):
                # MADB が限定版・廉価版・同梱版などの価格だった → 通常版の価格に置き換える
                yen, tax, price_src, package = my, mt, "maru-chang", ""
            elif (yen == my and tax == "税抜" and mt == "税込" and cfg.get("tax_inclusive_from")
                  and date0 >= cfg["tax_inclusive_from"]):
                # 総額表示義務化以降なのに MADB が税抜表記 → maru-chang の税込表記を採る
                tax, price_src = "税込", "MADB+maru-chang"
            else:
                issues.append(f"価格不一致 MADB={yen}{tax} maru-chang={my}{mt}")

        # ---- 発売日: 一致した出典を記録する（Wikipedia が基準）
        date = ov.get("release_date_fix") or date0
        dsrc = ["manual"] if ov.get("release_date_fix") else ["Wikipedia"]
        for name, src in (("MADB", md), ("MAME", mm), ("maru-chang", ma)):
            if src and src["date"] == date:
                dsrc.append(name)
            elif src and src["date"] and C.days(date, src["date"]) is not None:
                issues.append(f"発売日不一致 {name}={src['date']}")
        if maru is not None and not ma and not ov.get("maru_code"):
            issues.append("maru-chang未照合")

        r.update({
            "release_date": date, "release_date_sources": "+".join(dsrc),
            "model_number": model, "model_number_source": "+".join(srcs),
            "price_yen": yen, "price_tax": tax, "price_source": price_src,
            # 価格の根拠になったMADBのパッケージ名（限定版・セット品等の場合に判別できるように）
            "price_package": package if price_src.startswith("MADB") else "",
            "maru_code": ma["key"] if ma else "",
        })
        if issues:
            rep = {
                "release_date": r["release_date"], "title": r["title"], "issues": "; ".join(issues),
                "madb_id": md["key"] if md else "", "madb_title": md["label"] if md else "",
                "madb_date": md["date"] if md else "",
                "mame_name": mm["key"] if mm else "", "mame_title": mm["label"] if mm else "",
                "mame_date": mm["date"] if mm else "",
            }
            if maru is not None:
                rep.update({"maru_code": ma["key"] if ma else "", "maru_title": ma["label"] if ma else "",
                            "maru_date": ma["date"] if ma else ""})
            report.append(rep)

    for n, r in enumerate(rows, 1):
        r["id"] = f"{cfg['id_prefix']}-{n:04d}"
    extra = [c for c in cfg.get("extra_columns", [])]
    fields = BASE_FIELDS[:4] + extra + BASE_FIELDS[4:] + (["maru_code"] if maru is not None else [])
    C.write_csv(data / "jp_titles.csv", rows, fields)
    C.write_csv(data / "review" / "match_report.csv", report)
    print(f"{len(rows)} 件: 型番 {sum(bool(r['model_number']) for r in rows)} / "
          f"価格 {sum(bool(r['price_yen']) for r in rows)} / 要確認 {len(report)}", file=sys.stderr)


if __name__ == "__main__":
    main()
