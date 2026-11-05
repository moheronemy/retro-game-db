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

def norm(s):
    s = unicodedata.normalize("NFKC", s).lower()
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
    tax = "税込" if "税込" in s else "税抜" if "税抜" in s else ""
    return yen, tax


def tax_rate(date):
    """発売日時点の消費税率（1989-04-01 に3%、1997-04-01 に5%）。"""
    if date and date >= "1997-04-01":
        return 0.05
    if date and date >= "1989-04-01":
        return 0.03
    return 0.0


def net_price(yen, tax, date=""):
    """税込価格を発売日時点の消費税率で税抜に換算する。"""
    return round(int(yen) / (1 + tax_rate(date or "2000-01-01"))) if tax == "税込" else int(yen)


# ---------------------------------------------------------------- matching

def match(rows, src, overrides, col):
    """rows の各行に src の1件を割り当てる（貪欲法・重複割り当てなし）。"""
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
                })
    return out


def mame_xml(name):
    return fetch(MAME_URL.format(name=name), CACHE / f"mame_{name}.xml")


def load_mame(lists, jp_models=None):
    """MAME ソフトウェアリストの日本版（一般販売品）を読む。
    jp_models を渡すと、説明に (Japan) が無くても（例: 'Tetris (World)'）シリアルに日本版の型番があれば含める。"""
    out = []
    for lst in lists:
        for s in ET.parse(mame_xml(lst)).getroot().findall("software"):
            desc = s.findtext("description") or ""
            key = mame_key(lists, lst, s.get("name"))
            info = {i.get("name"): i.get("value") for i in s.findall("info")}
            serial = info.get("serial") or ""
            if "(Japan" not in desc and "JPN" not in serial and not (jp_models and jp_models(serial)):
                continue
            if re.search(r"prototype|promo|demo|Kiosk|Hot Mario", desc, re.I):
                continue  # 一般販売品ではないもの（非売品は別途扱う）
            rel = info.get("release") or ""
            # '19890614' のほか '19890614 (JPN)' のような注記付きもある
            rm = re.match(r"(\d{4})(\d{2})(\d{2})(?:$|\s)", rel)
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


def mame_crcs(lists):
    """CRC → [(キー, 状態)]。"""
    out = {}
    for key, s in mame_software(lists).items():
        for rom in s.iter("rom"):
            if rom.get("crc"):
                out.setdefault(rom.get("crc").lower(), []).append((key, rom.get("status") or "good"))
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


def load_nointro_dat(names):
    """libretro 版 No-Intro DAT: 名前 → (ゲームコード, サイズ, CRC, MD5, SHA1)。"""
    out = {}
    for name in names:
        for m in re.finditer(r'game \(\n(.*?)\n\)\n', nointro_dat_text(name), re.S):
            b = m.group(1)
            gname = re.search(r'name "([^"]+)"', b).group(1)
            rom = re.search(r'rom \( (.*?) \)', b).group(1)
            g = lambda k: (re.search(k + r' "?([^" ]+)"?', rom) or [None, ""])[1]
            out[gname] = dict(serial=g("serial"), size=g("size"), crc=g("crc").lower(),
                              md5=g("md5").lower(), sha1=g("sha1").lower(), dat=name)
    return out


def nointro_dat_as_export(dat_name):
    """DB Export が無いときの代わりに、libretro 版 DAT から DB Export と同じ形の XML を組み立てる。
    吸い出し記録（確認区分・ROM チップ刻印など）は無いので、確認区分は dat_only になる。"""
    root = ET.Element("root")
    text = nointro_dat_text(dat_name)
    for m in re.finditer(r'game \(\n(.*?)\n\)\n', text, re.S):
        b = m.group(1)
        name = re.search(r'name "([^"]+)"', b).group(1)
        rom = re.search(r'rom \( (.*?) \)', b).group(1)
        g = lambda k: (re.search(k + r' "?([^" ]+)"?', rom) or [None, ""])[1]
        region = (re.search(r'region "([^"]+)"', b) or [None, ""])[1]
        if "Japan" in name:
            region = region or "Japan"
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
        for m in re.finditer(r'<tr id="[^"]+" class="line\d">(.*?)<td class="code">([^<]*)</td>', t, re.S):
            body, code = m.group(1), m.group(2).strip()
            mon = re.search(r'class="month">(\d{4})年(\d{1,2})月', body)
            day = re.search(r'class="day">(\d{1,2})日', body)
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
    return [m for m in out if not m["not_for_sale"]]


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
    for r in rows:
        if r["_i"] in result:
            continue
        # 行のタイトルに加えて、照合済みの MADB の別表記（英字タイトルなど）でも比べる
        names = [r["title"]] + list(r.get("_alt_titles") or [])
        cands = [(max(sim(n, m["label"]) for n in names), m) for m in maru
                 if m["key"] not in used and m["date"] == r["release_date"]]
        cands = [c for c in cands if c[0] >= 0.6]
        if cands:
            m = max(cands, key=lambda c: c[0])[1]
            result[r["_i"]] = m
            used.add(m["key"])
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
