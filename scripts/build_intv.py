#!/usr/bin/env python3
"""バンダイのインテレビジョン（1982年7月発売。米国マテルの Intellivision の日本版）のソフト一覧を作る。

出典はメディア芸術データベース（機種の欄が「Intellivision」の商品のうち、発売元がバンダイのもの）だけ。
Wikipedia に日本のソフトの一覧は無く、MAME `intv`・No-Intro（Mattel - Intellivision）に日本版の項目が無い。
全件かは確かめられない。米国 Imagic 社のカートリッジ（日本での発売の記録が無い）は対象外。
ハッシュは載せない（日本版の吸い出しの記録が無い。英字題から米国版を当てることはしない）。

出力: data/intv/jp_titles.csv
使い方: python3 scripts/build_intv.py
"""
import json
import re
import sys
import zipfile

import common as C

DIR = C.ROOT / "data" / "intv"


def main():
    items = []
    with zipfile.ZipFile(C.CACHE / "madb_gm301.zip") as z:
        for f in z.namelist():
            for x in json.loads(z.read(f).decode("utf-8", "replace"), strict=False).get("@graph", []):
                if x.get("gamePlatform") == "Intellivision" and "バンダイ" in str(x.get("ma:publisher", "")):
                    items.append(x)
    items.sort(key=lambda x: (str(x.get("datePublished") or "9999"), x.get("label", "")))
    rows = []
    for i, x in enumerate(items, 1):
        yen = re.sub(r"\D", "", str(x.get("price") or ""))
        note = "ゲームシート同梱" if "ゲームシート同梱" in str(x.get("description", "")) else ""
        rows.append({"id": f"intv-jp-{i:04d}", "release_date": x.get("datePublished") or "", "title": x["label"],
                     "title_en": x.get("variantTitle") or "", "publisher": "バンダイ", "model_number": "",
                     "price_yen": yen, "price_tax": "税なし" if yen else "", "notes": note,
                     "release_date_sources": "MADB" if x.get("datePublished") else "",
                     "price_source": "MADB" if yen else "", "madb_id": x["identifier"],
                     "madb_source": x.get("source") or ""})
    C.write_csv(DIR / "jp_titles.csv", rows,
                ["id", "release_date", "title", "title_en", "publisher", "model_number", "price_yen", "price_tax", "notes",
                 "release_date_sources", "price_source", "madb_id", "madb_source"])
    print(f"{len(rows)} 件（MADB。全件かは不明）", file=sys.stderr)


if __name__ == "__main__":
    main()
