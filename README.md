# retro-game-db

Wii 世代（2000年代中盤）までのレトロゲーム情報を収集するデータベース。
まずは**日本国内で発売されたタイトルの一覧**を機種ごとに作成する。

## 収録状況

| 機種 | タイトル一覧 | 件数 | 型番 | 価格 | ROM 吸い出し一覧 |
|---|---|---|---|---|---|
| ゲームボーイアドバンス (GBA) | [`data/gba/jp_titles.csv`](data/gba/jp_titles.csv) | 793 | 792 | 792 | [`data/gba/jp_rom_dumps.csv`](data/gba/jp_rom_dumps.csv)（986 行） |

GBA ではほかに、非売品の一覧 [`data/gba/jp_not_for_sale.csv`](data/gba/jp_not_for_sale.csv)（5 件）と、
店頭体験版・開発版・試作品の一覧 [`data/gba/jp_non_retail.csv`](data/gba/jp_non_retail.csv)（35 件）がある。

## GBA

### 出典

| 用途 | 出典 | 版 | ライセンス |
|---|---|---|---|
| タイトル・発売日・発売元・備考 | ja.wikipedia「[ゲームボーイアドバンスのゲームタイトル一覧](https://ja.wikipedia.org/wiki/ゲームボーイアドバンスのゲームタイトル一覧)」 | oldid=110862677 (2026-09-01) | CC BY-SA 4.0 |
| 価格（・型番の補助） | [メディア芸術データベース データセット](https://github.com/mediaarts-db/dataset) gm301 ゲームパッケージ | 2024-11-26 コミット（データは2022-02時点） | 自由な二次利用可（加工した旨を表示） |
| 型番 | [MAME ソフトウェアリスト `hash/gba.xml`](https://github.com/mamedev/mame/blob/master/hash/gba.xml) | master | CC0-1.0 |
| 型番・価格の補完と照合、発売日の照合 | [maru-chang.com GBAソフトラインナップ](https://maru-chang.com/gamedb/gamelist.php/GBAlineup_new/) | 2026-11-05 取得（795 タイトル） | 個人サイト。照合・補完にのみ使い、一覧の転載はしない |
| 型番の検証 | [No-Intro DAT（libretro-database 収録）](https://github.com/libretro/libretro-database/blob/master/metadat/no-intro/Nintendo%20-%20Game%20Boy%20Advance.dat) | master | — |
| ハッシュ・リビジョン・吸い出し情報 | [No-Intro DAT-o-MATIC](https://datomatic.no-intro.org/) DB Export（GBA） | 20261102-131436 | [Data Usage License](https://datomatic.no-intro.org/terms.html)（自由に利用・再配布可、表示不要） |

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
| `release_date_sources` | 発売日が一致した出典（`Wikipedia` / `MADB` / `MAME` / `maru-chang` / `manual` を `+` で連結） |
| `model_number_source` | 型番が確認できた出典（`MAME` / `MADB` / `maru-chang` / `No-Intro` / `manual`） |
| `price_source` | 価格の出典（`MADB` / `maru-chang` / `manual`。両方一致なら `MADB+maru-chang`） |
| `price_package` | 価格の根拠にした MADB のパッケージ名（初回限定版・スターターセット等の判別用） |
| `madb_id` / `mame_name` / `maru_code` | 照合したメディア芸術データベースの ID / MAME のソフト名 / maru-chang の型番 |

### 照合の方法と精度

Wikipedia の各行を、MADB・MAME の各エントリと「発売日 ＋ タイトルの類似度」で自動照合している
（同梱版・限定版などは減点して通常版を優先）。自動照合で誤るものは
[`data/gba/overrides/matches.csv`](data/gba/overrides/matches.csv) で手動補正している。
無作為抽出 25 件の目視確認では誤照合はなかった。

型番は MAME を優先する。MAME と MADB の型番が食い違った 5 件（テトリスワールド、
ロックマンエグゼ3、RPGツクール アドバンス、ハドソンベストコレクションVol.1、ビーダマン炎魂）は
No-Intro と照らしていずれも MAME が正しく、MADB 側の誤記だった。

maru-chang とは型番で照合する（型番が無い行はタイトル＋発売日）。価格は税込を消費税5%で換算して比べ、
次のように扱う。

- MADB に価格が無い → maru-chang の価格で補う（税表記の無い価格は税抜とみなす。照合した 727 件で換算後の金額が一致）
- MADB が限定版・廉価版・同梱版・単品版などの価格 → maru-chang の通常版価格に置き換える
- 2004年4月以降なのに MADB が「税抜」、maru-chang が同額の「税込」 → 税込とする（総額表示義務化のため）
- それ以外の食い違い（11 件）→ MADB の値のまま要確認レポートに出す

型番は、maru-chang と食い違った 4 件（トゥームレイダー、ポケモンピンボール、ファミコンミニ14、
ONE PIECE ゴーイングベースボール）を No-Intro と照らした。前の 3 件は maru-chang の誤記、
ONE PIECE は MAME の誤記（`BO8J` → 正しくは数字の `B08J`）だった。

要確認の照合結果（低スコア、出典に見つからない、型番・価格・発売日の不一致など）は
[`data/gba/review/match_report.csv`](data/gba/review/match_report.csv) に出力される。

### 既知の欠落・注意点

- 型番・価格なし 1 件：GREMLiNS Stripe VS Gizmo（どの出典にも型番・価格が無い）
- 発売日：Wikipedia の日付を基本とし、3出典以上で誤りが明らかなもの（もじぴったん アドバンス 1/9 → 1/10）だけ手動で直している。
  他の出典と食い違う日付（おしゃれプリンセス5、鋼鉄帝国 など）は要確認レポートに出している
- `price_package` が初回限定版・スターターセット・「お買い得シリーズ」等のものは、そのパッケージの価格である
- ファミコンミニ17 高橋名人の冒険島 は MADB の値（4,900円税抜）が誤記と判断し、手動で 2,000円（税込）にしている
- 廉価版（追加要素なし）は Wikipedia の方針により含まない

## 非売品（`jp_not_for_sale.csv`）

一般の人の手に渡ったが販売されなかったカートリッジ（懸賞の景品、他機種ソフトの同梱品、株主優待など）。
**出典で配布経路まで確認できたものだけ**を載せる（配布時期が不明でも経路が確認できれば載せる）。
手で管理するファイルで、`id` は安定 ID。

| 列 | 内容 |
|---|---|
| `id` | `gba-jp-nfs-<連番>` |
| `title` | タイトル |
| `category` | `prize`（懸賞・キャンペーン景品）/ `bundled`（他機種ソフトの同梱品）/ `shareholder`（株主優待） |
| `parent_id` | 対応する製品版の `jp_titles.csv` の `id`（あれば） |
| `model_number` | 型番（ゲームコード） |
| `distributor` / `campaign` / `route` | 配布元 / キャンペーン名 / 配布経路 |
| `dist_start` / `dist_end` | 配布・応募の開始日 / 終了日（不明は空） |
| `quantity` | 配布数（当選数など） |
| `nointro_name` / `mame_name` | 吸い出し一覧と結びつけるための No-Intro 名 / MAME 名 |
| `sources` | 出典 URL（`;` 区切り） |
| `notes` | 補足 |

次の候補は配布経路を出典で確認できなかったため載せていない：ロックマンエグゼ3 BLACK（No-Intro の Promo 版）、
妖怪道 サクリコーンキャンペーン特別版、遊☆戯☆王デュエルモンスターズ5 エキスパート1 体験版。
カードe / カードe+ のカードは別プロジェクトとして対象外。

## 店頭体験版・開発版・試作品（`jp_non_retail.csv`）

No-Intro の DB Export から `scripts/build_dumps.py` が生成する。

| 区分（`category`） | 載せる条件 | 件数 |
|---|---|---|
| `store_demo` 店頭体験版 | No-Intro が店頭試遊用（Kiosk）と記録したもの。`media` が `gc_download` はゲームキューブの試遊台から GBA に送るもの、`cartridge` は体験版カートリッジ | 14 |
| `beta` 開発版 | No-Intro の Beta | 12 |
| `prototype` 試作品 | No-Intro の Proto（未発売作品・配布用機材を含む） | 7 |
| `tech_demo` 技術デモ | 開発キット付属のサンプル | 2 |

- 配布経路の記録がない体験版（ヒカルの碁 体験版など）と、非公式品・後年の自主制作は載せない。
- `id` は `gba-jp-nr-<No-Intro のアーカイブ番号>`。`parent_id` は No-Intro 名が製品版と一致するもので対応づける
  （開発版・試作品はゲームコードを別作品と共有していることがあるため、コードは使わない）。
  名前が一致しないものは [`data/gba/overrides/non_retail_parents.csv`](data/gba/overrides/non_retail_parents.csv) で補う。
- タイトルは対応する製品版がある場合「製品版タイトル（店頭体験版）」のように付け、無い場合は No-Intro 名のまま。

## ROM 吸い出し一覧（`jp_rom_dumps.csv`）

No-Intro の DB Export から、タイトルごとの吸い出し（ハッシュ・リビジョン）を 1 吸い出し 1 行で収録する。
ROM そのものは扱わない。製品版に加えて、非売品・店頭体験版・開発版・試作品の吸い出しも同じファイルに入れ、
`title_id` の接頭辞（`gba-jp-` / `gba-jp-nfs-` / `gba-jp-nr-`）と `dump_kind` で区別する。

| 列 | 内容 |
|---|---|
| `title_id` / `title` | `jp_titles.csv` / `jp_not_for_sale.csv` / `jp_non_retail.csv` の `id` / タイトル |
| `game_code` | ROM ヘッダのゲームコード（日米共通カートリッジは ROM 内が `xxxA`、型番は `xxxJ`） |
| `dump_name` | No-Intro の名前 |
| `revision` | リビジョン（`0` / `1` / `2`）。ROM チップ刻印の末尾（`AGB-XXXJ-0` / `-1`）と一致する。パッケージのラベル型番では見分けられない |
| `dump_kind` | `retail`（当時のカートリッジ）/ `virtual_console` / `collection`（後年の収録版）/ `not_for_sale` / `store_demo` / `beta` / `prototype` / `tech_demo` |
| `size` / `crc32` / `md5` / `sha1` / `sha256` | ROM のサイズ（バイト）とハッシュ。SHA256 は No-Intro の吸い出し記録があるものだけ |
| `verification` | `mame_only`（No-Intro に無く MAME のみ）/ `trusted_dump`（No-Intro が確認）/ `third_party`（外部提供）/ `trusted_modification` / `undocumented`（2001〜2003年ごろに出回った吸い出しの記録だけで、吸い出し元の記録なし） |
| `source_count` / `first_dump_date` | 吸い出し記録の数 / 最初の吸い出し日 |
| `rom_chip` / `label_serial` / `pcb` | ROM チップ刻印 / カートリッジのラベル型番 / 基板番号（記録があるもの） |
| `save_type` | セーブ方式（EEPROM / SRAM / Flash とライブラリ版） |
| `nointro_number` | No-Intro のアーカイブ番号 |
| `mame_name` / `mame_status` | 同じ CRC を持つ MAME のソフト名と状態 |
| `hash_source` | ハッシュの出典（`No-Intro` / `MAME`） |

製品版の吸い出しがあるのは 792 / 793 タイトル（GREMLiNS のみ無し）。製品版の吸い出しは 858 行で、Rev 0 が 783、Rev 1 が 71、Rev 2 が 4。
MAME と CRC が合わないものの多くは、ファミコンミニの ROM サイズの数え方（MAME 4MB / No-Intro 1MB）か、
MAME が 2003〜2007年ごろの古い外部提供の吸い出しを使っているもの。

## 再生成

```sh
python3 scripts/fetch_wikipedia_list.py gba   # Wikipedia → data/gba/wikipedia_titles.csv
python3 scripts/enrich.py gba                  # 型番・価格を付与 → data/gba/jp_titles.csv
python3 scripts/build_dumps.py gba             # ROM 吸い出し一覧・別リスト → jp_rom_dumps.csv / jp_non_retail.csv
```

- スクリプトは機種名（`gba` など）を引数に取る。機種ごとの設定（Wikipedia のページと表の列、
  MADB の機種名、MAME のリスト、No-Intro の DAT 名、型番の形式など）は `scripts/platforms.py` にあり、
  共通処理は `scripts/common.py` にある。
- `enrich.py` は MADB・MAME・No-Intro DAT・maru-chang のデータを `.cache/` にダウンロードして再利用する。
  maru-chang は 5 秒間隔で 16 ページを取得する。
- `build_dumps.py` が使う No-Intro DB Export は、利用規約への同意が必要なため自動取得しない。
  [DAT-o-MATIC](https://datomatic.no-intro.org/) で規約に同意し、Download → Nintendo - Game Boy Advance →
  「DB」の Prepare → Download!! で得た zip を `.cache/nointro-db/` に置く（または `--export` で指定）。

## ライセンス

`data/` 以下のデータは上記出典を加工したもの。Wikipedia 由来の部分は
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.ja) に従う。
メディア芸術データベース由来の価格は、同データベースのデータセットを加工して作成した。
