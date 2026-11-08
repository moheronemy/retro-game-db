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
  <dir>/review/match_notes.csv          値の決め方の注記（確かめ済みの照合方法・置き換えの記録・裏付けのある低スコアの照合）

使い方:
  python3 scripts/enrich.py gba         # ソースは .cache/ にダウンロードして再利用
"""
import argparse
import re
import sys

import common as C
import platforms as P

BASE_FIELDS = ["id", "release_date", "title", "publisher", "model_number", "price_yen", "price_tax", "price_note",
               "notes", "wikipedia_article", "release_date_sources", "model_number_source", "price_source",
               "price_package", "madb_id", "mame_name"]


# 要確認レポートではなく注記（review/match_notes.csv）に回すもの: 確かめ済みの照合方法・置き換えの記録
NOTE_RE = re.compile(r"Redumpの題名|psxdatacenter|同日1件のみ|型番をDATにあるもの|MADBの価格（.*）を同梱版等|MADBの見本盤|CERO公式を採用"
                     r"|GameTDB の題名")


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


# Redump の名前の括弧のうち、版の印でないもの（地域・言語・ディスク・版数）
_DAT_PLAIN_TAG = re.compile(r"^(?:(?:Japan|World|USA|Europe|Asia|Korea)(?:, .*)?|(?:[A-Z][a-z])(?:,[A-Z][a-z])*|Disc \d+|Rev [0-9A-Z]+|v\d.*)$")
# 体験版・店頭用など、製品の型番ではないもの
_DAT_DEMO_TAG = re.compile(r"Taikenban|Demo|Trial|Sample|Kiosk|Tentou|Beta|Proto", re.I)


# MAME の serial に添えられた版の印（限定版・廉価版などの型番は通常版の型番の候補にしない）
_EDITION_NOTE = re.compile(r"\((?:[^)]*(?:Genteiban|Gentei|Shokai|Limited|Premium|Collection|Best|Satakore|Reprint|Doukon|Set|Box|Pack))[^)]*\)", re.I)


def dat_title_entries(cfg, models_from, madb):
    """DAT（Redump）の日本版を基本の題名（括弧の印を除いたもの）ごとにまとめ、型番の候補にする。
    同じ題名に複数のシリアル（初回限定版・the Best など）があるものは、
      0. 廉価版の型番帯（設定の reissue_serial。Redump は再販に印が無いことが多い）を除く
      1. 体験版などを除く  2. MADB でほかの商品（別の版）の型番になっているものを除く
      3. それでも複数なら、名前に版の印の無いもの（通常版）だけを残す
    の順に絞り、1 つに決まったものだけを候補にする（決まらないものは候補にしない）。複数枚組は Disc 1 のシリアル"""
    madb_models = {c for x in madb for c in models_from(x["product_id"])}
    reissue = cfg.get("reissue_serial")
    groups = {}
    for name in cfg["nointro_dats"]:
        for block in C.nointro_dat_text(name).split("game (")[1:]:
            gm = re.search(r'name "([^"]+)"', block)
            if not gm:
                continue
            gname = gm.group(1)
            if not re.search(r"\((?:[^()]*, )?(?:Japan|World)(?:, [^()]*)?\)", gname):
                continue
            tags = re.findall(r"\(([^()]*)\)", gname)
            if any(_DAT_DEMO_TAG.search(t) for t in tags):
                continue
            disc = next((int(t[5:]) for t in tags if re.fullmatch(r"Disc \d+", t)), 1)
            if disc != 1:
                continue
            serials = [m for s_ in re.findall(r'serial "([^"]+)"', block) for m in models_from(s_)]
            if not serials or (reissue and reissue.match(serials[0])):
                continue   # 廉価版（the Best など）の型番帯。通常版の型番ではない
            title = re.sub(r" \([^()]*\)", "", gname)
            plain = all(_DAT_PLAIN_TAG.match(t) for t in tags)
            g = groups.setdefault(title, {})
            g.setdefault(serials[0], {"serials": [], "label": gname, "plain": False})
            g[serials[0]]["serials"] += [x for x in serials if x not in g[serials[0]]["serials"]]
            g[serials[0]]["plain"] |= plain
    entries = []
    for title, g in groups.items():
        cand = dict(g)
        if len(cand) > 1:
            cand = {k: v for k, v in cand.items() if not (set(v["serials"]) & madb_models)} or cand
        if len(cand) > 1:
            cand = {k: v for k, v in cand.items() if v["plain"]} or cand
        if len(cand) != 1:
            continue
        (key, v), = cand.items()
        entries.append({"key": key, "serials": v["serials"], "titles": [title], "date": "", "label": v["label"]})
    return entries


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
    # 照合した MADB の商品が見本盤（価格欄が「SAMPLE」「見本盤」。型番も見本盤のもの〈PS の SCPS-45xxx〉）なら、
    # 同じ発売日・同じ題名で版の印の無い通常版の商品に置き換える（無ければ見本盤のまま。価格は空欄）
    is_sample = lambda x: bool(re.search(r"SAMPLE|見本", str(x.get("price") or ""), re.I))
    taken = {v[0]["key"] for v in m_madb.values() if v[0]}
    for i, (md0, sc0, how0) in list(m_madb.items()):
        if not md0 or how0 == "manual" or not is_sample(md0):
            continue
        same = [x for x in madb if x["key"] not in taken and x["date"] == md0["date"] and not is_sample(x)
                and C.norm(x["label"]) == C.norm(md0["label"]) and not C.VARIANT.search(x["label"])]
        if len(same) == 1:
            m_madb[i] = (same[0], sc0, how0)
            taken.add(same[0]["key"])
            rows[i]["_sample_swap"] = md0["key"]
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
        wiki_codes = models_from(r.get("wiki_model", ""))   # Wikipedia の表に品番の列がある機種（プレイディア）
        model = ov.get("model_number") or (mame_codes or madb_codes or wiki_codes or [""])[0]
        srcs = []
        if ov.get("model_number"):
            srcs.append("manual")
        if model and model in wiki_codes:
            srcs.append("Wikipedia")
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
        if r.get("_sample_swap"):
            issues.append(f"MADBの見本盤（{r['_sample_swap']}）を同じ題名の通常版に置き換え")
        for name, src, how in (("MADB", md, md_how), ("MAME", mm, mm_how)):
            if how == "date_only":
                issues.append(f"{name}同日1件のみで照合（{src['label']}）")
            elif how == "date_hint":
                issues.append(f"{name}同日1件のみ・題名の手がかりで照合（{src['label']}）")
        if not md and md_how != "manual" and cfg["madb_platforms"] and not cfg.get("madb_partial"):
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

    if cfg.get("gametdb_models"):
        # GameTDB（PS3 は ps3tdb）の日本版で、日本語の題名が完全に一致し、ほかに候補の無いものの ID を型番にする
        import zipfile
        with zipfile.ZipFile(C.CACHE / "gametdb" / f"{cfg['gametdb_models']}.zip") as z:
            text = z.read(z.namelist()[0]).decode("utf-8", "replace")
        by_title = {}
        for g in re.findall(r"<game name=.*?</game>", text, re.S):
            gid = re.search(r"<id>([^<]+)</id>", g)
            ja = re.search(r'<locale lang="JA">\s*<title>([^<]+)</title>', g)
            if "<region>NTSC-J" not in g or not gid or not ja:
                continue
            for c in cfg["models_from_serial"](gid.group(1)):
                if cfg.get("reissue_serial") and cfg["reissue_serial"].match(c):
                    continue   # 廉価版の型番帯
                by_title.setdefault(C.norm(ja.group(1)), {})[c] = ja.group(1)
        used_models = {r["model_number"] for r in rows if r["model_number"]}
        n = 0
        for r in rows:
            cand = {k: v for k, v in by_title.get(C.norm(r["title"]), {}).items() if k not in used_models}
            if r["model_number"] or len(cand) != 1:
                continue
            (code, ja_title), = cand.items()
            r["model_number"] = code
            r["_model_srcs"].append("GameTDB")
            used_models.add(code)
            n += 1
        print(f"GameTDB の題名から型番 {n} 件を補完", file=sys.stderr)

    if cfg.get("dat_title_models"):
        # MADB・MAME で型番が決まらない行を、DAT（Redump）の題名とシリアルで補う（PS・PS2・PS3・PSP・DC・3DO）。DAT に発売日は無いので
        # psxdatacenter の PS2 と同じく、ローマ字にした題名がとても似ていてほかに候補の無いものだけを採る
        import psxdc
        entries = dat_title_entries(cfg, models_from, madb)
        used_models = {r["model_number"] for r in rows if r["model_number"]}
        no_model = [r for r in rows if not r["model_number"]]
        m_dt = psxdc.match(no_model, entries, used_models, by_date=False,
                           strict_sim=cfg.get("dat_title_sim", 0.85))   # 機種ごとに調整（PSP は 0.75 でも誤りが無かった）
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
                gm = re.search(r'name "([^"]+)"', block)
                if not gm:
                    continue   # 題名に 'game (' を含むものの区切り違いなど
                gname = gm.group(1)
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

    tdb = {}
    if cfg.get("cero") and cfg["cero"].get("gametdb"):
        import cero as CR
        tdb = CR.load_gametdb(cfg["cero"]["gametdb"])
    official = []
    if cfg.get("cero") and cfg["cero"].get("official"):
        import cero as CR
        official = CR.load_official(cfg["cero"]["official"])
    m_maru = C.match_maru(rows, maru, overrides, cfg.get("code_of") if cfg.get("ref_code_models") else None,
                          cfg.get("maru_date_only", False)) if maru is not None else {}
    report = []
    note_rows = []
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
        if model and nointro and key(model) not in keys(nointro) and not ov.get("model_number"):
            # 出典どうしで型番が食い違い、採った型番は DAT（No-Intro・Redump）に無く、ほかの出典の 1 つだけが DAT にある
            # → DAT にある方を採る（MADB の誤記〈A02J と AO2J など〉で吸い出しが結びつかない・別作品に結びつくのを防ぐ）
            others = []
            mame_regular = ", ".join(x for x in re.split(r",(?![^()]*\))", mm["serial"] if mm else "") if not _EDITION_NOTE.search(x))
            for c in ((models_from(mame_regular) if mm else []) + (models_from(md["product_id"]) if md else [])
                      + ([ma["model"]] if ma and ma["model"] else [])):
                if c != model and key(c) in keys(nointro) and c not in others:
                    others.append(c)
            if len(others) == 1:
                issues.append(f"型番をDATにあるもの（{others[0]}）に置換（元 {model}）")
                model = others[0]
                srcs[:] = [s_ for s_, ok in (("MAME", mm and key(model) in keys(models_from(mm["serial"]))),
                                             ("MADB", md and key(model) in keys(models_from(md["product_id"])))) if ok]
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
        price_note = "オープン価格" if md and not yen and "オープン価格" in str(md["price"] or "") else ""
        my, mt = (ma["yen"], ma["tax"]) if ma and ma["yen"] else ("", "")
        if ov.get("price_yen") == "-":   # 照合した MADB の価格が限定版などのもの → 価格を採らない（照合・型番は残す）
            yen, tax, price_src, package = "", "", "", ""
        elif ov.get("price_yen"):
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

        import cero as CR
        if cfg.get("cero") and date >= CR.CERO_START:
            val, descs, src = "", [], ""
            got = CR.from_madb(md["rating"]) if md else set()
            if len(got) == 1:
                val, descs, src = got.pop(), CR.descriptors_madb(md["rating_desc"]), "MADB"
            elif len(got) > 1:
                issues.append(f"CERO区分が複数 MADB={'/'.join(sorted(got))}")
            off = CR.official_lookup(official, r["title"], C.sim, date=date) if official else None
            if off and off[0] == "conflict":
                issues.append(f"CERO公式で区分が食い違い {'/'.join(off[1])}")
                off = None
            if off and val and off[0] != val:
                if CR.same_level(off[0], val):   # 公式は審査時の旧区分、MADB は新区分に書き換えたもの
                    val, descs, src = off[0], off[1] or descs, "CERO公式（MADB は新区分の表記）"
                elif not CR.same_level(val, off[0]) and off[3] >= 1.0:
                    # 題名が完全に一致する CERO 公式の審査タイトルは、審査をした機関の記録として公式を採る（合意済み）
                    issues.append(f"CERO公式を採用 MADB={val} CERO公式={off[0]}")
                    src = f"CERO公式（MADB は {val}）"
                    val, descs = off[0], off[1]
                elif not CR.same_level(val, off[0]):
                    issues.append(f"CERO不一致 MADB={val} CERO公式={off[0]}（{off[2]}）")
            if not val and off:
                val, descs, src = off[0], off[1], "CERO公式"
            if not val and date >= CR.NEW_SYSTEM_FROM and tdb:
                hit = CR.gametdb_lookup(tdb, cfg["cero"]["gametdb_key"](model))
                if hit:
                    val, descs, src = hit[0], hit[1], "GameTDB"
            if not val:
                pool = {v for x in madb if x is not md and x["rating"] and max(C.sim(r["title"], t) for t in x["titles"]) >= 0.85
                        for v in CR.from_madb(x["rating"])}
                if len(pool) == 1:
                    val, src = pool.pop(), "MADB（別の版）"
                elif len(pool) > 1:
                    issues.append(f"CERO区分が別の版で食い違い {'/'.join(sorted(pool))}")
            if val and md and src == "MADB" and tdb and date >= CR.NEW_SYSTEM_FROM:
                hit = CR.gametdb_lookup(tdb, cfg["cero"]["gametdb_key"](model))
                if hit and hit[0] != val:
                    issues.append(f"CERO不一致 MADB={val} GameTDB={hit[0]}")
            desc_src = src.split("（")[0] if descs else ""
            if val and not descs and off and off[0] == val and off[1]:
                # MADB などで区分を採ったがアイコンの記録が無い → 区分が同じ CERO 公式の審査タイトルのアイコン（合意済み）
                descs, desc_src = off[1], "CERO公式"
            if val in ("A", "B", "C", "D", "Z") and date < CR.NEW_SYSTEM_FROM:
                src += "（新区分の表記。再販時の区分とみられる）"   # 新区分は 2006年3月から
            r.update({"cero": val, "cero_descriptors": ";".join(descs) if val else "", "cero_source": src,
                      "cero_descriptors_source": desc_src if val else ""})
        for col, fn in cfg.get("derive", {}).items():  # 型番などから決まる列（DS の compat）
            r[col] = fn({**r, "model_number": model})
        for col in cfg.get("extra_columns", []):   # 手動補正（SG-1000 のマイカード再販の型番など）
            if ov.get(col):
                r[col] = ov[col]
        r.update({
            "release_date": date, "release_date_sources": "+".join(dsrc),
            "model_number": model, "model_number_source": "+".join(srcs),
            "price_yen": yen, "price_tax": tax, "price_source": price_src,
            "price_note": price_note if not yen else "",
            # 価格の根拠になったMADBのパッケージ名（限定版・セット品等の場合に判別できるように）
            "price_package": package if price_src.startswith("MADB") else "",
            "maru_code": ma["key"] if ma else "",
        })
        # 要確認と注記に分ける。注記は値の決め方の記録（確認済みの照合方法など）で review/match_notes.csv へ。
        # 低スコアの照合も、型番が 2 つ以上の出典で一致し発売日も一致するなら裏付けありとして注記に回す
        srcs_set = set(srcs) - {"manual"}
        notes = []
        for i in list(issues):
            backed = (i.startswith("MADB低スコア") and "MADB" in srcs_set and len(srcs_set) >= 2 and "MADB" in dsrc) or \
                     (i.startswith("MAME低スコア") and "MAME" in srcs_set and len(srcs_set) >= 2 and "MAME" in dsrc)
            if backed or NOTE_RE.search(i):
                issues.remove(i)
                notes.append(i + ("（型番・発売日が他の出典と一致）" if backed else ""))
        for target, items in ((report, issues), (note_rows, notes)):
            if not items:
                continue
            rep = {
                "release_date": r["release_date"], "title": r["title"], "issues": "; ".join(items),
                "madb_id": md["key"] if md else "", "madb_title": md["label"] if md else "",
                "madb_date": md["date"] if md else "",
                "mame_name": mm["key"] if mm else "", "mame_title": mm["label"] if mm else "",
                "mame_date": mm["date"] if mm else "",
            }
            if maru is not None:
                rep.update({"maru_code": ma["key"] if ma else "", "maru_title": ma["label"] if ma else "",
                            "maru_date": ma["date"] if ma else ""})
            target.append(rep)

    for n, r in enumerate(rows, 1):
        r["id"] = f"{cfg['id_prefix']}-{n:04d}"
    extra = [c for c in cfg.get("extra_columns", [])] + (["cero", "cero_descriptors", "cero_source", "cero_descriptors_source"] if cfg.get("cero") else [])
    fields = BASE_FIELDS[:4] + extra + BASE_FIELDS[4:] + (["maru_code"] if maru is not None else [])
    C.write_csv(data / "jp_titles.csv", rows, fields)
    C.write_csv(data / "review" / "match_report.csv", report)
    C.write_csv(data / "review" / "match_notes.csv", note_rows)
    if cfg.get("dat_title_link"):
        C.write_csv(data / "review" / "dat_title_matches.csv",
                    [{"dump_name": n, "title_id": r["id"], "title": r["title"], "dat_title": e["label"], "score": f"{sc:.2f}"}
                     for r, e, sc in dat_links for n in e["names"]])
    print(f"{len(rows)} 件: 型番 {sum(bool(r['model_number']) for r in rows)} / "
          f"価格 {sum(bool(r['price_yen']) for r in rows)} / 要確認 {len(report)}", file=sys.stderr)


if __name__ == "__main__":
    main()
