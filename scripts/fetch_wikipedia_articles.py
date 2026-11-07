#!/usr/bin/env python3
"""作品ごとの ja.wikipedia の記事（wikitext）を取得して .cache/wikipedia/articles/<記事名>.wiki に保存する。

発売日の食い違いの確認（scripts/check_release_dates.py）に使う。2 秒間隔、保存済みの記事は取り直さない（中断しても続きから）。
記事が無い（404）ものは .missing として記録する。

使い方: python3 scripts/fetch_wikipedia_articles.py <記事名の一覧ファイル（1 行 1 記事）>
"""
import sys
import time
import urllib.error

import common as C
import fetch_wikipedia_list as F

DIR = C.CACHE / "wikipedia" / "articles"


def path_of(name):
    return DIR / (name.replace("/", "／") + ".wiki")


def main():
    DIR.mkdir(parents=True, exist_ok=True)
    names = [l.strip() for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
    todo = [n for n in dict.fromkeys(names) if not path_of(n).exists() and not path_of(n).with_suffix(".missing").exists()]
    print(f"{len(names)} 件中 {len(todo)} 件を取得", file=sys.stderr)
    for i, n in enumerate(todo, 1):
        try:
            text, _ = F.fetch_wikitext(n)
            path_of(n).write_text(text, encoding="utf-8")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                path_of(n).with_suffix(".missing").write_text("", encoding="utf-8")
            else:
                print(f"  {n}: {e}", file=sys.stderr)
        if i % 50 == 0:
            print(f"  {i}/{len(todo)}", file=sys.stderr)
        time.sleep(2)


if __name__ == "__main__":
    main()
