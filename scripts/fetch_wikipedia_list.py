#!/usr/bin/env python3
"""日本語版Wikipediaの「〇〇のゲームタイトル一覧」から国内発売タイトルを抽出してCSVに書き出す。

どのページのどの表を読むか、表の列の並びは scripts/platforms.py の "wikipedia" に書く。

使い方:
    python3 scripts/fetch_wikipedia_list.py gba
    python3 scripts/fetch_wikipedia_list.py gba --wikitext saved.wiki  # 保存済みwikitextから再生成（1ページの機種のみ）
"""
import argparse
import html
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
from common import ROOT

API = "https://ja.wikipedia.org/w/api.php"
UA = "retro-game-db/0.1 (https://github.com/moheronemy/retro-game-db)"


def fetch_wikitext(page):
    """ページ本文（wikitext）を取得する。API はアクセス制限（429）がかかりやすいため action=raw を使う。
    版番号は返らないので "raw" とする。"""
    url = "https://ja.wikipedia.org/w/index.php?" + urllib.parse.urlencode(
        {"title": page, "action": "raw", "redirect": "yes"})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for wait in (30, 90, 180, None):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8"), "raw"
        except urllib.error.HTTPError as e:
            if e.code != 429 or wait is None:
                raise
            print(f"HTTP 429, retry in {wait}s", file=sys.stderr)
            time.sleep(wait)


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


_MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                        "September", "October", "November", "December"], 1)}


def dts(s):
    """{{dts|1988|10|29}}・{{dts|1993|1|14|}}・{{dts|October 29, 1988}} などの日付テンプレートを「1988年10月29日」にする。"""
    def repl(m):
        parts = [p.strip() for p in m.group(1).split("|") if p.strip() and "=" not in p]
        if parts and re.fullmatch(r"\d{4}", parts[0]):
            nums = [int(p) for p in parts[1:3] if p.isdigit()]
            return parts[0] + "年" + "".join(f"{n}{u}" for n, u in zip(nums, ("月", "日")))
        if parts:
            e = re.fullmatch(r"([A-Z][a-z]+)\s+(\d{1,2}),\s*(\d{4})", parts[0])
            if e and e.group(1) in _MONTHS:
                return f"{e.group(3)}年{_MONTHS[e.group(1)]}月{int(e.group(2))}日"
            e = re.fullmatch(r"([A-Z][a-z]+)\s+(\d{4})", parts[0])
            if e and e.group(1) in _MONTHS:
                return f"{e.group(2)}年{_MONTHS[e.group(1)]}月"
        return ""
    return re.sub(r"\{\{\s*dts\s*\|([^{}]*)\}\}", repl, s, flags=re.I)


def parse_date(s, year=None):
    """「2001年3月21日」等を ISO 形式に。year を渡すと年を省いた「1月15日」にも年を補う（DS の年別ページ）。"""
    if year:
        m = re.search(r"^\s*(\d{1,2})月\s*(\d{1,2})日?", s)
        if m and "年" not in s:
            return "%s-%02d-%02d" % (year, int(m.group(1)), int(m.group(2)))
    m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", s)
    if m:
        return "%s-%02d-%02d" % (m.group(1), int(m.group(2)), int(m.group(3)))
    m = re.search(r"(\d{4})年(\d{1,2})月", s)
    if m:
        return "%s-%02d" % (m.group(1), int(m.group(2)))
    m = re.fullmatch(r"\s*(\d{4})年\s*", s)
    if m:
        return m.group(1)
    return ""


def split_top(s, sep="|"):
    """[[...]] / {{...}} の中を無視して sep で分割する。"""
    parts, buf, depth, i = [], [], 0, 0
    while i < len(s):
        two = s[i:i + 2]
        if two in ("[[", "{{"):
            depth += 1; buf.append(two); i += 2; continue
        if two in ("]]", "}}") and depth:
            depth -= 1; buf.append(two); i += 2; continue
        if s[i] == sep and depth == 0:
            parts.append("".join(buf)); buf = []; i += 1; continue
        buf.append(s[i]); i += 1
    parts.append("".join(buf))
    return parts


def first_line(s):
    """「日本題<br />英題」や {{ubl|日本題|英題}} の先頭（日本の表記）を取り出す。"""
    m = re.match(r"\s*\{\{\s*ubl\s*\|", s, re.I)
    if m:
        end = s.rfind("}}")
        args = split_top(s[m.end():end if end > m.end() else len(s)])
        return args[0] if args else ""
    return re.split(r"<br\s*/?>", s)[0]


def title_text(s):
    """タイトル欄の表示文字列。表示名のないリンク [[記事名]] は記事名がそのまま出るため、
    「#節名」と末尾の曖昧さ回避「 (…)」を取り除く（例: [[ボクシング (1990年のゲーム)]] → ボクシング）。"""
    def repl(m):
        target = m.group(1).split("#")[0].strip()
        return re.sub(r"\s+\([^()]*\)$", "", target)
    s = re.sub(r"\[\[([^\]|]+)\]\]", repl, interlang(s))
    return plain(s)


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


KNOWN_COLUMNS = {"jp", "na", "eu", "br", "title", "publisher", "notes", "sgb", "refs"}


def parse_rows(text, columns=("jp", "title", "publisher", "notes"), extra=None, year=None, ref_code=None,
               row_filter=None, derive=None):
    """表の各行を読む。columns は先頭からの列の意味（jp=日本の発売日）。日本未発売の行は除く。"""
    rows = []
    in_table = False
    carry = {}   # 列番号 → (rowspan で続く値, 残り行数)
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
        # 並べ替え用の隠し文字（<span style="display:none">し26</span>）を除く
        cells = [re.sub(r'<span style="display:\s*none;?">[^<]*</span>', "", x) for x in cells]
        # 「卒業 &#12316;Graduation&#12316;」「トージャム&amp;アール」。&lt; &gt; は HTML タグとして消されないよう
        # 私用領域の文字にしておき、最後に < > に戻す（『谷川浩司の将棋指南II &lt;名人への道&gt;』）
        cells = [html.unescape(x.replace("&lt;", "\ue000").replace("&gt;", "\ue001")) for x in cells]
        # rowspan="n" のセルは次の n-1 行の同じ列にも入れる（『ぽけかの』3作の発売元・備考など）
        filled, col = [], 0
        own = list(cells)   # この行に実際に書かれたセル（脚注からのゲームコードはこれだけから拾う）
        queue = list(cells)
        while queue or any(k >= col for k in carry):
            if col in carry:
                val, left = carry[col]
                filled.append(val)
                carry[col] = (val, left - 1)
                if left - 1 <= 0:
                    del carry[col]
            elif queue:
                cell = queue.pop(0)
                m = re.match(r'\s*rowspan="?(\d+)"?[^|\[\]{}]*\|(.*)$', cell, re.S)
                if m:
                    cell = m.group(2)
                    if int(m.group(1)) > 1:
                        carry[col] = (cell, int(m.group(1)) - 1)
                filled.append(cell)
            else:
                break
            col += 1
        cells = filled
        if len(cells) < 3:
            print("skip:", cells, file=sys.stderr)
            continue
        c = dict(zip(columns, cells))
        date_raw = dts(re.sub(r"<span[^>]*></span>", "", c.get("jp", "")))
        date_raw = re.sub(r"\{\{\s*nowrap\s*\|([^{}]*)\}\}", r"\1", date_raw, flags=re.I)
        date_raw = date_raw.lstrip("|")   # 「||2月28日」のような区切りの誤記
        date = parse_date(plain(date_raw), year)
        if regional and not date:
            continue  # 日本未発売（{{Unreleased}}）
        if year and not date:
            print("日付なし:", plain(date_raw)[:30], plain(c.get("title", ""))[:30], file=sys.stderr)
        title_raw, pub_raw = c.get("title", ""), c.get("publisher", "")
        if regional:
            # 元の表に「|||発売元」のような区切りの誤記があるため先頭の「|」を落とす
            title_raw = first_line(interlang(title_raw)).lstrip("|")
            pub_raw = first_line(pub_raw.lstrip("|"))
        row = {
            "release_date": date,
            "title": title_text(title_raw),
            "publisher": plain(pub_raw),
            "notes": plain(c.get("notes", "")),
            "wikipedia_article": link_target(title_raw),
        }
        if "sgb" in columns:
            row["sgb"] = "yes" if re.search(r"[○◯〇]", c.get("sgb", "")) else ""
        for col in columns:  # 表固有の列（DSiウェアの必要ブロック数など）はそのまま文字列で持つ
            if col not in KNOWN_COLUMNS:
                row[col] = plain(c.get(col, ""))
        if ref_code:  # 脚注の公式サイト URL に含まれるゲームコード（例: nintendo.co.jp/ds/software/aifj/）
            m = re.search(ref_code, "||".join(own), re.I)
            row["ref_code"] = m.group(1).upper() if m else ""
        for k, v in row.items():
            if isinstance(v, str):
                row[k] = v.replace("\ue000", "<").replace("\ue001", ">")
        row.update(extra or {})
        if row_filter and not row_filter(row):
            continue
        for col, fn in (derive or {}).items():
            row[col] = fn(row)
        rows.append(row)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("platform")
    ap.add_argument("--wikitext", help="保存済みwikitextファイルを使う（1ページの機種のみ）")
    ap.add_argument("--out")
    ap.add_argument("--refresh", action="store_true", help=".cache/wikipedia/ の保存済み本文を使わず取り直す")
    ap.add_argument("--list", help="本リスト以外の一覧（platforms.py の extra_lists。例: dsiware）")
    a = ap.parse_args()
    cfg = P.get(a.platform)
    wcfg = cfg["wikipedia"] if not a.list else cfg["extra_lists"][a.list]
    pages = {t.get("page", wcfg.get("page")) for t in wcfg["tables"]}
    texts = {}
    for page in sorted(pages):
        if a.wikitext:
            texts[page], rev = Path(a.wikitext).read_text(encoding="utf-8"), None
        else:
            cache = ROOT / ".cache" / "wikipedia" / f"{page}.wiki"
            if cache.exists() and not a.refresh:
                texts[page], rev = cache.read_text(encoding="utf-8"), "cached"
            else:
                texts[page], rev = fetch_wikitext(page)
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(texts[page], encoding="utf-8")
                time.sleep(5)
        print(f"{page}: revid={rev}", file=sys.stderr)
    rows = []
    for t in wcfg["tables"]:
        page = t.get("page", wcfg.get("page"))
        text = table_text(section(texts[page], t["section"]), t.get("table_id"))
        got = parse_rows(text, t.get("columns", ("jp", "title", "publisher", "notes")), t.get("extra"),
                         t.get("year"), wcfg.get("ref_code"), t.get("row_filter"), t.get("derive"))
        print(f"  {t['section']}: {len(got)} 行", file=sys.stderr)
        rows += got
    for r in rows:   # 表の発売日の欄が空・誤っている行の補正（platforms.py の date_fixes。根拠はそこに書く）
        if r["title"] in wcfg.get("date_fixes", {}):
            r["release_date"] = wcfg["date_fixes"][r["title"]]
    if len(wcfg["tables"]) > 1:
        rows.sort(key=lambda r: r["release_date"])  # 複数の表をまとめるときは発売日順（同日は表の順）
    prefix = cfg["id_prefix"] + (f"-{wcfg['id_suffix']}" if a.list else "")
    for i, r in enumerate(rows, 1):
        r["id"] = f"{prefix}-{i:04d}"
    out = Path(a.out) if a.out else cfg["dir"] / (wcfg["out"] if a.list else "wikipedia_titles.csv")
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
