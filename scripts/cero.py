"""CERO の年齢区分（2002年〜）。

出典の優先順:
  1. MADB で照合した商品の contentRating（「CERO A (全年齢対象)」→ A、旧区分の「CERO 全年齢」→ 全年齢）
  2. GameTDB（Wii・GC: wiitdb、DS: dstdb、PS3: ps3tdb）。新区分（A〜Z）でしか書かれていないので、2006年3月以降の発売分だけに使う
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
