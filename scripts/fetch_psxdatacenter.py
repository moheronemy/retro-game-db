#!/usr/bin/env python3
"""psxdatacenter.com（PS1・PS2 の型番データベース）の日本版の一覧と、PS1 の作品別ページを取得して .cache/ に保存する。

  .cache/psxdatacenter/jlist.html     PS1 日本版の一覧（型番・ローマ字／英語の題名・作品別ページへのリンク）
  .cache/psxdatacenter/jlist2.html    PS2 日本版の一覧（型番・ローマ字／英語の題名のみ。作品別ページは無い）
  .cache/psxdatacenter/ps1/<型番>.html PS1 の作品別ページ（発売日・発売元・題名）

個人運営のサイトなので、保存済みのページは取り直さず、取得は 2 秒間隔にする（PS1 の作品別ページは約 4,800 件で約 3 時間）。
中断しても、もう一度実行すれば続きから取得する。

使い方:
  python3 scripts/fetch_psxdatacenter.py            # 一覧と PS1 の作品別ページ
  python3 scripts/fetch_psxdatacenter.py --lists    # 一覧だけ
"""
import argparse
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / ".cache" / "psxdatacenter"
BASE = "https://www.psxdatacenter.com/"   # www の無いホストは接続できない環境がある
UA = "retro-game-db research (https://github.com/moheronemy/retro-game-db)"
INTERVAL = 2.0


def get(url, path, retries=4):
    if path.exists() and path.stat().st_size > 0:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                path.write_bytes(r.read())
            return True
        except Exception as e:  # noqa: BLE001
            wait = 30 * (i + 1)
            print(f"  {url}: {e} → {wait} 秒後に再試行", file=sys.stderr)
            time.sleep(wait)
    print(f"  取得できず: {url}", file=sys.stderr)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lists", action="store_true", help="一覧ページだけ取得する")
    a = ap.parse_args()
    for name, url in (("jlist.html", BASE + "jlist.html"), ("jlist2.html", BASE + "psx2/jlist2.html")):
        if get(url, DIR / name):
            time.sleep(INTERVAL)
    if a.lists:
        return
    text = (DIR / "jlist.html").read_text(encoding="utf-8", errors="replace")
    links = sorted(set(re.findall(r'href="(games/J/[^"]+\.html)"', text)))
    done = 0
    for n, link in enumerate(links, 1):
        if get(BASE + link, DIR / "ps1" / Path(link).name):
            done += 1
            time.sleep(INTERVAL)
        if n % 200 == 0:
            print(f"{n}/{len(links)}（今回取得 {done}）", file=sys.stderr, flush=True)
    print(f"完了: {len(links)} 件（今回取得 {done}）", file=sys.stderr)


if __name__ == "__main__":
    main()
