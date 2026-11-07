#!/usr/bin/env python3
"""アタリ・インターナショナル日本支社のアタリ2800（Atari 2800。1983年5月10日発売の日本版 Atari 2600）のソフト一覧を作る。

出典: ja.wikipedia「Atari 2600」の「バリエーション」節の Atari 2800 の項。
  - パンフレットカタログの第1弾 25 本（本文「31タイトルを発売、この内の25タイトルが本体と同時発売」）→ 発売日 1983-05-10
  - パッケージと説明書が確認されている 2 本（パックマン・飛び鳥戦士）→ 発売日は空欄
  - アンケートはがきにだけ名前のある 10 本は載せない（発売が確かめられない。合意済み）
本文の 31 本とは数が合わず、全件かは分からない。価格・型番は出典が無い。
ハッシュは No-Intro DAT（libretro 収録の Atari - 2600）で「(Japan, USA)」と記録されたもののうち、題名の対応が明らかなものだけ
（DAT_NAMES。米国だけの吸い出しは使わない）。MAME `a2600` に日本版の記録は無く、MADB にも記録が無い。

出力: data/atari2800/jp_titles.csv、data/atari2800/jp_rom_dumps.csv
使い方: python3 scripts/build_atari2800.py
"""
import re
import sys

import common as C

DIR = C.ROOT / "data" / "atari2800"
PAGE = "Atari 2600"
LAUNCH = "1983-05-10"
PUBLISHER = "アタリ・インターナショナル日本支社"
# 日本語題 → No-Intro の「(Japan, USA)」の吸い出し（題名の対応が明らかなものだけ）
DAT_NAMES = {
    "空・海戦闘": ["Air-Sea Battle ~ Target Fun (Japan, USA) (En)", "Air-Sea Battle ~ Target Fun (Japan, USA) (En) (Atari Anthology)"],
    "アステロイド（小遊星）": ["Asteroids (Japan, USA) (En)"],
    "バザーク": ["Berzerk (Japan, USA) (En)"],
    "センティビード": ["Centipede (Japan, USA) (En)"],
    "サーカス・アタリ": ["Circus Atari (Japan, USA) (En)"],
}


def wiki_text():
    cache = C.CACHE / "wikipedia" / f"{PAGE}.wiki"
    if not cache.exists():
        import fetch_wikipedia_list as F
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(F.fetch_wikitext(PAGE)[0], encoding="utf-8")
    return cache.read_text(encoding="utf-8")


def numbered(block):
    out = []
    for m in re.findall(r"^:#\s*(.+?)\s*$", block, re.M):
        m = re.sub(r"\{\{\s*Sfn[^}]*\}\}|<ref[^>]*/>|<ref[^>]*>.*?</ref>", "", m)   # 出典の注記
        out.append(re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", m).strip())
    return out


def main():
    text = wiki_text()
    sec = text[text.index("; Atari 2800"):text.index("== 反響 ==")]
    first = sec[sec.index("第1弾の発売"):sec.index("アンケートはがき")]
    confirmed = sec[sec.index("パッケージと説明書が確認"):]
    launch, extra = numbered(first), numbered(confirmed)
    if len(launch) != 25 or len(extra) != 2:
        sys.exit(f"一覧の本数が想定と違います: 第1弾 {len(launch)} / 確認済み {len(extra)}")

    rows = []
    for t in launch:
        rows.append({"release_date": LAUNCH, "title": t, "publisher": PUBLISHER, "model_number": "", "price_yen": "",
                     "price_tax": "", "notes": "パンフレットカタログの第1弾（本体と同時発売）", "release_date_sources": "Wikipedia"})
    for t in extra:
        rows.append({"release_date": "", "title": t, "publisher": PUBLISHER, "model_number": "", "price_yen": "",
                     "price_tax": "", "notes": "記事に「パッケージと説明書が確認されている」とある。発売時期は出典に無い",
                     "release_date_sources": ""})
    for i, r in enumerate(rows, 1):
        r["id"] = f"atari2800-jp-{i:04d}"
    unknown = set(DAT_NAMES) - {r["title"] for r in rows}
    if unknown:
        sys.exit(f"DAT_NAMES の題名が一覧にありません: {unknown}")

    games = {}
    for b in C.nointro_dat_text("Atari - 2600").split("game (")[1:]:
        n = re.search(r'name "([^"]+)"', b)
        rom = re.search(r"size (\d+) crc ([0-9A-F]+) md5 ([0-9A-F]+) sha1 ([0-9A-F]+)", b)
        if n and rom:
            games[n.group(1)] = rom
    dumps = []
    for r in rows:
        for name in DAT_NAMES.get(r["title"], []):
            rom = games.get(name)
            if rom is None:
                sys.exit(f"No-Intro にありません: {name}")
            dumps.append({"title_id": r["id"], "title": r["title"], "dump_name": name,
                          "dump_kind": "collection" if "Anthology" in name else "retail",
                          "size": rom.group(1), "crc32": rom.group(2).lower(), "md5": rom.group(3).lower(),
                          "sha1": rom.group(4).lower(), "hash_source": "No-Intro"})
    C.write_csv(DIR / "jp_titles.csv", rows, ["id", "release_date", "title", "publisher", "model_number", "price_yen", "price_tax",
                                              "notes", "release_date_sources"])
    C.write_csv(DIR / "jp_rom_dumps.csv", dumps)
    print(f"{len(rows)} 件 / 吸い出しのあるタイトル {len({d['title_id'] for d in dumps})} / {len(dumps)} 行", file=sys.stderr)


if __name__ == "__main__":
    main()
