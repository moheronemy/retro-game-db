"""機種に依存しない共通処理（出典の取得・キャッシュ、正規化、照合）。"""
import csv
import datetime
import difflib
import html
import json
import re
import subprocess
import time
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
UA = "retro-game-db/0.1 (https://github.com/moheronemy/retro-game-db)"

MADB_REPO = "https://github.com/mediaarts-db/dataset"
MADB_ZIP = "data/json-ld/metadata_gm-item_gm301_json.zip"
NOINTRO_DAT_URL = ("https://raw.githubusercontent.com/libretro/libretro-database/master/"
                   "metadat/no-intro/{name}.dat")
MAME_URL = "https://raw.githubusercontent.com/mamedev/mame/master/hash/{name}.xml"

MIN_SIM_SAME_DATE = 0.5   # 同日発売の候補を採用する最低類似度
MIN_SIM_NEAR_DATE = 0.9   # 発売日が近い(±NEAR_DAYS)場合の最低類似度
NEAR_DAYS = 31
REVIEW_SIM = 0.75         # これ未満の自動照合はレポートに出す
# 同梱版・限定版・廉価版など通常版以外のパッケージ（照合時に減点し、採用時はレポートに出す）
VARIANT = re.compile(r"同梱|限定|セット|BOX|ベスト|BEST|廉価|お買い得|特別版|専売|アルティメットヒッツ|ベスト・プライス"
                     r"|単品版|バリューセレクション|ビギナーズパック|ゲートパック|スペシャルパッケージ")
VARIANT_PENALTY = 0.3


# ---------------------------------------------------------------- files

def read_csv(p):
    p = Path(p)
    if not p.exists():
        return []
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields=None):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields or (list(rows[0]) if rows else ["id"]), extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def fetch(url, path):
    path = Path(path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    return path


# ---------------------------------------------------------------- normalize

_KANJI_NUM = {"一": "1", "二": "2", "三": "3", "四": "4", "五": "5", "六": "6", "七": "7", "八": "8", "九": "9",
              "十": "10"}


def norm(s):
    s = unicodedata.normalize("NFKC", s).lower()
    # 「for WonderSwan」と「for ワンダースワン」（MADB・MAME と Wikipedia で表記が分かれる）
    s = s.replace("wonderswan", "ワンダースワン")
    # 「第一巻」「第2弾」などを数字だけにそろえる（例: 「火の鳥1」と「火の鳥 第一巻」）
    s = re.sub(r"第([一二三四五六七八九十]|\d+)(巻|弾|章|話|号)",
               lambda m: _KANJI_NUM.get(m.group(1), m.group(1)), s)
    return re.sub(r"[\s・･~〜～\-－―:：!！?？.,、。&＆'\"“”「」『』()（）\[\]【】/+＋☆★♪®×x]", "", s)


def sim(a, b):
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    r = difflib.SequenceMatcher(None, a, b).ratio()
    # 片方がもう一方の先頭に含まれる（副題の有無だけが違う）場合は底上げする
    # 例: 「フリップル」と「フリップル AN EXCITING CUBE GAME」
    short, long_ = sorted((a, b), key=len)
    if len(short) >= 4 and long_.startswith(short):
        r = max(r, 0.75)
    return r


def days(a, b):
    try:
        return abs((datetime.date.fromisoformat(a) - datetime.date.fromisoformat(b)).days)
    except ValueError:
        return None


def parse_price(s):
    s = unicodedata.normalize("NFKC", s)
    m = re.search(r"([\d,]+)\s*円", s) or re.search(r"\\\s*([\d,]+)", s)
    if not m:
        return "", ""
    yen = m.group(1).replace(",", "")
    # 「（税別）」「（消費税別）」も税抜、「税込み」「消費税込」も税込（MADB の表記ゆれ）
    tax = "税込" if re.search(r"税込", s) else "税抜" if re.search(r"税抜|税別", s) else ""
    return yen, tax


def tax_rate(date):
    """発売日時点の消費税率（1989-04-01 に3%、1997-04-01 に5%、2014-04-01 に8%）。"""
    if date and date >= "2014-04-01":
        return 0.08
    if date and date >= "1997-04-01":
        return 0.05
    if date and date >= "1989-04-01":
        return 0.03
    return 0.0


def net_price(yen, tax, date=""):
    """税込価格を発売日時点の消費税率で税抜に換算する。"""
    return round(int(yen) / (1 + tax_rate(date or "2000-01-01"))) if tax == "税込" else int(yen)


# ---------------------------------------------------------------- matching

def date_compatible(a, b):
    """日まで分からない発売日（'1984-12'・'1984'）どうしが矛盾しないか。片方が空なら矛盾しないとみなす。"""
    return not a or not b or a.startswith(b) or b.startswith(a)


def _numbers(title):
    import cero
    return cero._numbers(title)


def title_hint(title, cand_titles, cand_label):
    """同日 1 件ずつの組を採ってよいだけの題名の手がかりがあるか（match の date_hint）。"""
    import psxdc
    if VARIANT.search(cand_label) and not VARIANT.search(title):
        return False
    for t in cand_titles:
        t = re.sub(r"\s*~\s.*$", "", t)   # MAME の「日本語題 ~ ローマ字題」
        a, b = norm(title), norm(t)
        if not a or not b or _numbers(title) != _numbers(t):
            continue
        if (min(len(a), len(b)) >= 2 and (a in b or b in a)) or \
                difflib.SequenceMatcher(None, psxdc.romaji(title), psxdc.romaji(t)).ratio() >= 0.62:
            return True
    return False


def match(rows, src, overrides, col, date_only=False, undated_sim=None):
    """rows の各行に src の1件を割り当てる（貪欲法・重複割り当てなし）。
    date_only なら、残った行と候補が同じ発売日にちょうど1件ずつのとき、題名が似ていなくても組にする
    （FC の『ダブルドラゴン』と MAME の『双截龍』のような表記違い。要確認レポートに出す）。"""
    by_key = {s["key"]: s for s in src}
    result = {}
    used = set()
    for r in rows:
        o = overrides.get((r["release_date"], r["title"]), {}).get(col)
        if o is not None:
            result[r["_i"]] = (by_key.get(o), 1.0, "manual") if o != "-" else (None, 0, "manual")
            if o != "-":
                used.add(o)
    pairs = []
    for r in rows:
        if r["_i"] in result:
            continue
        for s in src:
            d = days(r["release_date"], s["date"])
            if d is None and undated_sim and date_compatible(r["release_date"], s["date"]):
                # 発売日が日まで分からない・出典に発売日が無い（SG-1000）: 題名がとても似ているものだけ
                sc = max(sim(r["title"], t) for t in s["titles"])
                if sc >= undated_sim:
                    pairs.append((sc - 0.5, sc, r["_i"], s["key"]))
                continue
            if d is None or d > NEAR_DAYS:
                continue   # 採用条件（同日、または ±NEAR_DAYS）に入らない候補は類似度を計算しない
            sc = max(sim(r["title"], t) for t in s["titles"])
            if VARIANT.search(s["label"]) and not VARIANT.search(r["title"]):
                sc -= VARIANT_PENALTY
            if (d == 0 and sc >= MIN_SIM_SAME_DATE) or (d <= NEAR_DAYS and sc >= MIN_SIM_NEAR_DATE):
                pairs.append((sc - d * 0.001, sc, r["_i"], s["key"]))
    pairs.sort(reverse=True)
    for _, sc, i, k in pairs:
        if i in result or k in used:
            continue
        result[i] = (by_key[k], sc, "auto")
        used.add(k)
    # 同じ発売日に残った行と候補がちょうど1件ずつで、題名に手がかりがあるもの（ローマ字にした題名が似ている〈0.62 以上〉か、
    # 片方の題名がもう片方に含まれる）は組にする。題名の中の番号が違うもの・候補だけが限定版などのものは採らない
    # （『エレベーターアクション』と MAME の『Elevator Action』、『四川省』と『四川省 MATCH MANIA』など。要確認レポートに出す）
    hint = []
    left_rows, left_src = {}, {}
    for r in rows:
        if r["_i"] not in result:
            left_rows.setdefault(r["release_date"], []).append(r)
    for x in src:
        if x["key"] not in used and x["date"]:
            left_src.setdefault(x["date"], []).append(x)
    for date, rs in left_rows.items():
        if len(rs) == 1 and len(left_src.get(date, [])) == 1:
            r, x = rs[0], left_src[date][0]
            if title_hint(r["title"], x["titles"], x["label"]):
                result[r["_i"]] = (x, 0, "date_hint")
                used.add(x["key"])
    if date_only:
        left_rows, left_src = {}, {}
        for r in rows:
            if r["_i"] not in result:
                left_rows.setdefault(r["release_date"], []).append(r)
        for x in src:
            if x["key"] not in used and x["date"]:
                left_src.setdefault(x["date"], []).append(x)
        for date, rs in left_rows.items():
            if len(rs) == 1 and len(left_src.get(date, [])) == 1:
                result[rs[0]["_i"]] = (left_src[date][0], 0, "date_only")
    return result


# ---------------------------------------------------------------- sources

def load_madb(platforms):
    """メディア芸術データベース gm301（ゲームパッケージ）から指定機種のパッケージを読む。"""
    path = CACHE / "madb_gm301.zip"
    if not path.exists():
        CACHE.mkdir(exist_ok=True)
        repo = CACHE / "madb-dataset"
        if not repo.exists():
            subprocess.run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none",
                            "--no-checkout", MADB_REPO, str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "checkout", "-q", "HEAD", "--", MADB_ZIP], check=True)
        (repo / MADB_ZIP).replace(path)
    out = []
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            # データ中に生の制御文字が含まれるため strict=False
            graph = json.loads(z.read(name).decode("utf-8"), strict=False)["@graph"]
            for x in graph:
                if x["@id"].startswith("_:") or x.get("gamePlatform") not in platforms:
                    continue
                names = [x["label"]]
                for n in x["name"] if isinstance(x["name"], list) else [x["name"]]:
                    if isinstance(n, str):
                        names.append(n)
                v = x.get("variantTitle")
                if v:
                    names += v if isinstance(v, list) else [v]
                out.append({
                    "key": x["identifier"],
                    "label": x["label"],
                    "date": x.get("datePublished") or "",
                    "titles": names,
                    "price": x.get("price") or "",
                    "product_id": x.get("productID") or "",
                    "media_format": x.get("mediaFormat") or "",
                    "rating": x.get("contentRating") or "",            # 年齢区分（scripts/cero.py）
                    "rating_desc": x.get("contentRatingDescriptor") or "",
                })
    return out


def mame_xml(name):
    return fetch(MAME_URL.format(name=name), CACHE / f"mame_{name}.xml")


def load_mame(lists, jp_models=None, all_japanese=()):
    """MAME ソフトウェアリストの日本版（一般販売品）を読む。
    jp_models を渡すと、説明に (Japan) が無くても（例: 'Tetris (World)'）シリアルに日本版の型番があれば含める。"""
    out = []
    for lst in lists:
        for s in ET.parse(mame_xml(lst)).getroot().findall("software"):
            desc = s.findtext("description") or ""
            key = mame_key(lists, lst, s.get("name"))
            info = {i.get("name"): i.get("value") for i in s.findall("info")}
            serial = info.get("serial") or ""
            if (lst not in all_japanese and not re.search(r"[(,] ?Japan[,)?]", desc) and "JPN" not in serial
                    and not (jp_models and jp_models(serial))):
                continue
            if (jp_models and not re.search(r"Japan|World", desc)
                    and re.search(r"\([^()]*\b(?:USA|Europe|Asia|Korea|Brazil|Taiwan)\b[^()]*\)", desc)):
                continue   # 型番の形が全地域共通の機種（ネオジオポケットの 'NeoP00930'）の海外だけの版
            if re.search(r"prototype|promo|demo|Kiosk|Hot Mario", desc, re.I):
                continue  # 一般販売品ではないもの（非売品は別途扱う）
            if lst in all_japanese and re.search(r"\((?:Asia|Korea|Hong Kong)", desc):
                continue  # 日本版だけのリストに混じる海外版（ワンダースワンの 'Robot Works (Asia)'）
            rel = info.get("release") or ""
            # '19890614' のほか '19890614 (JPN)' のような注記付きもある
            # ネオジオは '19900426 (MVS), 19910701 (AES)' のように業務用と家庭用の日付が並ぶので家庭用を採る
            rm = re.search(r"(\d{4})(\d{2})(\d{2}) \(AES\)", rel) or re.match(r"(\d{4})(\d{2})(\d{2})(?:$|\s)", rel)
            date = f"{rm.group(1)}-{rm.group(2)}-{rm.group(3)}" if rm else ""
            alt = info.get("alt_title") or ""
            if "(Japan)" in alt:  # 'メトロイド2 リターン・オブ・サムス (Japan), …(China)' のような複数表記
                alt = next(a for a in alt.split(", ") if "(Japan)" in a).replace("(Japan)", "").strip()
            titles = [t for t in (alt, re.sub(r"\s*\(.*$", "", desc)) if t]
            out.append({
                "key": key,
                "label": alt or desc,
                "date": date,
                "titles": titles,
                "serial": serial,
                "clone": bool(s.get("cloneof")),
                "list": lst,
            })
    # 同じゲームの別リビジョン(clone)は親を優先して除外
    parents = {(m["serial"], m["date"]) for m in out if not m["clone"]}
    return [m for m in out if not m["clone"] or (m["serial"], m["date"]) not in parents]


def mame_key(lists, lst, name):
    """ソフト名は MAME のリストごとに一意なので、2つ目以降のリストは「リスト名:ソフト名」にする
    （例: gameboy と gbcolor の両方に 'supchinf' がある）。"""
    return name if lst == lists[0] else f"{lst}:{name}"


def mame_software(lists):
    """キー → software 要素。"""
    out = {}
    for lst in lists:
        for s in ET.parse(mame_xml(lst)).getroot().findall("software"):
            out[mame_key(lists, lst, s.get("name"))] = s
    return out


def _gf2_times(mat, vec):
    out, i = 0, 0
    while vec:
        if vec & 1:
            out ^= mat[i]
        vec >>= 1
        i += 1
    return out


def crc32_combine(crc1, crc2, len2):
    """crc32(A + B) を crc32(A)、crc32(B)、len(B) から求める（zlib の crc32_combine と同じ）。"""
    if len2 <= 0:
        return crc1
    odd = [0xEDB88320] + [1 << i for i in range(31)]
    even = [_gf2_times(odd, odd[i]) for i in range(32)]
    odd = [_gf2_times(even, even[i]) for i in range(32)]
    while True:
        even = [_gf2_times(odd, odd[i]) for i in range(32)]
        if len2 & 1:
            crc1 = _gf2_times(even, crc1)
        len2 >>= 1
        if not len2:
            break
        odd = [_gf2_times(even, even[i]) for i in range(32)]
        if len2 & 1:
            crc1 = _gf2_times(odd, crc1)
        len2 >>= 1
        if not len2:
            break
    return crc1 ^ crc2


def _mame_joined_crc(s):
    """FC のように ROM がチップ別（prg / chr）に分かれているとき、つなげた ROM 全体（ヘッダーなし）の CRC。"""
    roms = []
    for area in ("prg", "chr"):
        for d in s.iter("dataarea"):
            if d.get("name") == area:
                roms += [r for r in d.findall("rom") if r.get("crc")]
    if len(roms) < 2 or any(r.get("loadflag") for r in roms):
        return None
    crc = int(roms[0].get("crc"), 16)
    for r in roms[1:]:
        crc = crc32_combine(crc, int(r.get("crc"), 16), int(r.get("size"), 0))
    return f"{crc:08x}"


def mame_crcs(lists):
    """CRC → [(キー, 状態)]。チップ別の ROM は、つなげた全体の CRC も登録する。"""
    out = {}
    for key, s in mame_software(lists).items():
        status = "good"
        for rom in s.iter("rom"):
            if rom.get("crc"):
                out.setdefault(rom.get("crc").lower(), []).append((key, rom.get("status") or "good"))
            if rom.get("status") in ("baddump", "nodump"):
                status = rom.get("status")
        joined = _mame_joined_crc(s)
        if joined:
            out.setdefault(joined, []).append((key, status))
    return out


def nointro_dat_text(name):
    """libretro-database 収録の DAT。'redump:Nintendo - GameCube' のように 'redump:' を付けると Redump の DAT。"""
    group = "no-intro"
    if name.startswith("redump:"):
        group, name = "redump", name[len("redump:"):]
    url = NOINTRO_DAT_URL.replace("/no-intro/", f"/{group}/").format(name=urllib.request.quote(name))
    safe = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").lower()
    prefix = "nointro" if group == "no-intro" else group
    return fetch(url, CACHE / f"{prefix}_{safe}.dat").read_text(encoding="utf-8")


# 1つのゲームに複数の形式の ROM を載せている DAT で採る形式（FC はヘッダーなし、ディスクシステムは .fds）
DAT_ROM_EXT = {"Nintendo - Nintendo Entertainment System": ".unh",
               "Nintendo - Family Computer Disk System": ".fds",
               "Nintendo - Nintendo 64": ".z64"}   # N64 はビッグエンディアン（.z64）。.v64 は載せない


def _dat_games(name):
    """DAT の game ブロック。同じ名前で複数の形式の ROM がある場合は採る形式（DAT_ROM_EXT）のものだけ。"""
    ext = DAT_ROM_EXT.get(name)
    # 末尾に改行の無い DAT があるので補う（最後の game を落とさないように）
    blocks = [m.group(1) for m in re.finditer(r'game \(\n(.*?)\n\)\n', nointro_dat_text(name) + "\n", re.S)]
    if not ext:
        return blocks
    has_ext = lambda b: re.search(r'rom \( name "[^"]*' + re.escape(ext) + '"', b)
    gname_of = lambda b: re.search(r'name "([^"]+)"', b).group(1)
    names_with_ext = {gname_of(b) for b in blocks if has_ext(b)}
    return [b for b in blocks if has_ext(b) or gname_of(b) not in names_with_ext]


def _dat_named_games(name):
    """(一意な名前, ブロック) の一覧。libretro 版 DAT には同名の game が複数あることがある。
    - 同じハッシュ（Redump の GC・PCE CD でレーベルのシリアル違いだけ）: 1つにまとめ、シリアルは ';' でつなぐ
    - 違うハッシュ（PCE CD『イースI・II』の '(Alt)' 版など）: それぞれ ROM のファイル名
      （トラック番号・拡張子を除く）を名前にし、それでも重なるときは [2] などを付ける"""
    blocks = list(_dat_games(name))
    gname_of = lambda b: re.search(r'name "([^"]+)"', b).group(1)
    sha1_of = lambda b: (re.search(r'sha1 ([0-9A-Fa-f]+)', b) or [None, ""])[1].lower()
    serial_of = lambda b: (re.search(r'rom \(.*?serial "([^"]+)"', b) or [None, ""])[1]
    groups = {}
    for b in blocks:
        groups.setdefault(gname_of(b), []).append(b)
    out, used = [], set()
    for gname, bs in groups.items():
        merged = {}   # sha1 → ブロック（シリアルを足していく）
        for b in bs:
            h = sha1_of(b)
            if h in merged:
                extra = serial_of(b)
                if extra and extra not in serial_of(merged[h]).split(";"):
                    old = serial_of(merged[h])
                    merged[h] = re.sub(r'(rom \(.*?serial ")([^"]*)(")', lambda m: m.group(1) + (old + ";" if old else "") + extra + m.group(3),
                                       merged[h], count=1) if old else merged[h].replace(" )", f' serial "{extra}" )', 1)
                continue
            merged[h] = b
        uniq = list(merged.values())
        for b in uniq:
            uname = gname
            if len(uniq) > 1:
                rom = re.search(r'rom \( name "([^"]+)"', b).group(1)
                uname = re.sub(r" \(Track \d+\)", "", re.sub(r"\.[A-Za-z0-9]+$", "", rom))
            n = 2
            base = uname
            while uname in used:
                uname = f"{base} [{n}]"
                n += 1
            used.add(uname)
            out.append((uname, b))
    return out


def load_nointro_dat(names):
    """libretro 版 No-Intro DAT: 名前 → (ゲームコード, サイズ, CRC, MD5, SHA1)。"""
    out = {}
    for name in names:
        for gname, b in _dat_named_games(name):
            rom = re.search(r'rom \( (.*?) \)', b).group(1)
            g = lambda k: (re.search(k + r' "?([^" ]+)"?', rom) or [None, ""])[1]
            out[gname] = dict(serial=g("serial"), size=g("size"), crc=g("crc").lower(),
                              md5=g("md5").lower(), sha1=g("sha1").lower(), dat=name)
    return out


def nointro_dat_as_export(dat_name):
    """DB Export が無いときの代わりに、libretro 版 DAT から DB Export と同じ形の XML を組み立てる。
    吸い出し記録（確認区分・ROM チップ刻印など）は無いので、確認区分は dat_only になる。"""
    root = ET.Element("root")
    for name, b in _dat_named_games(dat_name):
        rom = re.search(r'rom \( (.*?) \)', b).group(1)
        g = lambda k: (re.search(k + r' "?([^" ]+)"?', rom) or [None, ""])[1]
        region = (re.search(r'region "([^"]+)"', b) or [None, ""])[1]
        if "Japan" in name:
            region = region or "Japan"
        first = re.search(r"\(([^()]*)\)", name)
        if first and "Japan" in first.group(1).split(", ") and "Japan" not in region:
            region += ", Japan"   # DAT の region 欄は最初の地域だけ（'Doom (USA, Japan)' → 'USA'）
        game = ET.SubElement(root, "game", name=name)
        ET.SubElement(game, "archive", region=region, number="", details="")
        src = ET.SubElement(game, "source")
        ET.SubElement(src, "details", section="DAT")
        ET.SubElement(src, "file", size=g("size"), crc32=g("crc").lower(), md5=g("md5").lower(),
                      sha1=g("sha1").lower(), serial=g("serial"))
    return root


def load_nointro_export(pattern, path=None, fallback_dat=None):
    """No-Intro DB Export（DAT-o-MATIC から手動で取得する zip / xml）を読む。
    無ければ fallback_dat（libretro 版 DAT の名前）から組み立てる。"""
    if path is None:
        found = sorted((CACHE / "nointro-db").glob(f"*{pattern}*"))
        if not found:
            if fallback_dat:
                print(f"No-Intro DB Export（{pattern}）が無いため libretro 版 DAT（{fallback_dat}）を使う",
                      file=__import__("sys").stderr)
                return nointro_dat_as_export(fallback_dat), f"libretro DAT ({fallback_dat})"
            raise SystemExit(f"No-Intro DB Export（{pattern}）が見つかりません。"
                             ".cache/nointro-db/ に置くか --export で指定してください")
        path = found[-1]
    path = Path(path)
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as z:
            text = z.read(z.namelist()[0]).decode("utf-8")
    else:
        text = path.read_text(encoding="utf-8")
    version = re.search(r"<version>([^<]+)</version>", text)
    # <header> と <datafile> の2つのルート要素が並んでいるので包んで読む
    root = ET.fromstring("<root>" + text.split("?>", 1)[1] + "</root>")
    return root, version.group(1) if version else ""


# ---------------------------------------------------------------- maru-chang

def load_maru(cfg):
    """maru-chang.com のラインナップ全ページを取得・解析する（.cache/maru-chang/ に保存）。"""
    d = CACHE / cfg["cache_dir"]
    d.mkdir(parents=True, exist_ok=True)
    out = []
    for page in range(1, cfg["pages"] + 1):
        path = d / f"p{page:02d}.html"
        if not path.exists():
            req = urllib.request.Request(cfg["url"].format(page=page), headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                path.write_bytes(r.read())
            time.sleep(cfg.get("interval", 5))  # 個人サイトなのでアクセス間隔を空ける
        t = path.read_text(encoding="utf-8", errors="replace")
        # 1件は <tr id="…"> から次の <tr id="…"> まで（行の class が "line1" 以外のこともあるので id で区切る）
        starts = [m.start() for m in re.finditer(r'<tr id="', t)] + [len(t)]
        for a, b in zip(starts, starts[1:]):
            seg = t[a:b]
            m = re.match(r'<tr id="([^"]+)"[^>]*>(.*?)<td class="code">([^<]*)</td>', seg, re.S)
            if not m:
                continue
            row_id, body, code = m.group(1), m.group(2), m.group(3).strip()
            # 他社ソフトは型番欄にメーカー独自の商品番号（例: NCS89006）が入り、任天堂の型番は行の id にある
            if not cfg["model"](code) and cfg["model"](row_id):
                code = row_id
            # 日付欄は class="month" のほか class="ndate month" のこともある
            mon = re.search(r'class="[^"]*\bmonth">(\d{4})年(\d{1,2})月', body)
            day = re.search(r'class="[^"]*\bday">(\d{1,2})日', body)
            title = re.search(r'class="title">(.*?)</div>', body, re.S)
            title = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", title.group(1)))).strip() if title else ""
            price = re.search(r'class="price">(.*?)</div>', body, re.S)
            ptxt = html.unescape(re.sub(r"<[^>]+>", " ", price.group(1))) if price else ""
            # 先頭の価格が発売時の通常版価格。2つ目以降は廉価版・セット等。
            # ただし「¥36,000：6巻セット … ¥6,000：単品」のようにセット価格が先に来る場合は単品を採る
            prices = list(re.finditer(r"¥([\d,]+)(（税込）)?\s*(?:：\s*([^¥]*))?", ptxt))
            pm = next((p for p in prices if p.group(3) and "単品" in p.group(3)), None) \
                or next((p for p in prices if not (p.group(3) and re.search(r"セット|本体", p.group(3)))), None)
            out.append({
                "key": code,
                "label": title,
                "titles": [title],
                "date": "%s-%02d-%02d" % (mon.group(1), int(mon.group(2)), int(day.group(1))) if mon and day else "",
                "model": cfg["model"](code),
                # 税表記のない価格は税抜とみなす（GBA で照合した727件で税換算後の金額が一致することを確認）
                "yen": pm.group(1).replace(",", "") if pm else "",
                "tax": ("税込" if pm.group(2) else "税抜") if pm else "",
                "not_for_sale": ptxt.strip().startswith("非売品"),
            })
    out = [m for m in out if not m["not_for_sale"]]
    if cfg.get("require_model"):  # 型番がディスクソフトの形式のものだけ（Wii のチャンネル・VC 等を除く）
        out = [m for m in out if m["model"]]
    return out


def match_maru(rows, maru, overrides, code_of=None, date_only=False):
    """型番が同じものを優先し、型番が無い行はタイトル＋発売日で照合する。
    code_of を渡すと型番の接頭辞を無視してゲームコードで比べる（DS の NTR-/TWL- の違いを吸収）。
    行に ref_code（Wikipedia の脚注から拾ったゲームコード）があればそれでも照合する。"""
    by_key = {m["key"]: m for m in maru}
    key_of = code_of or (lambda x: x)
    by_model = {}
    for m in maru:
        by_model.setdefault(key_of(m["model"]), []).append(m)
    result, used = {}, set()
    for r in rows:
        o = overrides.get((r["release_date"], r["title"]), {}).get("maru_code")
        if o:
            result[r["_i"]] = by_key.get(o) if o != "-" else None
            used.add(o)
    for r in rows:
        k = key_of(r["model_number"]) if r["model_number"] else r.get("ref_code", "")
        if r["_i"] in result or not k:
            continue
        cands = [m for m in by_model.get(k, []) if m["key"] not in used]
        cands = [m for m in cands if (days(r["release_date"], m["date"]) or 0) <= NEAR_DAYS]
        if cands:
            m = min(cands, key=lambda m: days(r["release_date"], m["date"]) or 0)
            result[r["_i"]] = m
            used.add(m["key"])
    # タイトルでの照合: 同じ発売日の候補との類似度が高い組から順に割り当てる（行の順に取ると、
    # 同日に似た題名が並ぶシリーズ物で先の行が別の行の正解を奪うため）。1位と2位が拮抗する行は割り当てない。
    pairs = []
    for r in rows:
        if r["_i"] in result:
            continue
        # 行のタイトルに加えて、照合済みの MADB の別表記（英字タイトルなど）でも比べる
        names = [r["title"]] + list(r.get("_alt_titles") or [])
        cands = sorted(((max(sim(n, m["label"]) for n in names), m) for m in maru
                        if m["key"] not in used and m["date"] == r["release_date"]), key=lambda c: -c[0])
        cands = [c for c in cands if c[0] >= 0.6]
        if not cands:
            continue
        if len(cands) > 1 and cands[0][0] < 0.95 and cands[0][0] - cands[1][0] < 0.05:
            continue
        pairs.append((cands[0][0], r["_i"], cands[0][1]["key"]))  # 各行はいちばん近い候補だけ（取られたら諦める）
    pairs.sort(key=lambda p: -p[0])
    for sc, i, k in pairs:
        if i in result or k in used:
            continue
        result[i] = by_key[k]
        used.add(k)
    if date_only:
        # 最後に、同じ発売日に照合されていない行と maru-chang のエントリが1件ずつだけ残っていれば組にする
        # （maru-chang が英字表記・Wikipedia が日本語表記で類似度が出ない場合。要確認として扱う）
        left_rows, left_maru = {}, {}
        for r in rows:
            if r["_i"] not in result and r["release_date"]:
                left_rows.setdefault(r["release_date"], []).append(r)
        for m in maru:
            if m["key"] not in used and m["date"]:
                left_maru.setdefault(m["date"], []).append(m)
        for d, rs in left_rows.items():
            ms = left_maru.get(d, [])
            if len(rs) == 1 and len(ms) == 1:
                result[rs[0]["_i"]] = ms[0]
                rs[0]["_maru_date_only"] = True
    return result
