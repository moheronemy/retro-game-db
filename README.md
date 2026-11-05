# retro-game-db

Wii 世代（2000年代中盤）までのレトロゲーム情報を収集するデータベース。
まずは**日本国内で発売されたタイトルの一覧**を機種ごとに作成する。

## 収録状況

| 機種 | タイトル一覧 | 件数 | 型番 | 価格 | ROM 吸い出し一覧 |
|---|---|---|---|---|---|
| ゲームボーイアドバンス (GBA) | [`data/gba/jp_titles.csv`](data/gba/jp_titles.csv) | 793 | 792 | 792 | [`data/gba/jp_rom_dumps.csv`](data/gba/jp_rom_dumps.csv)（997 行） |
| ゲームボーイ／ゲームボーイカラー (GB/GBC) | [`data/gb/jp_titles.csv`](data/gb/jp_titles.csv) | 1,245 | 1,194 | 1,199 | [`data/gb/jp_rom_dumps.csv`](data/gb/jp_rom_dumps.csv)（1,375 行） |
| ニンテンドーDS (DS) | [`data/ds/jp_titles.csv`](data/ds/jp_titles.csv) | 1,840 | 1,800 | 1,829 | [`data/ds/jp_rom_dumps.csv`](data/ds/jp_rom_dumps.csv)（2,074 行） |
| ニンテンドー ゲームキューブ (GC) | [`data/gc/jp_titles.csv`](data/gc/jp_titles.csv) | 276 | 272 | 274 | [`data/gc/jp_rom_dumps.csv`](data/gc/jp_rom_dumps.csv)（366 行） |

| 機種 | 非売品 | 店頭体験版・開発版・試作品 | その他 |
|---|---|---|---|
| GBA | [`jp_not_for_sale.csv`](data/gba/jp_not_for_sale.csv)（5 件） | [`jp_non_retail.csv`](data/gba/jp_non_retail.csv)（35 件） | |
| GB/GBC | [`jp_not_for_sale.csv`](data/gb/jp_not_for_sale.csv)（2 件） | [`jp_non_retail.csv`](data/gb/jp_non_retail.csv)（92 件） | ニンテンドウパワー [`jp_nintendo_power.csv`](data/gb/jp_nintendo_power.csv)（153 件） |
| DS | [`jp_not_for_sale.csv`](data/ds/jp_not_for_sale.csv)（13 件） | [`jp_non_retail.csv`](data/ds/jp_non_retail.csv)（35 件） | DSiウェア [`jp_dsiware.csv`](data/ds/jp_dsiware.csv)（493 件） |
| GC | [`jp_not_for_sale.csv`](data/gc/jp_not_for_sale.csv)（3 件） | [`jp_non_retail.csv`](data/gc/jp_non_retail.csv)（62 件） | |

各ファイルの列は GBA の節で説明している（GB/GBC も共通。GB/GBC 固有の列は GB/GBC の節を参照）。

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

## GB/GBC

ゲームボーイ・ゲームボーイカラーは 1 本のリストにまとめ、`compat` 列でカートリッジの種類を区別する。

| `compat` | 種類 | 件数 |
|---|---|---|
| `gb` | ゲームボーイ専用（灰カートリッジ） | 781 |
| `gbc_compatible` | ゲームボーイカラー対応（黒カートリッジ。モノクロ機でも動く） | 213 |
| `gbc_only` | ゲームボーイカラー専用（透明カートリッジ） | 251 |

`sgb` 列はスーパーゲームボーイ対応（`yes`）を示す（366 件）。`id` は `gb-jp-<連番>`（発売順）。

### 出典

| 用途 | 出典 | 版 |
|---|---|---|
| タイトル・発売日・発売元・SGB 対応 | ja.wikipedia「[ゲームボーイのゲームタイトル一覧](https://ja.wikipedia.org/wiki/ゲームボーイのゲームタイトル一覧)」（GB 専用）、「[ゲームボーイカラーのゲームタイトル一覧](https://ja.wikipedia.org/wiki/ゲームボーイカラーのゲームタイトル一覧)」（カラー対応・カラー専用の 2 表） | oldid=111571037 / 111419004 |
| 価格（・型番の補助） | メディア芸術データベース（機種「ゲームボーイ」。GBC も含む） | GBA と同じ |
| 型番・発売日の照合 | MAME ソフトウェアリスト `hash/gameboy.xml` / `hash/gbcolor.xml` | master |
| ハッシュ・リビジョン | No-Intro DB Export（Game Boy / Game Boy Color） | 20261031-010415 / 20261102-232700 |
| ニンテンドウパワー | ja.wikipedia「[ニンテンドウパワーのゲームタイトル一覧](https://ja.wikipedia.org/wiki/ニンテンドウパワーのゲームタイトル一覧)」ゲームボーイの表 | 2026-11-05 取得 |

maru-chang には GB/GBC の一覧が無いため、照合は Wikipedia・MADB・MAME の 3 つで行う。

### 件数について

Wikipedia の 3 つの表から日本で発売された行（日本の発売日が `{{Unreleased}}` でない行）を取り出すと 1,260 件で、
各ページ本文の記載（GB 781・カラー対応 223・カラー専用 256）と一致する。このうちニンテンドウパワーの
書き換え専用タイトル 15 件（スーパーマリオブラザーズDX、バルーンファイトGB、Loppi パズルマガジンなど）は
別リストに移したため、本リストは 1,245 件。

発売日が年月まで（`YYYY-MM`）・年まで（`YYYY`）しか分からない行がある（ドラえもんのスタディボーイ 1〜6）。

### 型番

型番の形式は時期で異なる。

- 初期: `DMG-TRA`、`DMG-WQJ` のような 3 文字（末尾が地域で、日本版は `A` または `J`）
- 後期: `DMG-ACCJ-JPN`（GB 専用・カラー対応）、`CGB-BDLJ-JPN`（カラー専用）

カラー対応は `DMG-`、カラー専用は `CGB-` で始まるのが通例で、外れる 4 件（ゴルフ王、ドン・キホーテが行く、
とっとこハム太郎 ともだち大作戦でちゅ、DDR GB3）は要確認レポートに出している。

GB の ROM の大半にはゲームコードが無く、No-Intro の DAT にもシリアルがほとんど無いため、型番の検証と
吸い出しとの対応づけは MAME 経由（CRC・英語名）が中心になる。型番なしは 51 件、価格なしは 46 件。

### 価格の税

1989年4月に消費税（3%）、1997年4月に 5% になったため、税込・税抜の換算は発売日時点の税率で行う。

### 非売品（`jp_not_for_sale.csv`）

基準は GBA と同じ（出典で配布経路まで確認できたもののみ）。現時点では Wikipedia「ゲームボーイカラーのゲームタイトル一覧」の
「その他」に出典付きで載っている 2 件（ボンバーマンMAX アインバージョン、同 完全データバージョン）。
各作品の Wikipedia 記事からの洗い出しは、Wikipedia 側のアクセス制限のため未実施。

### 店頭体験版・開発版・試作品（`jp_non_retail.csv`）

GBA の区分に加えて `event_demo`（展示会用の体験版。No-Intro の `Spaceworld 1997` の印。ポケットモンスター金・銀）がある。
No-Intro で `Possible Proto`（試作品の可能性）・`Sample`・`Test Program` とされたものは、区分が確かでないため載せない。

### ニンテンドウパワー（`jp_nintendo_power.csv`）

ローソン等の端末でフラッシュカートリッジに書き込む書き換えサービスで提供されたタイトル。1 行 = 1 書き換えタイトル。

| 列 | 内容 |
|---|---|
| `id` | `gb-jp-np-<連番>`（一覧の順） |
| `np_date` | 書き換え開始日 |
| `title` / `publisher` | タイトル / 発売元 |
| `np_only` | `yes` は通常版のカートリッジが発売されなかった書き換え専用タイトル（15 件） |
| `retail_date` / `parent_id` | 通常版の発売日 / `jp_titles.csv` の対応する `id` |
| `flash_blocks` / `save_blocks` | 書き込みに使うブロック数（F）/ セーブ用のブロック数（B） |
| `sheet_no` / `product_no` | 遊び方シート番号 / 商品番号 |

No-Intro の `(NP)` の吸い出し（28 件）は `jp_rom_dumps.csv` に `dump_kind = nintendo_power` で入れる（26 件を対応づけ。
書き換え専用タイトルは [`data/gb/overrides/np_dump_matches.csv`](data/gb/overrides/np_dump_matches.csv) で手動対応）。

## DS

ニンテンドーDS / DS Lite / DSi 用として日本で発売されたソフト（2004年12月〜2012年）。`id` は `ds-jp-<連番>`（発売順）。

| 列（DS 固有） | 内容 |
|---|---|
| `compat` | `ds`（1,805）/ `dsi_enhanced`（DSi の機能に対応、35）/ `dsi_only`（DSi 専用カートリッジ。No-Intro に日本版の登録が無く 0） |
| `ref_code` | Wikipedia の脚注にある任天堂公式サイトの URL から拾ったゲームコード（型番の補完と maru-chang との照合に使う） |

`compat` は No-Intro の分類で決める（DSi の DAT にあれば `dsi_only`、DS の DAT で `NDSi Enhanced` なら `dsi_enhanced`）。
型番の `TWL-` は DSi 対応・DSi 専用の両方に使われているため判定には使わない。

### 出典

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元 | ja.wikipedia「ニンテンドーDSのゲームタイトル一覧」の年別 6 ページ（2004-05 / 2006 / 2007 / 2008 / 2009 / 2010 / 2011-12）。表の発売日は年を省いているため、節の年を補う |
| 型番・価格の補完と照合、発売日の照合 | maru-chang.com DS ソフトラインナップ（2,354 タイトル。48 ページ） |
| 価格 | メディア芸術データベース（機種「ニンテンドーDS」） |
| 型番の検証・ハッシュ | No-Intro DAT（libretro-database 収録の DS / DSi） |

MAME には DS のソフトウェアリストがほぼ無いため使わない。照合は Wikipedia・MADB・maru-chang の 3 つ。

- 件数は 1,840 件で、親ページ本文の記載（全 1,840 タイトル）と一致する。
- maru-chang は英字タイトル（例: FINAL FANTASY III）で載せていることが多い。型番・Wikipedia 脚注のゲームコード・
  MADB の別表記で照合し、それでも合わないものは「同じ発売日に双方 1 件ずつ残ったもの」を組にしている（37 件。
  要確認レポートに「maru-chang同日1件のみで照合」と出る。目視ではすべて正しい組だった）。
- 型番なし 40 件（得点力学習DS シリーズなど、どの出典にも型番が無いもの）、価格なし 11 件。

### 吸い出し一覧

No-Intro DB Export（DS / DSi）は取得できていないため、libretro 版 DAT で代用している。ハッシュ（CRC32・MD5・SHA1）・
サイズ・リビジョンはあるが、確認区分は `dat_only` で、SHA256・ROM チップ刻印・セーブ方式は無い。
（DAT-o-MATIC から自動アクセスを制限されたため。DB Export を `.cache/nointro-db/` に置けば同じスクリプトで差し替わる。）

No-Intro の印の扱い: `DS Broadcast`（店頭の DS ステーションで配信された体験版）は店頭体験版、`Club Nintendo` と
`Not for Resale` は非売品・業務用の各リストで扱い、製品版からは除く。`Multiplayer`（ダウンロードプレイの子機データ）と
`Save Data` は対象外。

### 非売品（`jp_not_for_sale.csv`）・別リスト

Wikipedia「ニンテンドーDSのゲームタイトル一覧」の「非売品」節（出典付き）を次のように振り分けた。

| 振り分け先 | 内容 |
|---|---|
| 非売品（A1, 13 件） | クラブニンテンドー限定 4（ゲーム&ウオッチコレクション 1・2 など）、限定版・セット同梱品 3（逆転裁判事典など）、ANA のキャンペーン景品、江ノ島のイベント用ソフト、進研ゼミの付録 4 |
| 別リスト `event_demo`（3 件） | LEVEL 5 PREMIUM SILVER / GOLD / Platinum（東京ゲームショウ等で無料配布された体験版） |
| 別リスト `business`（3 件） | マクドナルドの従業員研修ソフト 2、介護事業所向けケア記録ソフト（すぐろくDS） |

非売品の `category` は GBA の 3 種に加えて `event`（イベント用ソフト）と `supplement`（雑誌・通信教育の付録）を使う。
別リストの手動追加分は [`data/ds/overrides/non_retail_manual.csv`](data/ds/overrides/non_retail_manual.csv)。

### DSiウェア（`jp_dsiware.csv`）

ダウンロード専用ソフトの別リスト（Wikipedia「ニンテンドーDSiウェアのタイトル一覧」、2008〜2015年配信、493 件）。
`release_date` は配信開始日、`blocks` は必要ブロック数、`3ds` はニンテンドー3DS での扱い（○△□×）。
2009年は本文「全170タイトル」に対し表は 169 行。ハッシュ（No-Intro の DSi (Digital)）は未収録。

## GC

ニンテンドー ゲームキューブ用として日本で発売されたソフト（2001〜2006年）。`id` は `gc-jp-<連番>`（発売順）。

### 出典

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元 | ja.wikipedia「ニンテンドー ゲームキューブのゲームタイトル一覧」（日本の発売日がある行。本文の記載どおり 275 件） |
| 型番・価格の補完と照合、発売日の照合 | maru-chang.com ゲームキューブ ソフトラインナップ（282 タイトル。6 ページ） |
| 価格 | メディア芸術データベース（機種「ニンテンドーゲームキューブ」） |
| 型番の検証・ハッシュ | Redump DAT（libretro-database 収録の `metadat/redump/Nintendo - GameCube.dat`） |

- 本リストは 276 件。Wikipedia の 275 件に、周辺機器に同梱されたソフト「ゲームボーイプレーヤー スタートアップディスク」
  （単体では販売されていないため価格なし）を [`data/gc/overrides/extra_titles.csv`](data/gc/overrides/extra_titles.csv) で加えた。
- 型番は `DOL-XXXJ-JPN`（Redump のシリアル `DL-DOL-XXXJ-JPN` もこの形にそろえる）。
- maru-chang は英字タイトルが多く、24 件は「同じ発売日に双方 1 件ずつ残ったもの」で照合している（要確認レポートに出る）。
- MADB の価格が maru-chang より 3 割以上高いものは本体・周辺機器との同梱版等の価格とみて maru-chang の価格にしている
  （どうぶつの森+ の DX パック、テイルズ オブ シンフォニアの同梱版など。DS にも同じ規則を適用）。

### 吸い出し一覧

光ディスクなのでハッシュは Redump。Redump 本家（redump.org）には現在接続できないため libretro 収録の Redump DAT を使っており、
確認区分は `dat_only`。複数枚組（バイオハザード、バイオハザード0 など）は 1 行にまとめ、`discs` 列に枚数、
`size`・`crc32` などはディスク順に `;` でつないでいる（`discs` 列は全機種共通で、カートリッジは 1）。

### 非売品・別リスト

| 振り分け先 | 内容 |
|---|---|
| 非売品（3 件） | ゼルダの伝説 時のオカリナGC（風のタクト予約特典）、パックマンvs.（R:レーシング･エボリューション同梱・クラブニンテンドー入会キャンペーン）、ゼルダコレクション（クラブニンテンドー景品） |
| 別リスト `store_demo`（62 件） | 月刊任天堂店頭デモ（2002〜2006年、54 号分）、店頭実演用サンプル（Redump の `Jitsuen-you Sample`）、店頭体験版 |

Redump の `Taikenban`（体験版）・`Special Taiken Disc`・ムービー体験版は配布経路が確認できていないため載せていない。
非売品の `category` に `preorder`（予約特典）を加えた。

## 再生成

```sh
python3 scripts/fetch_wikipedia_list.py gba   # Wikipedia → data/gba/wikipedia_titles.csv
python3 scripts/enrich.py gba                  # 型番・価格を付与 → data/gba/jp_titles.csv
python3 scripts/build_dumps.py gba             # ROM 吸い出し一覧・別リスト → jp_rom_dumps.csv / jp_non_retail.csv

python3 scripts/fetch_wikipedia_list.py gb
python3 scripts/enrich.py gb                   # ニンテンドウパワー書き換え専用タイトルはここで除く
python3 scripts/build_nintendo_power.py gb     # → data/gb/jp_nintendo_power.csv（enrich の後に実行）
python3 scripts/build_dumps.py gb

python3 scripts/fetch_wikipedia_list.py ds
python3 scripts/fetch_wikipedia_list.py ds --list dsiware   # → data/ds/jp_dsiware.csv
python3 scripts/enrich.py ds                   # maru-chang は 5 秒間隔で 48 ページ取得
python3 scripts/build_dumps.py ds

python3 scripts/fetch_wikipedia_list.py gc
python3 scripts/enrich.py gc                   # maru-chang は 5 秒間隔で 6 ページ取得
python3 scripts/build_dumps.py gc
```

- Wikipedia のページ本文は `.cache/wikipedia/` に保存して再利用する（取り直すときは `--refresh`）。

- スクリプトは機種名（`gba` など）を引数に取る。機種ごとの設定（Wikipedia のページと表の列、
  MADB の機種名、MAME のリスト、No-Intro の DAT 名、型番の形式など）は `scripts/platforms.py` にあり、
  共通処理は `scripts/common.py` にある。
- `enrich.py` は MADB・MAME・No-Intro DAT・maru-chang のデータを `.cache/` にダウンロードして再利用する。
  maru-chang は 5 秒間隔で 16 ページを取得する。
- `build_dumps.py` が使う No-Intro DB Export は、利用規約への同意が必要なため自動取得しない。
  [DAT-o-MATIC](https://datomatic.no-intro.org/) で規約に同意し、Download → Nintendo - Game Boy Advance →
  「DB」の Prepare → Download!! で得た zip を `.cache/nointro-db/` に置く（または `--export` で指定）。
  GB/GBC は Game Boy と Game Boy Color の 2 つを置く。

## ライセンス

`data/` 以下のデータは上記出典を加工したもの。Wikipedia 由来の部分は
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.ja) に従う。
メディア芸術データベース由来の価格は、同データベースのデータセットを加工して作成した。
