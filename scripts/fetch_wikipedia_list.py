#!/usr/bin/env python3
"""日本語版Wikipediaの「〇〇のゲームタイトル一覧」から国内発売タイトルを抽出してCSVに書き出す。

どのページのどの表を読むか、表の列の並びは scripts/platforms.py の "wikipedia" に書く。

使い方:
    python3 scripts/fetch_wikipedia_list.py gba
    python3 scripts/fetch_wikipedia_list.py gba --wikitext saved.wiki  # 保存済みwikitextから再生成（1ページの機種のみ）
"""
import argparse
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import platforms as P

API = "https://ja.wikipedia.org/w/api.php"
UA = "retro-game-db/0.1 (https://github.com/moheronemy/retro-game-db)"


def fetch_wikitext(page):
    q = urllib.parse.urlencode({
        "action": "parse", "page": page, "prop": "wikitext|revid",
        "format": "json", "redirects": 1,
    })
    req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": UA})
    for wait in (2, 4, 8, 16, None):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.load(r)["parse"]
            break
        except urllib.error.HTTPError as e:
            if e.code != 429 or wait is None:
                raise
            print(f"HTTP 429, retry in {wait}s", file=sys.stderr)
            time.sleep(wait)
    return d["wikitext"]["*"], d.get("revid")


def section(wikitext, name):
    m = re.search(rf"^==\s*{re.escape(name)}\s*==\s*$", wikitext, re.M)
    if not m:
        raise SystemExit(f"section not found: {name}")
    rest = wikitext[m.end():]
    n = re.search(r"^==[^=].*==\s*$", rest, re.M)
    return rest[: n.start()] if n else rest


def split_cells(line):
    """'||' でセルを分割する。[[...]] / {{...}} / <ref>...</ref> 内は無視。"""
    cells, buf, i, depth_l, depth_t, in_ref = [], [], 0, 0, 0, False
    while i < len(line):
        two = line[i:i + 2]
        if line.startswith("<ref", i) and not re.match(r"<ref[^>]*/>", line[i:]):
            in_ref = True
        elif line.startswith("</ref>", i):
            in_ref = False
        if two == "[[":
            depth_l += 1; buf.append(two); i += 2; continue
        if two == "]]" and depth_l:
            depth_l -= 1; buf.append(two); i += 2; continue
        if two == "{{":
            depth_t += 1; buf.append(two); i += 2; continue
        if two == "}}" and depth_t:
            depth_t -= 1; buf.append(two); i += 2; continue
        if two == "||" and not (depth_l or depth_t or in_ref):
            cells.append("".join(buf)); buf = []; i += 2; continue
        buf.append(line[i]); i += 1
    cells.append("".join(buf))
    return cells


def strip_refs(s):
    s = re.sub(r"<ref[^>]*/>", "", s)
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    return s


def strip_templates(s):
    # {{R|..}} {{Sfn|..}} {{efn|..}} など脚注系テンプレートを除去（ネスト対応）
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    return s


def link_target(s):
    m = re.search(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]", s)
    return m.group(1).strip() if m else ""


def plain(s):
    s = strip_templates(strip_refs(s))
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"'{2,}", "", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_date(s):
    m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", s)
    if m:
        return "%s-%02d-%02d" % (m.group(1), int(m.group(2)), int(m.group(3)))
    m = re.search(r"(\d{4})年(\d{1,2})月", s)
    if m:
        return "%s-%02d" % (m.group(1), int(m.group(2)))
    return ""


def first_line(s):
    """「日本題<br />英題」や {{ubl|日本題|英題}} の先頭（日本の表記）を取り出す。"""
    m = re.match(r"\s*\{\{\s*ubl\s*\|([^|}]*)", s, re.I)
    if m:
        return m.group(1)
    return re.split(r"<br\s*/?>", s)[0]


def interlang(s):
    """{{仮リンク|日本語名|en|英語名}} を [[日本語名]] にする（脚注テンプレート除去で消えないように）。"""
    return re.sub(r"\{\{\s*仮リンク\s*\|([^|}]*)\|[^}]*\}\}", r"[[\1]]", s)


def table_text(text, table_id):
    """id 指定の表だけを取り出す（無指定なら text 全体）。"""
    if not table_id:
        return text
    i = text.index(f'id="{table_id}"')
    i = text.rindex("{|", 0, i)
    j = text.index("\n|}", i)
    return text[i:j + 3]


def parse_rows(text, columns=("jp", "title", "publisher", "notes"), extra=None):
    """表の各行を読む。columns は先頭からの列の意味（jp=日本の発売日）。日本未発売の行は除く。"""
    rows = []
    in_table = False
    regional = "na" in columns
    for block in re.split(r"^\|-.*$", text, flags=re.M):
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
            elif lines:  # セル内改行の継続行
                lines[-1] += "\n" + ln
        if not lines:
            continue
        cells = []
        for ln in lines:
            cells.extend(split_cells(ln))
        if len(cells) < 3:
            print("skip:", cells, file=sys.stderr)
            continue
        c = dict(zip(columns, cells))
        date_raw = re.sub(r"<span[^>]*></span>", "", c.get("jp", ""))
        date = parse_date(plain(date_raw))
        if regional and not date:
            continue  # 日本未発売（{{Unreleased}}）
        title_raw, pub_raw = c.get("title", ""), c.get("publisher", "")
        if regional:
            title_raw, pub_raw = first_line(interlang(title_raw)), first_line(pub_raw)
        row = {
            "release_date": date,
            "title": plain(title_raw),
            "publisher": plain(pub_raw),
            "notes": plain(c.get("notes", "")),
            "wikipedia_article": link_target(title_raw),
        }
        if "sgb" in columns:
            row["sgb"] = "yes" if re.search(r"[○◯〇]", c.get("sgb", "")) else ""
        row.update(extra or {})
        rows.append(row)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("platform")
    ap.add_argument("--wikitext", help="保存済みwikitextファイルを使う（1ページの機種のみ）")
    ap.add_argument("--out")
    a = ap.parse_args()
    cfg = P.get(a.platform)
    wcfg = cfg["wikipedia"]
    pages = {t.get("page", wcfg.get("page")) for t in wcfg["tables"]}
    texts = {}
    for page in sorted(pages):
        if a.wikitext:
            texts[page], rev = Path(a.wikitext).read_text(encoding="utf-8"), None
        else:
            texts[page], rev = fetch_wikitext(page)
            time.sleep(3)
        print(f"{page}: revid={rev}", file=sys.stderr)
    rows = []
    for t in wcfg["tables"]:
        page = t.get("page", wcfg.get("page"))
        text = table_text(section(texts[page], t["section"]), t.get("table_id"))
        got = parse_rows(text, t.get("columns", ("jp", "title", "publisher", "notes")), t.get("extra"))
        print(f"  {t['section']}: {len(got)} 行", file=sys.stderr)
        rows += got
    if len(wcfg["tables"]) > 1:
        rows.sort(key=lambda r: r["release_date"])  # 複数の表をまとめるときは発売日順（同日は表の順）
    for i, r in enumerate(rows, 1):
        r["id"] = f"{cfg['id_prefix']}-{i:04d}"
    out = Path(a.out) if a.out else cfg["dir"] / "wikipedia_titles.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = ["id", "release_date", "title", "publisher", "notes", "wikipedia_article"] + \
        [k for k in (rows[0] if rows else {}) if k not in ("id", "release_date", "title", "publisher", "notes",
                                                         "wikipedia_article")]
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows -> {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
