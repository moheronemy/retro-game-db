"""CERO の年齢区分（2002年〜）。

出典の優先順:
  1. MADB で照合した商品の contentRating（「CERO A (全年齢対象)」→ A、旧区分の「CERO 全年齢」→ 全年齢）
  2. GameTDB（Wii・GC: wiitdb、DS: dstdb、PS3: ps3tdb）。新区分（A〜Z）でしか書かれていないので、2006年3月以降の発売分だけに使う
  1'. CERO 公式サイトのタイトル検索（www.cero.biz。DS・PSP・PS3・Wii・Xbox 360）。題名で引く。MADB に区分の無い行を補う。
     MADB が新区分・公式が旧区分で同じ程度のもの（MADB=A・公式=全年齢など）は審査時の表記として公式を採る
  3. 照合した商品に区分が無いとき、同じ題名の MADB の別の商品（the Best・限定版など）。別の商品どうしで食い違わない場合だけ
CERO 以外（ESRB・PEGI、コンピュータソフトウェア倫理機構など）は採らない。
内容アイコン（暴力・セクシャルなど）は MADB の contentRatingDescriptor か GameTDB の descriptor。
"""
import re
import zipfile

import common as C

CERO_START = "2002-10-01"        # 区分の表示の開始（MADB で区分の付いた最も早いソフトも 2002年10月）。これより前の発売分には付けない
NEW_SYSTEM_FROM = "2006-03-01"   # A〜Z の新区分の開始
_OLD = {"全年齢": "全年齢", "12": "12", "15": "15", "18": "18"}
_TDB_DESC = {"violence": "暴力", "sex": "セクシャル", "crime": "犯罪", "love": "恋愛", "horror": "恐怖",
             "drugs": "麻薬", "alcohol/tobacco": "飲酒・喫煙", "gambling": "ギャンブル", "language": "言葉・その他"}


_EQUIV = {"全年齢": {"A"}, "12": {"B"}, "15": {"C"}, "18": {"D", "Z"}}   # 旧区分 → 対応する新区分


def same_level(old, new):
    """旧区分 old と新区分 new が同じ程度の区分か（全年齢≈A、12≈B、15≈C、18≈D/Z）。表記の違いだけのものを見分ける。"""
    return new in _EQUIV.get(old, set())


def from_madb(values):
    """MADB の contentRating（文字列か一覧）→ CERO の区分の値の集合。"""
    vals = set()
    for v in values if isinstance(values, list) else [values]:
        for part in str(v or "").split(","):
            m = re.match(r"\s*CERO\s+([A-DZ])\b", part)
            if m:
                vals.add(m.group(1))
                continue
            m = re.match(r"\s*CERO\s+(全年齢|12|15|18)", part)
            if m:
                vals.add(_OLD[m.group(1)])
    return vals


def descriptors_madb(values):
    out = []
    for v in values if isinstance(values, list) else [values]:
        for part in str(v or "").split(","):
            m = re.match(r"\s*(.+?)\s*\(CERO\)", part)
            if m and m.group(1) not in out:
                out.append(m.group(1))
    return out


def load_gametdb(name):
    """GameTDB の日本版 → {ID: (区分, [内容アイコン])}。区分の無いものは含めない。"""
    path = C.CACHE / "gametdb" / f"{name}.zip"
    if not path.exists():
        return {}
    with zipfile.ZipFile(path) as z:
        text = z.read(z.namelist()[0]).decode("utf-8", "replace")
    out = {}
    for g in re.findall(r"<game name=.*?</game>", text, re.S):
        if "<region>NTSC-J" not in g:
            continue
        gid = re.search(r"<id>([^<]+)</id>", g)
        rating = re.search(r'<rating type="CERO" value="([A-DZ])"\s*/?>(.*?)(?:</rating>|$)', g, re.S)
        if gid and rating:
            descs = [_TDB_DESC.get(d, d) for d in re.findall(r"<descriptor>([^<]+)</descriptor>", rating.group(2))]
            out[gid.group(1)] = (rating.group(1), descs)
    return out


def gametdb_lookup(tdb, key):
    """GameTDB の ID はゲームコード4文字＋メーカー2文字（Wii・GC）、4文字（DS）、PS3 は型番（ハイフン無し）。"""
    if not key:
        return None
    if key in tdb:
        return tdb[key]
    if len(key) < 4:
        return None
    hits = {(v[0], tuple(v[1])) for k, v in tdb.items() if k.startswith(key)}
    return (lambda h: (h[0], list(h[1])))(hits.pop()) if len(hits) == 1 else None


_OFFICIAL_OLD = {"全年齢対象": "全年齢", "12才以上対象": "12", "15才以上対象": "15", "18才以上対象": "18"}


def load_official(pf):
    """fetch_cero.py で保存した CERO のタイトル検索の結果 → [{title, maker, rating, descriptors}]。
    区分・内容アイコンは画像の alt（新区分は 'A'〜'Z'、旧区分は「全年齢対象」など）。"""
    out = []
    d = C.CACHE / "cero" / pf
    for p in sorted(d.glob("p*.html"), key=lambda p: int(p.stem[1:])) if d.exists() else []:
        t = p.read_bytes().decode("euc_jis_2004", "replace")
        for row in re.findall(r"<tr>\s*<td class=\"css2n\">(.*?)</tr>", t, re.S):
            cells = re.findall(r"<td[^>]*>(.*?)</td>", "<td class=\"css2n\">" + row, re.S)
            if len(cells) < 5:
                continue
            title = re.sub(r"<[^>]+>", "", cells[0]).replace("　", " ").strip()
            alts = re.findall(r'alt="([^"]*)"', cells[3])
            rating = alts[0] if alts else ""
            rating = _OFFICIAL_OLD.get(rating, rating)
            out.append({"title": title, "maker": re.sub(r"<[^>]+>", "", cells[1]).strip(),
                        "rating": rating, "descriptors": re.findall(r'alt="([^"]*)"', cells[4])})
    return out


def _numbers(title):
    """題名に含まれる番号（続編の番号）。ローマ数字（II〜X、Ⅱ〜Ⅹ）も数字として扱う。"""
    import unicodedata
    t = unicodedata.normalize("NFKC", title).lower()   # Ⅸ → ix、全角数字 → 半角
    def roman(m):
        v = {"i": 1, "v": 5, "x": 10}
        r = m.group(1)
        n = sum(-v[c] if i + 1 < len(r) and v[c] < v[r[i + 1]] else v[c] for i, c in enumerate(r))
        return str(n)
    t = re.sub(r"(?<![a-z])(x{0,2}(?:ix|iv|v?i{0,3}))(?![a-z])", lambda m: roman(m) if m.group(1) not in ("", "i") else m.group(1), t)
    return re.findall(r"\d+", t)


def official_lookup(entries, title, sim, min_sim=0.9, date=""):
    """題名がとても似ている（または一致する）CERO の審査タイトルの区分。同じ題名で区分が食い違うものは採らない。
    戻り値: (区分, [内容アイコン], 一致した題名, 類似度) / ("conflict", [区分]) / None"""
    import difflib
    if not entries:
        return None
    if "_norm" not in entries[0]:
        for e in entries:
            e["_norm"] = C.norm(e["title"])
            e["_nums"] = _numbers(e["title"])
    n = C.norm(title)
    nums = _numbers(title)
    exact = [e for e in entries if e["_norm"] == n]
    if exact:
        hits, best = exact, 1.0
    else:
        best, hits = 0.0, []
        for e in entries:
            m = difflib.SequenceMatcher(None, n, e["_norm"])
            if m.real_quick_ratio() < min_sim or m.quick_ratio() < min_sim or e["_nums"] != nums:
                continue   # 番号の違う続編（ゴッドファーザー と ゴッドファーザー2 など）は別のタイトル
            sc = sim(title, e["title"])
            if sc > best + 1e-9:
                best, hits = sc, [e]
            elif abs(sc - best) <= 1e-9:
                hits.append(e)
        if best < min_sim:
            return None
    ratings = {e["rating"] for e in hits}
    if len(ratings) == 2:   # 旧区分と新区分で 2 回審査されたもの（全年齢 と A など）は発売時期の表記を採る
        old, new = sorted(ratings, key=lambda v: v in "ABCDZ")
        if same_level(old, new):
            keep = old if date and date < NEW_SYSTEM_FROM else new
            hits = [e for e in hits if e["rating"] == keep]
            ratings = {keep}
    if len(ratings) != 1:
        return ("conflict", sorted(ratings))
    descs = sorted({tuple(e["descriptors"]) for e in hits}, key=len)[-1]
    return (hits[0]["rating"], list(descs), hits[0]["title"], best)
