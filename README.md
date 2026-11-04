# retro-game-db

Wii 世代（2000年代中盤）までのレトロゲーム情報を収集するデータベース。
まずは**日本国内で発売されたタイトルの一覧**を機種ごとに作成する。

## 収録状況

| 機種 | ファイル | 件数 | 型番 | 価格 |
|---|---|---|---|---|
| ゲームボーイアドバンス (GBA) | [`data/gba/jp_titles.csv`](data/gba/jp_titles.csv) | 793 | 777 | 759 |

## GBA

### 出典

| 用途 | 出典 | 版 | ライセンス |
|---|---|---|---|
| タイトル・発売日・発売元・備考 | ja.wikipedia「[ゲームボーイアドバンスのゲームタイトル一覧](https://ja.wikipedia.org/wiki/ゲームボーイアドバンスのゲームタイトル一覧)」 | oldid=110862677 (2026-09-01) | CC BY-SA 4.0 |
| 価格（・型番の補助） | [メディア芸術データベース データセット](https://github.com/mediaarts-db/dataset) gm301 ゲームパッケージ | 2024-11-26 コミット（データは2022-02時点） | 自由な二次利用可（加工した旨を表示） |
| 型番 | [MAME ソフトウェアリスト `hash/gba.xml`](https://github.com/mamedev/mame/blob/master/hash/gba.xml) | master | CC0-1.0 |
| 型番の検証 | [No-Intro DAT（libretro-database 収録）](https://github.com/libretro/libretro-database/blob/master/metadat/no-intro/Nintendo%20-%20Game%20Boy%20Advance.dat) | master | — |

### 件数について

出典ページの本文では「国内発売 全791タイトル」とされている。表の 761 行のうち、
複数タイトルをまとめて1行にしている次の5行を個別タイトルに展開して 793 件とした
（展開内容は [`data/gba/overrides/group_expansions.csv`](data/gba/overrides/group_expansions.csv)）。

- ファミコンミニ（01〜10）／第2弾（11〜20）／ディスクシステムセレクション（21〜30）
- bit Generations（3作）／Series 2（4作）

年別では本文記載と 2002年・2005年が各 +1 件で、それ以外は一致する。

| 年 | 2001 | 2002 | 2003 | 2004 | 2005 | 2006 |
|---|---|---|---|---|---|---|
| 本文記載 | 132 | 209 | 155 | 185 | 79 | 31 |
| 収録 | 132 | 210 | 155 | 185 | 80 | 31 |

### CSV の列

| 列 | 内容 |
|---|---|
| `id` | `gba-jp-<連番>`（発売順）。出典の行が増減すると変わるため、現時点では安定IDではない |
| `release_date` | 国内発売日 `YYYY-MM-DD` |
| `title` | タイトル（Wikipedia表記） |
| `publisher` | 発売元 |
| `model_number` | 型番 `AGB-XXXJ-JPN`（カートリッジ／ROM のゲームコード） |
| `price_yen` | 発売時のメーカー希望小売価格（円） |
| `price_tax` | `税抜` / `税込`。2004年4月の総額表示義務化以降はほぼ税込表記 |
| `notes` | 備考（Wikipedia の備考欄） |
| `wikipedia_article` | リンク先の Wikipedia 記事名 |
| `model_number_source` | 型番が確認できた出典（`MAME` / `MADB` / `No-Intro` / `manual` を `+` で連結） |
| `price_source` | 価格の出典（`MADB` / `manual`） |
| `price_package` | 価格の根拠にした MADB のパッケージ名（初回限定版・スターターセット等の判別用） |
| `madb_id` / `mame_name` | 照合したメディア芸術データベースの ID / MAME のソフト名 |

### 照合の方法と精度

Wikipedia の各行を、MADB・MAME の各エントリと「発売日 ＋ タイトルの類似度」で自動照合している
（同梱版・限定版などは減点して通常版を優先）。自動照合で誤るものは
[`data/gba/overrides/matches.csv`](data/gba/overrides/matches.csv) で手動補正している。
無作為抽出 25 件の目視確認では誤照合はなかった。

型番は MAME を優先する。MAME と MADB の型番が食い違った 5 件（テトリスワールド、
ロックマンエグゼ3、RPGツクール アドバンス、ハドソンベストコレクションVol.1、ビーダマン炎魂）は
No-Intro と照らしていずれも MAME が正しく、MADB 側の誤記だった。

要確認の照合結果（低スコア、出典に見つからない、型番不一致など）は
[`data/gba/review/match_report.csv`](data/gba/review/match_report.csv) に出力される。

### 既知の欠落・注意点

- 型番なし 16 件：EZ-TALK 初級編 1〜6、ドラえもん どこでもウォーカー、ウイ・イレ、GREMLiNS など、MAME に日本版が無く MADB にも型番が無いもの
- 価格なし 34 件：MADB に未収録（メトロイドフュージョン、ゾイドサーガ等）または価格欄が空のもの
- `price_package` が初回限定版・スターターセット・「お買い得シリーズ」等のものは、そのパッケージの価格である
- ファミコンミニ17 高橋名人の冒険島 は MADB の値（4,900円税抜）が誤記と判断し、手動で 2,000円（税込）にしている
- 廉価版（追加要素なし）は Wikipedia の方針により含まない

## 再生成

```sh
python3 scripts/fetch_wikipedia_list.py gba   # Wikipedia → data/gba/wikipedia_titles.csv
python3 scripts/enrich_gba.py                 # 型番・価格を付与 → data/gba/jp_titles.csv
```

`enrich_gba.py` は MADB・MAME・No-Intro のデータを `.cache/` にダウンロードして再利用する。

## ライセンス

`data/` 以下のデータは上記出典を加工したもの。Wikipedia 由来の部分は
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.ja) に従う。
メディア芸術データベース由来の価格は、同データベースのデータセットを加工して作成した。
