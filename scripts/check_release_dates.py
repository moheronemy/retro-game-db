#!/usr/bin/env python3
"""発売日の食い違い（要確認レポートの「発売日不一致」）を、作品ごとの ja.wikipedia の記事の基本情報欄（発売日）と照らし合わせる。

一覧の表（Wikipedia のゲームタイトル一覧）の日付と、MADB・MAME・maru-chang の日付が違う行について、記事の基本情報欄の「発売日」に
どちらの日付が書かれているかを見る（記事は scripts/fetch_wikipedia_articles.py で .cache/wikipedia/articles/ に取得しておく）。
記事は複数の機種の発売日を並べて書くことが多いので、欄に出てくる日付をすべて拾い、機種は区別しない。

判定:
  記事は他の出典と同じ   記事に他の出典の日付があり、一覧の日付が無い。かつ他の出典（2 つ以上ならすべて）が同じ日付。
                         記事名が行の題名と似ている（0.5 以上。リンク先がシリーズや別作品の記事のものは除く）
                         → 一覧の表の誤りとみて overrides/matches.csv の release_date_fix で直す候補
  記事は一覧と同じ       記事に一覧の日付があり、他の出典の日付が無い → 一覧のまま
  決まらない             どちらも無い・両方ある・記事が無い

出力: review/release_date_check.csv（機種ごと）と、全体の集計（標準エラー）
使い方:
  python3 scripts/check_release_dates.py --list-articles .cache/release_date_articles.txt   # 要る記事名の一覧
  python3 scripts/fetch_wikipedia_articles.py .cache/release_date_articles.txt              # 記事を取得（2 秒間隔）
  python3 scripts/check_release_dates.py             # 判定だけ
  python3 scripts/check_release_dates.py --apply     # 「記事は他の出典と同じ」を overrides/matches.csv に書く
"""
import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import common as C
from fetch_wikipedia_articles import path_of

DATE_RE = re.compile(r"(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日")


def infobox_dates(text):
    """記事の先頭の基本情報欄の「発売日」（Template:コンピュータゲーム では Date）に出てくる日付（YYYY-MM-DD）の集合。"""
    ms = re.findall(r"^\s*\|\s*(?:発売日|Date|date|発売)\s*=(.*?)(?=^\s*\|\s*[^=|\n]{1,20}?\s*=|^\s*\}\})", text, re.M | re.S)
    if not ms:
        return None
    v = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", "\n".join(ms))   # 基本情報欄が複数ある記事（シリーズの記事）はすべて
    v = re.sub(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>", "", v, flags=re.S)
    dates = {f"{y}-{int(mo):02d}-{int(d):02d}" for y, mo, d in DATE_RE.findall(v)}
    for y, mo, d in re.findall(r"\{\{\s*(?:vgrelease|Vgrelease|start date|Start date)[^}]*?(\d{4})\|(\d{1,2})\|(\d{1,2})", v):
        dates.add(f"{y}-{int(mo):02d}-{int(d):02d}")
    dates |= set(re.findall(r"\b(\d{4}-\d\d-\d\d)\b", v))
    return dates


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--list-articles", metavar="FILE", help="照らし合わせに要る記事名の一覧を書き出すだけ（fetch_wikipedia_articles.py の入力）")
    a = ap.parse_args()
    reports = sorted(C.ROOT.glob("data/*/review/match_report.csv")) + sorted(C.ROOT.glob("data/*/*/review/match_report.csv"))
    total = Counter()
    fixes = defaultdict(list)
    needed = set()
    for rep in reports:
        d = rep.parent.parent
        titles = {(r["release_date"], r["title"]): r for r in C.read_csv(d / "jp_titles.csv")}
        out = []
        for r in C.read_csv(rep):
            others = re.findall(r"発売日不一致 (\S+?)=([\d-]+)", r.get("issues", ""))
            row = titles.get((r.get("release_date"), r.get("title")))
            if not others or not row:
                continue
            art = row.get("wikipedia_article", "").split("#")[0].replace("_", " ").strip()
            if art:
                needed.add(art)
            vals = {v for _, v in others}
            supporters = [x for x in row.get("release_date_sources", "").split("+") if x not in ("", "Wikipedia", "manual")]
            text = path_of(art).read_text(encoding="utf-8") if art and path_of(art).exists() else None
            dates = infobox_dates(text) if text else None
            if text is None:
                verdict = "決まらない（記事なし）"
            elif dates is None:
                verdict = "決まらない（基本情報欄に発売日なし）"
            else:
                has_list, has_other = row["release_date"] in dates, bool(vals & dates)
                same_work = C.sim(row["title"], re.sub(r"\s*\(.*?\)$", "", art)) >= 0.5
                if has_other and not has_list and len(vals) == 1 and not same_work:
                    verdict = "決まらない（記事は別の作品・シリーズの記事）"
                elif has_other and not has_list and len(vals) == 1 and supporters:
                    verdict = "決まらない（一覧の日付と一致する出典もある）"
                elif has_other and not has_list and len(vals) == 1:
                    verdict = "記事は他の出典と同じ"
                elif has_list and not has_other:
                    verdict = "記事は一覧と同じ"
                else:
                    verdict = "決まらない（両方ある）" if has_list and has_other else "決まらない（どちらも無い）"
            total[verdict] += 1
            out.append({"id": row["id"], "title": row["title"], "list_date": row["release_date"],
                        "other_dates": "; ".join(f"{n}={v}" for n, v in others),
                        "article": art, "article_dates": " ".join(sorted(dates)) if dates else "", "verdict": verdict})
            if verdict == "記事は他の出典と同じ":
                fixes[d].append((row, vals.pop(), [n for n, _ in others], art))
        if out and not a.list_articles:
            C.write_csv(d / "review" / "release_date_check.csv", out)
    if a.list_articles:
        Path(a.list_articles).write_text("\n".join(sorted(needed)) + "\n", encoding="utf-8")
        print(f"記事 {len(needed)} 件を {a.list_articles} に書いた", file=sys.stderr)
        return
    for k, v in total.most_common():
        print(f"{k}: {v}", file=sys.stderr)
    if not a.apply:
        return
    n = 0
    for d, items in fixes.items():
        path = d / "overrides" / "matches.csv"
        rows = C.read_csv(path) if path.exists() else []
        fields = list(rows[0].keys()) if rows else ["release_date", "title", "madb_id", "mame_name", "maru_code", "model_number",
                                                    "price_yen", "price_tax", "release_date_fix", "comment"]
        for col in ("release_date_fix", "comment"):
            if col not in fields:
                fields.append(col)
        index = {(o["release_date"], o["title"]): o for o in rows}
        for row, new, names, art in items:
            key = (row["release_date"], row["title"])
            o = index.get(key)
            if o is None:
                o = {f: "" for f in fields}
                o.update({"release_date": row["release_date"], "title": row["title"]})
                rows.append(o)
                index[key] = o
            if o.get("release_date_fix"):
                continue
            o["release_date_fix"] = new
            note = f"発売日: 一覧の表は {row['release_date']}。{'・'.join(names)} と記事「{art}」の基本情報欄は {new}"
            o["comment"] = f"{o['comment']}。{note}" if o.get("comment") else note
            n += 1
        path.parent.mkdir(parents=True, exist_ok=True)
        eol = "\r\n" if path.exists() and b"\r\n" in path.read_bytes()[:2000] else "\n"   # 元のファイルの改行のまま
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator=eol)
            w.writeheader()
            w.writerows(rows)
    print(f"overrides/matches.csv に {n} 件の release_date_fix を書いた", file=sys.stderr)


if __name__ == "__main__":
    main()
