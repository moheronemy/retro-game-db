#!/usr/bin/env python3
"""CERO のタイトル検索（https://www.cero.biz/search/）から、機種ごとの審査タイトル（題名・メーカー・区分・内容アイコン）を取得して
.cache/cero/<機種>/p<ページ>.html に保存する。1ページ10件。2 秒間隔で、保存済みのページは取り直さない（中断しても続きから）。

検索の対象機種は DS・PSP・PS3・Wii・Xbox 360 など（PS2・GBA・GC・Xbox は無い）。発売日・型番は載っていない。

使い方:
  python3 scripts/fetch_cero.py            # NDS PSP PS3 Wii Xbox360
  python3 scripts/fetch_cero.py PS3        # 指定した機種だけ
"""
import re
import sys
import time
import urllib.request

from common import CACHE

BASE = "https://www.cero.biz/search/search.cgi?chkPF={pf}&name=&txtCP=&pg={pg}&sort=2"
UA = "retro-game-db research (https://github.com/moheronemy/retro-game-db)"
PLATFORMS = ["NDS", "PSP", "PS3", "Wii", "Xbox360"]


def get(url, retries=4):
    for i in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            print(f"  {url}: {e}", file=sys.stderr)
            time.sleep(30 * (i + 1))
    raise SystemExit(f"取得できず: {url}")


def main():
    for pf in sys.argv[1:] or PLATFORMS:
        d = CACHE / "cero" / pf
        d.mkdir(parents=True, exist_ok=True)
        first = d / "p1.html"
        if not first.exists():
            first.write_bytes(get(BASE.format(pf=pf, pg=1)))
            time.sleep(2)
        total = int(re.search(rb"(\d+)\s*</[^>]+>\s*\xb7\xef\xc3\xe6", first.read_bytes()).group(1))   # 「件中」（EUC-JP）
        pages = (total + 9) // 10
        for pg in range(2, pages + 1):
            p = d / f"p{pg}.html"
            if p.exists() and p.stat().st_size > 0:
                continue
            p.write_bytes(get(BASE.format(pf=pf, pg=pg)))
            time.sleep(2)
        print(f"{pf}: {total} 件 / {pages} ページ", file=sys.stderr)


if __name__ == "__main__":
    main()
