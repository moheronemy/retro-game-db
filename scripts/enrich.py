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
    # Wikipedia の一覧に無いが本リストに含めるタイトル（周辺機器に同梱されたソフトなど）
    extra = C.read_csv(data / "overrides" / "extra_titles.csv")
    if extra:
        rows = sorted(rows + [{k: v for k, v in e.items() if k != "source"} for e in extra],
                      key=lambda r: r["release_date"])
    if cfg.get("nintendo_power"):
        # ニンテンドウパワーの書き換え専用タイトルは別リスト（jp_nintendo_power.csv）で扱う
        import build_nintendo_power as NP
        np_rows = NP.parse_np(cfg)
        dropped = [r for r in rows if NP.is_np_only_row(r, np_rows)]
        rows = [r for r in rows if not NP.is_np_only_row(r, np_rows)]
        print(f"ニンテンドウパワー書き換え専用として除外: {len(dropped)} 件 "
              f"（{', '.join(r['title'] for r in dropped)}）", file=sys.stderr)
    for i, r in enumerate(rows):
        r["_i"] = i
    overrides = {}
    for o in C.read_csv(data / "overrides" / "matches.csv"):
        d = overrides.setdefault((o["release_date"], o["title"]), {})
        for col in ("madb_id", "mame_name", "maru_code", "model_number", "price_yen", "price_tax",
                    "release_date_fix", *cfg.get("extra_columns", [])):
            if o.get(col):
                d[col] = o[col]

    madb = C.load_madb(cfg["madb_platforms"])
    if cfg.get("madb_filter"):  # 同じ機種名で別媒体・別機種が混在する（FC のディスクカード、MD の 32X など）
        madb = [x for x in madb if cfg["madb_filter"](x)]
    mame = C.load_mame(cfg["mame_lists"], cfg.get("mame_jp_models"), cfg.get("mame_all_japanese", ()))
    if cfg.get("mame_filter"):   # 業務用と家庭用が混ざったリスト（ネオジオ）から家庭用だけを使う
        mame = [m for m in mame if cfg["mame_filter"](m)]
    nointro = nointro_models(cfg)
    maru = C.load_maru(cfg["maru"]) if cfg.get("maru") else None
    print(f"MADB: {len(madb)} 件 / MAME 日本版: {len(mame)} 件"
          + (f" / maru-chang: {len(maru)} 件" if maru is not None else ""), file=sys.stderr)
    m_madb = C.match(rows, madb, overrides, "madb_id", cfg.get("match_date_only", False), cfg.get("match_undated"))
    m_mame = C.match(rows, mame, overrides, "mame_name", cfg.get("match_date_only", False), cfg.get("match_undated"))
    models_from = cfg["models_from"]
    key = cfg.get("model_key", lambda m: m)   # 照合で同じとみなす型番の表記ゆれ（PCE のハイフン有無など）
    keys = lambda codes: {key(c) for c in codes}

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
        if model and key(model) in keys(mame_codes):
            srcs.append("MAME")
        if model and key(model) in keys(madb_codes):
            srcs.append("MADB")
        r["_alt_titles"] = (md["titles"] if md else []) + (mm["titles"] if mm else [])
        r["_codes"] = mame_codes + [c for c in madb_codes if c not in mame_codes]   # 再販版の型番など（SG-1000 のマイカード）
        r.update({"model_number": model, "_model_srcs": srcs, "_md": md, "_mm": mm,
                  "madb_id": md["key"] if md else "", "mame_name": mm["key"] if mm else ""})

        issues = []
        if md_how == "auto" and md_sc < C.REVIEW_SIM:
            issues.append(f"MADB低スコア{md_sc:.2f}")
        if mm_how == "auto" and mm_sc < C.REVIEW_SIM:
            issues.append(f"MAME低スコア{mm_sc:.2f}")
        for name, src, how in (("MADB", md, md_how), ("MAME", mm, mm_how)):
            if how == "date_only":
                issues.append(f"{name}同日1件のみで照合（{src['label']}）")
        if not md and md_how != "manual" and cfg["madb_platforms"]:
            issues.append("MADB未照合")
        if not mm and mm_how != "manual" and cfg["mame_lists"] and not cfg.get("mame_partial"):
            issues.append("MAME未照合")
        if md and md_how == "auto" and C.VARIANT.search(md["label"]) and not C.VARIANT.search(r["title"]):
            issues.append("MADBが通常版以外の可能性")
        if mame_codes and madb_codes and key(mame_codes[0]) not in keys(madb_codes):
            issues.append(f"型番不一致 MAME={mame_codes[0]} MADB={'/'.join(madb_codes)}")
        r["_issues"] = issues

    if cfg.get("psxdc"):
        # MADB・MAME で型番が決まらない行を psxdatacenter.com のデータで補う（PS1 は発売日つき、PS2 は題名だけ）
        import psxdc
        entries = psxdc.load_ps1(models_from) if cfg["psxdc"] == "ps1" else psxdc.load_ps2(models_from)
        used_models = {r["model_number"] for r in rows if r["model_number"]}
        no_model = [r for r in rows if not r["model_number"]]
        m_px = psxdc.match(no_model, entries, used_models, by_date=cfg["psxdc"] == "ps1")
        for r in no_model:
            hit = m_px.get(r["_i"])
            if not hit:
                continue
            e, sc, how = hit
            r["model_number"] = e["key"]
            r["_model_srcs"].append("psxdatacenter")
            if how == "date_only":
                r["_issues"].append(f"psxdatacenter同日1件のみで型番を照合（{e['label']}）")
            elif sc < 0.7:
                r["_issues"].append(f"psxdatacenter低スコア{sc:.2f}で型番を照合（{e['label']}）")
        print(f"psxdatacenter: {len(entries)} 件から型番 {len(m_px)} 件を補完", file=sys.stderr)

    if cfg.get("dat_title_models"):
        # MADB・MAME で型番が決まらない行を、DAT（Redump）の題名とシリアルで補う（3DO）。DAT に発売日は無いので
        # psxdatacenter の PS2 と同じく、ローマ字にした題名がとても似ていてほかに候補の無いものだけを採る
        import psxdc
        entries = []
        for name in cfg["nointro_dats"]:
            for block in C.nointro_dat_text(name).split("game (")[1:]:
                gname = re.search(r'name "([^"]+)"', block).group(1)
                if not re.search(r"\((?:[^()]*, )?(?:Japan|World)(?:, [^()]*)?\)", gname):
                    continue
                serials = [m for s_ in re.findall(r'serial "([^"]+)"', block) for m in models_from(s_)]
                title = re.sub(r" \([^()]*\)", "", gname)
                if serials and not any(e["key"] == serials[0] for e in entries):
                    entries.append({"key": serials[0], "serials": serials, "titles": [title], "date": "", "label": gname})
        used_models = {r["model_number"] for r in rows if r["model_number"]}
        no_model = [r for r in rows if not r["model_number"]]
        m_dt = psxdc.match(no_model, entries, used_models, by_date=False)
        for r in no_model:
            hit = m_dt.get(r["_i"])
            if hit:
                e, sc, _ = hit
                r["model_number"] = e["key"]
                r["_model_srcs"].append("Redump")
                r["_issues"].append(f"Redumpの題名（{e['label']}）から型番を補完（類似度{sc:.2f}）")
        print(f"DAT の題名から型番 {len(m_dt)} 件を補完（候補 {len(entries)} 件）", file=sys.stderr)

    dat_links = []
    if cfg.get("dat_title_link"):
        # DAT のシリアルが型番と違う機種（Xbox はソフト内部のタイトル ID）は、吸い出しを題名で結びつける。
        # 日本を含む地域の吸い出しを基本の題名（括弧の印を除いたもの）ごとにまとめ、ローマ字にした題名がとても似ていて
        # ほかに候補の無いものだけを採る。結果は review/dat_title_matches.csv（build_dumps.py が手動の対応の次に使う）
        import psxdc
        groups = {}
        for name in cfg["nointro_dats"]:
            for block in C.nointro_dat_text(name).split("game (")[1:]:
                gname = re.search(r'name "([^"]+)"', block).group(1)
                first = re.search(r"\(([^()]*)\)", gname)
                if not first or not ({"Japan", "World"} & set(first.group(1).split(", "))):
                    continue
                base = re.sub(r" \([^()]*\)", "", gname)
                groups.setdefault(base, []).append(gname)
        entries = [{"key": b, "serials": [b], "titles": [b], "date": "", "label": b, "names": n} for b, n in groups.items()]
        m_dl = psxdc.match(rows, entries, set(), by_date=False)
        for r in rows:
            hit = m_dl.get(r["_i"])
            if hit:
                dat_links.append((r, hit[0], hit[1]))
        print(f"DAT の題名で吸い出し {len(m_dl)} 件を照合（候補 {len(entries)} 件）", file=sys.stderr)

    m_maru = C.match_maru(rows, maru, overrides, cfg.get("code_of") if cfg.get("ref_code_models") else None,
                          cfg.get("maru_date_only", False)) if maru is not None else {}
    report = []
    for r in rows:
        md, mm, ma = r["_md"], r["_mm"], m_maru.get(r["_i"])
        ov = overrides.get((r["release_date"], r["title"]), {})
        issues = r["_issues"]

        # ---- 型番: 既存の出典で決まらなければ maru-chang で補う
        model, srcs = r["model_number"], r["_model_srcs"]
        if not model and ma and ma["model"]:
            model = ma["model"]
        if not model and r.get("ref_code") and cfg.get("ref_code_models"):
            model = cfg["ref_code_models"](r["ref_code"])
        if model and r.get("ref_code") and cfg.get("code_of") and cfg["code_of"](model) == r["ref_code"]:
            srcs.append("Wikipedia")
        if model and ma and ma["model"] == model:
            srcs.append("maru-chang")
        if model and key(model) in keys(nointro):
            srcs.append("No-Intro")
        check_ni = cfg.get("nointro_model_check", lambda r: True)
        if model and nointro and key(model) not in keys(nointro) and check_ni({**r, **{c: fn(r) for c, fn in cfg.get("derive", {}).items()}}):
            issues.append("型番がNo-Introに無い")
        if ma and ma["model"] and model and ma["model"] != model:
            issues.append(f"型番不一致 maru-chang={ma['model']}")
        if cfg.get("check_row"):
            issues += cfg["check_row"]({**r, "model_number": model})

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
            elif C.net_price(yen, tax, date0) > 1.3 * C.net_price(my, mt, date0):
                # MADB が maru-chang より3割以上高い → 本体・周辺機器との同梱版などの価格とみて通常版の価格に置き換える
                issues.append(f"MADBの価格（{yen}{tax}・{package}）を同梱版等とみて maru-chang の価格に置換")
                yen, tax, price_src, package = my, mt, "maru-chang", ""
            elif C.VARIANT.search(package) and not C.VARIANT.search(r["title"]):
                # MADB が限定版・廉価版・同梱版などの価格だった → 通常版の価格に置き換える
                yen, tax, price_src, package = my, mt, "maru-chang", ""
            elif (yen == my and tax == "税抜" and mt == "税込" and cfg.get("tax_inclusive_from")
                  and date0 >= cfg["tax_inclusive_from"]):
                # 総額表示義務化以降なのに MADB が税抜表記 → maru-chang の税込表記を採る
                tax, price_src = "税込", "MADB+maru-chang"
            else:
                issues.append(f"価格不一致 MADB={yen}{tax} maru-chang={my}{mt}")

        if yen and cfg.get("tax_free_before") and date0 < cfg["tax_free_before"]:
            tax = "税なし"   # 消費税導入（1989年4月）前の発売
        # ---- 発売日: 一致した出典を記録する（Wikipedia が基準）
        date = ov.get("release_date_fix") or date0
        dsrc = ["manual"] if ov.get("release_date_fix") else ["Wikipedia"]
        for name, src in (("MADB", md), ("MAME", mm), ("maru-chang", ma)):
            if src and src["date"] == date:
                dsrc.append(name)
            elif src and src["date"] and C.days(date, src["date"]) is not None:
                issues.append(f"発売日不一致 {name}={src['date']}")
            elif src and src["date"] and not C.date_compatible(date, src["date"]):
                issues.append(f"発売日不一致 {name}={src['date']}")   # 日まで分からない発売日どうし（'1984-12' と '1985'）
        if maru is not None and not ma and not ov.get("maru_code"):
            issues.append("maru-chang未照合")
        if r.get("_maru_date_only"):
            issues.append(f"maru-chang同日1件のみで照合（{ma['label']}）")

        for col, fn in cfg.get("derive", {}).items():  # 型番などから決まる列（DS の compat）
            r[col] = fn({**r, "model_number": model})
        for col in cfg.get("extra_columns", []):   # 手動補正（SG-1000 のマイカード再販の型番など）
            if ov.get(col):
                r[col] = ov[col]
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
    if cfg.get("dat_title_link"):
        C.write_csv(data / "review" / "dat_title_matches.csv",
                    [{"dump_name": n, "title_id": r["id"], "title": r["title"], "dat_title": e["label"], "score": f"{sc:.2f}"}
                     for r, e, sc in dat_links for n in e["names"]])
    print(f"{len(rows)} 件: 型番 {sum(bool(r['model_number']) for r in rows)} / "
          f"価格 {sum(bool(r['price_yen']) for r in rows)} / 要確認 {len(report)}", file=sys.stderr)


if __name__ == "__main__":
    main()
