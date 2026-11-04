#!/usr/bin/env python3
"""GBA国内タイトル一覧に型番・価格を付与する。

入力:
  data/gba/wikipedia_titles.csv          fetch_wikipedia_list.py の出力（発売順の基礎リスト）
  data/gba/overrides/group_expansions.csv まとめ行（ファミコンミニ等）を個別タイトルに展開する表
  data/gba/overrides/matches.csv          自動照合の手動補正
  メディア芸術データベース(MADB) データセット gm301（ゲームパッケージ） … 価格・型番
  MAME ソフトウェアリスト hash/gba.xml                                  … 型番（ROMのゲームコード）

出力:
  data/gba/jp_titles.csv
  data/gba/review/match_report.csv        要確認の照合結果（自動照合の低スコア・型番の不一致など）

使い方:
  python3 scripts/enrich_gba.py            # ソースは .cache/ にダウンロードして再利用
"""
import csv
import datetime
import difflib
import json
import re
import subprocess
import sys
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
DATA = ROOT / "data" / "gba"

MADB_REPO = "https://github.com/mediaarts-db/dataset"
MADB_ZIP = "data/json-ld/metadata_gm-item_gm301_json.zip"
NOINTRO_URL = ("https://raw.githubusercontent.com/libretro/libretro-database/master/"
               "metadat/no-intro/Nintendo%20-%20Game%20Boy%20Advance.dat")
MAME_URL = "https://raw.githubusercontent.com/mamedev/mame/master/hash/gba.xml"
UA = "retro-game-db/0.1 (https://github.com/moheronemy/retro-game-db)"

MADB_PLATFORM = "ゲームボーイアドバンス"
MIN_SIM_SAME_DATE = 0.5   # 同日発売の候補を採用する最低類似度
MIN_SIM_NEAR_DATE = 0.9   # 発売日が近い(±NEAR_DAYS)場合の最低類似度
NEAR_DAYS = 31
REVIEW_SIM = 0.75         # これ未満の自動照合はレポートに出す
# 同梱版・限定版・廉価版など通常版以外のパッケージ（照合時に減点し、採用時はレポートに出す）
VARIANT = re.compile(r"同梱|限定|セット|BOX|ベスト|BEST|廉価|お買い得|特別版|専売|アルティメットヒッツ|ベスト・プライス")
VARIANT_PENALTY = 0.3


# ---------------------------------------------------------------- sources

def load_madb():
    """MADB gm301 から GBA のパッケージを読み込む（.cache に保存）。"""
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
                if x["@id"].startswith("_:") or x.get("gamePlatform") != MADB_PLATFORM:
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
                })
    return out


def fetch(url, path):
    if not path.exists():
        CACHE.mkdir(exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    return path


def load_nointro_jp_codes():
    """No-Intro DAT から日本版の4文字ゲームコード集合を得る（型番の検証用）。"""
    text = fetch(NOINTRO_URL, CACHE / "nointro_gba.dat").read_text(encoding="utf-8")
    return {f"AGB-{c}-JPN" for c in re.findall(r'serial "([A-Z0-9]{3}J)"', text)}


def load_mame():
    path = fetch(MAME_URL, CACHE / "mame_gba.xml")
    out = []
    for s in ET.parse(path).getroot().findall("software"):
        desc = s.findtext("description") or ""
        info = {i.get("name"): i.get("value") for i in s.findall("info")}
        serial = info.get("serial") or ""
        if "(Japan" not in desc and "JPN" not in serial:
            continue
        if re.search(r"prototype|promo|demo|Kiosk|Hot Mario", desc, re.I):
            continue  # 一般販売品ではないもの（非売品は別途扱う）
        rel = info.get("release") or ""
        date = f"{rel[:4]}-{rel[4:6]}-{rel[6:8]}" if re.fullmatch(r"\d{8}", rel) else ""
        titles = [t for t in (info.get("alt_title"), re.sub(r"\s*\(.*$", "", desc)) if t]
        out.append({
            "key": s.get("name"),
            "label": info.get("alt_title") or desc,
            "date": date,
            "titles": titles,
            "serial": serial,
            "clone": bool(s.get("cloneof")),
        })
    # 同じゲームの別リビジョン(clone)は親を優先して除外
    parents = {(m["serial"], m["date"]) for m in out if not m["clone"]}
    return [m for m in out if not m["clone"] or (m["serial"], m["date"]) not in parents]


# ---------------------------------------------------------------- normalize

def norm(s):
    s = unicodedata.normalize("NFKC", s).lower()
    return re.sub(r"[\s・･~〜～\-－―:：!！?？.,、。&＆'\"“”「」『』()（）\[\]【】/+＋☆★♪®×x]", "", s)


GAME_CODE = re.compile(r"\b(?:AGB|ABG|AGP)-(?:P-)?-?([A-Z0-9]{3}J)\b")


def model_from(text):
    """'AGB-P-B9AJ(JPN)' や 'AGB-B9AJ-JPN' から 'AGB-B9AJ-JPN' を得る。"""
    codes = []
    for m in GAME_CODE.finditer(text.upper()):
        c = f"AGB-{m.group(1)}-JPN"
        if c not in codes:
            codes.append(c)
    return codes


def parse_price(s):
    s = unicodedata.normalize("NFKC", s)
    m = re.search(r"([\d,]+)\s*円", s) or re.search(r"\\\s*([\d,]+)", s)
    if not m:
        return "", ""
    yen = m.group(1).replace(",", "")
    tax = "税込" if "税込" in s else "税抜" if "税抜" in s else ""
    return yen, tax


def days(a, b):
    try:
        return abs((datetime.date.fromisoformat(a) - datetime.date.fromisoformat(b)).days)
    except ValueError:
        return None


def sim(a, b):
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


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
            if d is None:
                continue
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


# ---------------------------------------------------------------- main

def read_csv(p):
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def expand_groups(rows):
    groups = {}
    for g in read_csv(DATA / "overrides" / "group_expansions.csv"):
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


def main():
    rows = expand_groups(read_csv(DATA / "wikipedia_titles.csv"))
    for i, r in enumerate(rows):
        r["_i"] = i
    overrides = {}
    for o in read_csv(DATA / "overrides" / "matches.csv"):
        d = overrides.setdefault((o["release_date"], o["title"]), {})
        for col in ("madb_id", "mame_name", "model_number", "price_yen", "price_tax"):
            if o.get(col):
                d[col] = o[col]

    madb, mame, nointro = load_madb(), load_mame(), load_nointro_jp_codes()
    print(f"MADB GBA: {len(madb)} 件 / MAME 日本版: {len(mame)} 件", file=sys.stderr)
    m_madb = match(rows, madb, overrides, "madb_id")
    m_mame = match(rows, mame, overrides, "mame_name")

    report = []
    for r in rows:
        i = r["_i"]
        md, md_sc, md_how = m_madb.get(i, (None, 0, ""))
        mm, mm_sc, mm_how = m_mame.get(i, (None, 0, ""))
        ov = overrides.get((r["release_date"], r["title"]), {})

        mame_codes = model_from(mm["serial"]) if mm else []
        madb_codes = model_from(md["product_id"]) if md else []
        # 型番の優先順位: 手動 > MAME（ROMのゲームコード） > MADB（パッケージ表記。誤記あり）
        model = ov.get("model_number") or (mame_codes or madb_codes or [""])[0]
        srcs = []
        if ov.get("model_number"):
            srcs.append("manual")
        if model and model in mame_codes:
            srcs.append("MAME")
        if model and model in madb_codes:
            srcs.append("MADB")
        if model and model in nointro:
            srcs.append("No-Intro")
        model_src = "+".join(srcs)

        yen, tax = parse_price(md["price"]) if md else ("", "")
        price_src = "MADB" if yen else ""
        if ov.get("price_yen"):
            yen, tax, price_src = ov["price_yen"], ov.get("price_tax", ""), "manual"

        r.update({
            "model_number": model, "model_number_source": model_src,
            "price_yen": yen, "price_tax": tax, "price_source": price_src,
            "madb_id": md["key"] if md else "", "mame_name": mm["key"] if mm else "",
            # 価格の根拠になったMADBのパッケージ名（限定版・セット品等の場合に判別できるように）
            "price_package": md["label"] if md and yen and price_src == "MADB" else "",
        })

        issues = []
        if md_how == "auto" and md_sc < REVIEW_SIM:
            issues.append(f"MADB低スコア{md_sc:.2f}")
        if mm_how == "auto" and mm_sc < REVIEW_SIM:
            issues.append(f"MAME低スコア{mm_sc:.2f}")
        if not md and md_how != "manual":
            issues.append("MADB未照合")
        if not mm and mm_how != "manual":
            issues.append("MAME未照合")
        if md and md_how == "auto" and VARIANT.search(md["label"]) and not VARIANT.search(r["title"]):
            issues.append("MADBが通常版以外の可能性")
        if model and model not in nointro:
            issues.append("型番がNo-Introに無い")
        if mame_codes and madb_codes and mame_codes[0] not in madb_codes:
            issues.append(f"型番不一致 MAME={mame_codes[0]} MADB={'/'.join(madb_codes)}")
        if issues:
            report.append({
                "release_date": r["release_date"], "title": r["title"], "issues": "; ".join(issues),
                "madb_id": md["key"] if md else "", "madb_title": md["label"] if md else "",
                "madb_date": md["date"] if md else "",
                "mame_name": mm["key"] if mm else "", "mame_title": mm["label"] if mm else "",
                "mame_date": mm["date"] if mm else "",
            })

    for n, r in enumerate(rows, 1):
        r["id"] = f"gba-jp-{n:04d}"
    fields = ["id", "release_date", "title", "publisher", "model_number", "price_yen", "price_tax",
              "notes", "wikipedia_article", "model_number_source", "price_source", "price_package", "madb_id", "mame_name"]
    with open(DATA / "jp_titles.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    (DATA / "review").mkdir(exist_ok=True)
    with open(DATA / "review" / "match_report.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(report[0]) if report else ["title"])
        w.writeheader()
        w.writerows(report)

    n = len(rows)
    print(f"{n} 件: 型番 {sum(bool(r['model_number']) for r in rows)} / "
          f"価格 {sum(bool(r['price_yen']) for r in rows)} / 要確認 {len(report)}", file=sys.stderr)


if __name__ == "__main__":
    main()
