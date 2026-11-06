"""psxdatacenter.com の日本版データ（scripts/fetch_psxdatacenter.py で .cache/ に保存したもの）で、
MADB・MAME で型番が決まらなかったタイトルの型番を補う。

psxdatacenter には日本語の題名が無い（ローマ字・英語の題名だけ）ので、Wikipedia の日本語の題名を pykakasi で
ローマ字にして似ているものを探す。
  PS1: 作品別ページの発売日が同じものの中から、題名が十分似ているものを採る（貪欲法・重複なし）。
       date_fallback=True のときだけ、残った行と候補が同じ発売日にちょうど1件ずつなら題名が似ていなくても組にする。
       PS1 で試すと約半数が別作品だった（発売日の誤りや一覧に無い作品のため）ので、既定では使わない。
  PS2: 発売日が無いので、題名がとても似ていて、候補がほかに無い（2番目と差がある）ものだけを採る。
"""
import datetime
import difflib
import html
import re
import unicodedata

import common as C

DIR = C.CACHE / "psxdatacenter"
_KAKASI = None


def _kakasi():
    global _KAKASI
    if _KAKASI is None:
        import pykakasi   # pip install pykakasi
        _KAKASI = pykakasi.kakasi()
    return _KAKASI


def norm_roman(s):
    """ローマ字表記のゆれ（長音の ou/oo/uu、記号・空白・大文字小文字）をならす。"""
    s = unicodedata.normalize("NFKC", s or "").lower()
    s = re.sub(r"[^a-z0-9]", "", s)
    for a, b in (("ou", "o"), ("oo", "o"), ("uu", "u"), ("aa", "a"), ("ii", "i"), ("ee", "e"), ("ei", "e")):
        s = s.replace(a, b)
    return s


def romaji(title, strip_series=False):
    if strip_series:
        title = _SERIES_JA.sub(" ", unicodedata.normalize("NFKC", title or ""))
    return norm_roman(" ".join(x["hepburn"] for x in _kakasi().convert(title or "")))


def _text(fragment):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment))).strip()


def load_ps1(models_from):
    """PS1 の作品別ページ → [{serials, titles, date, publisher, key}]。"""
    out = []
    for path in sorted((DIR / "ps1").glob("*.html")):
        t = _text(path.read_text(encoding="utf-8", errors="replace"))
        get = lambda label, nxt: (re.search(re.escape(label) + r"\s+(.*?)\s+" + nxt, t) or [None, ""])[1].strip()
        official = get("Official Title", "Common Title")
        common = get("Common Title", "Serial Number")
        serials = models_from(get("Serial Number(s)", "Region"))
        date_s = get("Date Released", "Disc Number")
        try:
            date = datetime.datetime.strptime(date_s, "%d %B %Y").strftime("%Y-%m-%d")
        except ValueError:
            date = ""
        if serials:
            out.append({"key": serials[0], "serials": serials, "titles": [official, common],
                        "date": date, "publisher": get("Publisher", "Date Released"), "label": official})
    return out


def load_ps2(models_from):
    """PS2 の一覧 → [{serials, titles, key}]（発売日は無い）。廉価版（the Best など）の行は除く。"""
    text = (DIR / "jlist2.html").read_text(encoding="utf-8", errors="replace")
    out = []
    for row in re.findall(r"<tr>(.*?)</tr>", text, re.S):
        cells = re.findall(r'<td class="col(\d)"[^>]*>(.*?)</td>', row, re.S)
        c = {k: v for k, v in cells}
        serials = models_from(_text(c.get("2", "").replace("<br>", " ")))
        title = _text(c.get("3", ""))
        if serials and title and not re.search(r"the best|best collection|\(reprint\)", title, re.I):
            out.append({"key": serials[0], "serials": serials, "titles": [title], "date": "", "label": title})
    return out


# 廉価版・シリーズの名前。両側から除いてから比べる（共通の長いシリーズ名だけで似ていると判定されるのを防ぐ）
_SERIES_JA = re.compile(r"(SIMPLE ?(1500|2000)?(実用)?|SIMPLEキャラクター ?2000|SuperLite ?(1500|GOLD|3 ?in ?1)?|Major ?Wave ?(1500)?|"
                        r"NICE PRICE|PANDORA MAX|スーパープライス|ファミリー ?1500|パーコン|森田思考搭載|value ?1500|"
                        r")シリーズ|山佐Digiガイド|キッズステーション|SuperLite|Major ?Wave ?1500|PANDORA MAX SERIES", re.I)
_SERIES_EN = re.compile(r"\[[^\]]*\]|\([^)]*\)|simple (characters )?(1500|2000) series|superlite (1500|gold|3 in 1)( series)?|"
                        r"major wave( 1500)?( series)?|nice price( series)?|pandora max series|super price series|"
                        r"family 1500 series|yamasa digi guide|kids station", re.I)
_VOL = re.compile(r"vol\.? ?0*(\d+)", re.I)


def _vol(s):
    m = _VOL.search(unicodedata.normalize("NFKC", s or ""))
    return int(m.group(1)) if m else None


def _ratio(a, b, floor):
    m = difflib.SequenceMatcher(None, a, b)
    if m.real_quick_ratio() < floor or m.quick_ratio() < floor:
        return 0.0
    return m.ratio()


def _score(row, entry, core_min=0.5):
    """row: (題名のローマ字, シリーズ名を除いたローマ字, 巻数)。題名全体で比べた似ている度合いを返す。
    ただしシリーズ物（題名にシリーズ名がある行）は、シリーズ名を除いた部分どうしも core_min 以上似ていることを求める。
    巻数がどちらにもあって違うものは採らない。"""
    full, core, vol = row
    best = 0.0
    for t in entry["titles"]:
        if not t or not full:
            continue
        if vol is not None and _vol(t) is not None and _vol(t) != vol:
            continue
        sc = _ratio(full, norm_roman(re.sub(r"\([^)]*\)", "", t)), best)
        if sc <= best:
            continue
        if core != full and _ratio(core, norm_roman(_SERIES_EN.sub(" ", t)), 0) < core_min:
            continue
        best = sc
    return best


def _row_key(title):
    return romaji(title), romaji(title, True), _vol(title)


def match(rows, entries, used_models, by_date=True, min_sim=0.5, strict_sim=0.85, date_fallback=False):
    """型番の無い行（rows: _i・title・release_date）に entries の1件を割り当てる。
    戻り値: {行の _i: (entry, score, how)}。how は 'title' か 'date_only'。"""
    free = [e for e in entries if not (set(e["serials"]) & used_models)]
    result, used = {}, set()
    if by_date:
        by = {}
        for e in free:
            by.setdefault(e["date"], []).append(e)
        pairs = []
        for r in rows:
            rk = _row_key(r["title"])
            for e in by.get(r["release_date"], []):
                sc = _score(rk, e)
                if sc >= min_sim:
                    pairs.append((sc, r["_i"], e["key"], e))
        pairs.sort(key=lambda p: -p[0])
        for sc, i, k, e in pairs:
            if i in result or k in used:
                continue
            result[i] = (e, sc, "title")
            used.add(k)
        left_rows, left_e = {}, {}
        for r in rows:
            if r["_i"] not in result:
                left_rows.setdefault(r["release_date"], []).append(r)
        for e in free:
            if e["key"] not in used:
                left_e.setdefault(e["date"], []).append(e)
        for d, rs in left_rows.items():
            if date_fallback and len(rs) == 1 and len(left_e.get(d, [])) == 1:
                result[rs[0]["_i"]] = (left_e[d][0], 0.0, "date_only")
        return result
    # 発売日が無い（PS2）: 1位が十分似ていて 2位と差があり、その候補にとっても1位の行であるものだけ
    best_for_row, best_for_entry = {}, {}
    romans = {r["_i"]: _row_key(r["title"]) for r in rows}
    grams = lambda x: {x[i:i + 3] for i in range(max(1, len(x) - 2))}
    index = {}   # 3文字の断片 → その断片を題名に含む候補（総当たりを避けるため）
    for n, e in enumerate(free):
        for t in e["titles"]:
            for g in grams(norm_roman(re.sub(r"\([^)]*\)", "", t))):
                index.setdefault(g, set()).add(n)
    for r in rows:
        counts = {}
        for g in grams(romans[r["_i"]][0]):
            for n in index.get(g, ()):
                counts[n] = counts.get(n, 0) + 1
        cands = [free[n] for n, _ in sorted(counts.items(), key=lambda x: -x[1])[:40]]
        scored = sorted(((_score(romans[r["_i"]], e), e) for e in cands), key=lambda x: -x[0])[:2]
        if not scored or scored[0][0] < strict_sim:
            continue
        if len(scored) > 1 and scored[1][0] > scored[0][0] - 0.1:
            continue
        sc, e = scored[0]
        best_for_row[r["_i"]] = (e, sc)
        if sc > best_for_entry.get(e["key"], (None, 0))[1]:
            best_for_entry[e["key"]] = (r["_i"], sc)
    for i, (e, sc) in best_for_row.items():
        if best_for_entry[e["key"]][0] == i:
            result[i] = (e, sc, "title")
    return result
