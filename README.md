# retro-game-db

Wii 世代（2000年代中盤）までのレトロゲーム情報を収集するデータベース。
まずは**日本国内で発売されたタイトルの一覧**を機種ごとに作成する。

## 収録状況

| 機種 | タイトル一覧 | 件数 | 型番 | 価格 | ROM 吸い出し一覧 |
|---|---|---|---|---|---|
| ゲームボーイアドバンス (GBA) | [`data/gba/jp_titles.csv`](data/gba/jp_titles.csv) | 793 | 792 | 792 | [`data/gba/jp_rom_dumps.csv`](data/gba/jp_rom_dumps.csv)（997 行） |
| ゲームボーイ／ゲームボーイカラー (GB/GBC) | [`data/gb/jp_titles.csv`](data/gb/jp_titles.csv) | 1,245 | 1,194 | 1,199 | [`data/gb/jp_rom_dumps.csv`](data/gb/jp_rom_dumps.csv)（1,375 行） |
| ニンテンドーDS (DS) | [`data/ds/jp_titles.csv`](data/ds/jp_titles.csv) | 1,840 | 1,796 | 1,830 | [`data/ds/jp_rom_dumps.csv`](data/ds/jp_rom_dumps.csv)（2,071 行） |
| ニンテンドー ゲームキューブ (GC) | [`data/gc/jp_titles.csv`](data/gc/jp_titles.csv) | 276 | 272 | 274 | [`data/gc/jp_rom_dumps.csv`](data/gc/jp_rom_dumps.csv)（366 行） |
| Wii | [`data/wii/jp_titles.csv`](data/wii/jp_titles.csv) | 461 | 461 | 461 | [`data/wii/jp_rom_dumps.csv`](data/wii/jp_rom_dumps.csv)（496 行） |
| NINTENDO 64 (N64) | [`data/n64/jp_titles.csv`](data/n64/jp_titles.csv) | 198 | 198 | 144 | [`data/n64/jp_rom_dumps.csv`](data/n64/jp_rom_dumps.csv)（245 行） |
| スーパーファミコン (SFC) | [`data/sfc/jp_titles.csv`](data/sfc/jp_titles.csv) | 1,422 | 1,384 | 1,324 | [`data/sfc/jp_rom_dumps.csv`](data/sfc/jp_rom_dumps.csv)（1,606 行） |
| ファミリーコンピュータ (FC) | [`data/fc/jp_titles.csv`](data/fc/jp_titles.csv) | 1,053 | 1,029 | 367 | [`data/fc/jp_rom_dumps.csv`](data/fc/jp_rom_dumps.csv)（1,320 行） |
| ディスクシステム (FC の別リスト) | [`data/fc/disk_system/jp_titles.csv`](data/fc/disk_system/jp_titles.csv) | 198 | 182 | 23 | [`data/fc/disk_system/jp_rom_dumps.csv`](data/fc/disk_system/jp_rom_dumps.csv)（288 行） |
| メガドライブ (MD) | [`data/md/jp_titles.csv`](data/md/jp_titles.csv) | 422 | 407 | 398 | [`data/md/jp_rom_dumps.csv`](data/md/jp_rom_dumps.csv)（524 行） |
| メガCD (MD の別リスト) | [`data/md/mega_cd/jp_titles.csv`](data/md/mega_cd/jp_titles.csv) | 115 | 110 | 101 | [`data/md/mega_cd/jp_rom_dumps.csv`](data/md/mega_cd/jp_rom_dumps.csv)（120 行） |
| スーパー32X (MD の別リスト) | [`data/md/32x/jp_titles.csv`](data/md/32x/jp_titles.csv) | 18 | 18 | 1 | [`data/md/32x/jp_rom_dumps.csv`](data/md/32x/jp_rom_dumps.csv)（18 行） |
| PCエンジン (PCE) | [`data/pce/jp_titles.csv`](data/pce/jp_titles.csv) | 668 | 656 | 418 | [`data/pce/jp_rom_dumps.csv`](data/pce/jp_rom_dumps.csv)（727 行） |
| セガサターン (SS) | [`data/ss/jp_titles.csv`](data/ss/jp_titles.csv) | 1,058 | 1,000 | 999 | [`data/ss/jp_rom_dumps.csv`](data/ss/jp_rom_dumps.csv)（1,210 行） |
| PlayStation (PS) | [`data/ps/jp_titles.csv`](data/ps/jp_titles.csv) | 3,289 | 2,860 | 2,809 | [`data/ps/jp_rom_dumps.csv`](data/ps/jp_rom_dumps.csv)（3,224 行） |
| PlayStation 2 (PS2) | [`data/ps2/jp_titles.csv`](data/ps2/jp_titles.csv) | 2,930 | 1,144 | 2,689 | [`data/ps2/jp_rom_dumps.csv`](data/ps2/jp_rom_dumps.csv)（1,308 行） |
| ゲームギア (GG) | [`data/gg/jp_titles.csv`](data/gg/jp_titles.csv) | 196 | 188 | 183 | [`data/gg/jp_rom_dumps.csv`](data/gg/jp_rom_dumps.csv)（214 行） |
| SC-3000／SG-1000 (SG) | [`data/sg1000/jp_titles.csv`](data/sg1000/jp_titles.csv) | 74 | 73 | 2 | [`data/sg1000/jp_rom_dumps.csv`](data/sg1000/jp_rom_dumps.csv)（101 行） |
| セガ・マークIII／マスターシステム (SMS) | [`data/sms/jp_titles.csv`](data/sms/jp_titles.csv) | 83 | 82 | 8 | [`data/sms/jp_rom_dumps.csv`](data/sms/jp_rom_dumps.csv)（92 行） |
| カセットビジョン (CV) | [`data/cv/jp_titles.csv`](data/cv/jp_titles.csv) | 11 | 0 | 11 | （出典なし） |
| プレイディア | [`data/playdia/jp_titles.csv`](data/playdia/jp_titles.csv) | 33 | 33 | 0 | （出典なし） |
| スーパーカセットビジョン (SCV) | [`data/scv/jp_titles.csv`](data/scv/jp_titles.csv) | 30 | 0 | 0 | [`data/scv/jp_rom_dumps.csv`](data/scv/jp_rom_dumps.csv)（31 行） |
| バーチャルボーイ (VB) | [`data/vb/jp_titles.csv`](data/vb/jp_titles.csv) | 19 | 19 | 4 | [`data/vb/jp_rom_dumps.csv`](data/vb/jp_rom_dumps.csv)（21 行） |
| PlayStation Portable (PSP) | [`data/psp/jp_titles.csv`](data/psp/jp_titles.csv) | 1,460 | 771 | 1,357 | [`data/psp/jp_rom_dumps.csv`](data/psp/jp_rom_dumps.csv)（781 行） |
| ドリームキャスト (DC) | [`data/dc/jp_titles.csv`](data/dc/jp_titles.csv) | 497 | 481 | 411 | [`data/dc/jp_rom_dumps.csv`](data/dc/jp_rom_dumps.csv)（578 行） |
| Xbox 360 | [`data/x360/jp_titles.csv`](data/x360/jp_titles.csv) | 699 | 58 | 571 | [`data/x360/jp_rom_dumps.csv`](data/x360/jp_rom_dumps.csv)（657 行） |
| Xbox | [`data/xbox/jp_titles.csv`](data/xbox/jp_titles.csv) | 222 | 60 | 179 | [`data/xbox/jp_rom_dumps.csv`](data/xbox/jp_rom_dumps.csv)（214 行） |
| 3DO | [`data/3do/jp_titles.csv`](data/3do/jp_titles.csv) | 214 | 208 | 200 | [`data/3do/jp_rom_dumps.csv`](data/3do/jp_rom_dumps.csv)（219 行） |
| PC-FX | [`data/pcfx/jp_titles.csv`](data/pcfx/jp_titles.csv) | 62 | 61 | 40 | [`data/pcfx/jp_rom_dumps.csv`](data/pcfx/jp_rom_dumps.csv)（65 行） |
| ネオジオ (ROM) | [`data/neogeo/jp_titles.csv`](data/neogeo/jp_titles.csv) | 117 | 115 | 117 | [`data/neogeo/jp_rom_dumps.csv`](data/neogeo/jp_rom_dumps.csv)（ROM チップ 1,449 行・115 タイトル） |
| ネオジオCD (ネオジオの別リスト) | [`data/neogeo/cd/jp_titles.csv`](data/neogeo/cd/jp_titles.csv) | 97 | 97 | 74 | [`data/neogeo/cd/jp_rom_dumps.csv`](data/neogeo/cd/jp_rom_dumps.csv)（102 行） |
| ネオジオポケット／カラー (NGP/NGPC) | [`data/ngp/jp_titles.csv`](data/ngp/jp_titles.csv) | 82 | 79 | 82 | [`data/ngp/jp_rom_dumps.csv`](data/ngp/jp_rom_dumps.csv)（92 行） |
| ワンダースワン／カラー (WS/WSC) | [`data/ws/jp_titles.csv`](data/ws/jp_titles.csv) | 202 | 200 | 181 | [`data/ws/jp_rom_dumps.csv`](data/ws/jp_rom_dumps.csv)（227 行） |
| PlayStation 3 (PS3) | [`data/ps3/jp_titles.csv`](data/ps3/jp_titles.csv) | 982 | 97 | 857 | [`data/ps3/jp_rom_dumps.csv`](data/ps3/jp_rom_dumps.csv)（106 行） |

| 機種 | 非売品 | 店頭体験版・開発版・試作品 | その他 |
|---|---|---|---|
| GBA | [`jp_not_for_sale.csv`](data/gba/jp_not_for_sale.csv)（5 件） | [`jp_non_retail.csv`](data/gba/jp_non_retail.csv)（35 件） | |
| GB/GBC | [`jp_not_for_sale.csv`](data/gb/jp_not_for_sale.csv)（2 件） | [`jp_non_retail.csv`](data/gb/jp_non_retail.csv)（92 件） | ニンテンドウパワー [`jp_nintendo_power.csv`](data/gb/jp_nintendo_power.csv)（153 件） |
| DS | [`jp_not_for_sale.csv`](data/ds/jp_not_for_sale.csv)（13 件） | [`jp_non_retail.csv`](data/ds/jp_non_retail.csv)（35 件） | DSiウェア [`jp_dsiware.csv`](data/ds/jp_dsiware.csv)（493 件） |
| GC | [`jp_not_for_sale.csv`](data/gc/jp_not_for_sale.csv)（3 件） | [`jp_non_retail.csv`](data/gc/jp_non_retail.csv)（62 件） | |
| Wii | [`jp_not_for_sale.csv`](data/wii/jp_not_for_sale.csv)（4 件） | （0 件） | Wiiウェア [`jp_wiiware.csv`](data/wii/jp_wiiware.csv)（210 件） |
| N64 | （未調査・0 件） | [`jp_non_retail.csv`](data/n64/jp_non_retail.csv)（5 件） | 64DD [`jp_64dd.csv`](data/n64/jp_64dd.csv)（10 件） |
| SFC | [`jp_not_for_sale.csv`](data/sfc/jp_not_for_sale.csv)（3 件） | [`jp_non_retail.csv`](data/sfc/jp_non_retail.csv)（9 件） | ニンテンドウパワー [`jp_nintendo_power.csv`](data/sfc/jp_nintendo_power.csv)（179 件） |
| FC | [`jp_not_for_sale.csv`](data/fc/jp_not_for_sale.csv)（9 件） | [`jp_non_retail.csv`](data/fc/jp_non_retail.csv)（9 件） | |
| ディスクシステム | [`jp_not_for_sale.csv`](data/fc/disk_system/jp_not_for_sale.csv)（4 件） | [`jp_non_retail.csv`](data/fc/disk_system/jp_non_retail.csv)（14 件） | |
| MD | （未調査・0 件） | [`jp_non_retail.csv`](data/md/jp_non_retail.csv)（7 件） | 配信専用 [`jp_online.csv`](data/md/jp_online.csv)（46 件） |
| メガCD | [`jp_not_for_sale.csv`](data/md/mega_cd/jp_not_for_sale.csv)（1 件） | [`jp_non_retail.csv`](data/md/mega_cd/jp_non_retail.csv)（1 件） | |
| PCE | [`jp_not_for_sale.csv`](data/pce/jp_not_for_sale.csv)（15 件） | [`jp_non_retail.csv`](data/pce/jp_non_retail.csv)（1 件） | 販売経路不明 [`jp_other.csv`](data/pce/jp_other.csv)（6 件） |
| SS | [`jp_not_for_sale.csv`](data/ss/jp_not_for_sale.csv)（9 件） | [`jp_non_retail.csv`](data/ss/jp_non_retail.csv)（36 件） | |
| PS | （未調査・0 件） | （0 件） | |
| PS2 | （未調査・0 件） | [`jp_non_retail.csv`](data/ps2/jp_non_retail.csv)（店頭体験版 19 件） | |
| GG | （未調査・0 件） | （0 件） | |
| SG | （未調査・0 件） | （0 件） | BASIC・教育用ソフト [`jp_non_game.csv`](data/sg1000/jp_non_game.csv)（26 件。吸い出し [`jp_non_game_rom_dumps.csv`](data/sg1000/jp_non_game_rom_dumps.csv) 20 行） |
| SMS | （未調査・0 件） | [`jp_non_retail.csv`](data/sms/jp_non_retail.csv)（3 件） | |
| プレイディア | [`jp_not_for_sale.csv`](data/playdia/jp_not_for_sale.csv)（2 件） | [`jp_non_retail.csv`](data/playdia/jp_non_retail.csv)（店頭販促用 1 件） | |
| VB | （未調査・0 件） | [`jp_non_retail.csv`](data/vb/jp_non_retail.csv)（試作品 2 件） | |
| PSP | [`jp_not_for_sale.csv`](data/psp/jp_not_for_sale.csv)（1 件） | （0 件） | 配信専用 [`jp_download.csv`](data/psp/jp_download.csv)（104 件） |
| DC | [`jp_not_for_sale.csv`](data/dc/jp_not_for_sale.csv)（1 件） | [`jp_non_retail.csv`](data/dc/jp_non_retail.csv)（店頭体験版 22 件） | |
| Xbox 360 | （未調査・0 件） | （0 件） | ダウンロード専売 [`jp_download.csv`](data/x360/jp_download.csv)（24 件） |
| Xbox | （未調査・0 件） | （0 件） | |
| 3DO | （調査中・0 件） | （0 件） | |
| PC-FX | [`jp_not_for_sale.csv`](data/pcfx/jp_not_for_sale.csv)（雑誌付録 4 件） | （0 件） | |
| ネオジオ | （未調査・0 件） | （0 件） | |
| ネオジオCD | （未調査・0 件） | （0 件） | |
| NGP/NGPC | （未調査・0 件） | （0 件） | |
| WS/WSC | [`jp_not_for_sale.csv`](data/ws/jp_not_for_sale.csv)（3 件） | （0 件） | 会場限定販売 [`jp_other.csv`](data/ws/jp_other.csv)（2 件） |
| PS3 | （未調査・0 件） | （0 件） | 配信専用 [`jp_psn.csv`](data/ps3/jp_psn.csv)（299 件） |

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

## Wii

Wii 用ディスクソフトとして日本で発売されたもの（2006年12月〜2015年）。`id` は `wii-jp-<連番>`（発売順）。
Wiiウェアは別リスト、バーチャルコンソールと Wii チャンネルは対象外。

### 出典

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元 | ja.wikipedia「Wiiのゲームタイトル一覧」（日本の発売日がある行。本文の年別件数どおり 461 件） |
| 型番・価格の補完と照合、発売日の照合 | maru-chang.com Wii ソフトラインナップ（1,372 件のうち、型番が `RVL-R***` / `RVL-S***` のディスクソフトだけを使う） |
| 価格 | メディア芸術データベース（機種「Wii」） |
| 型番の検証・ハッシュ | Redump DAT（libretro-database 収録の `Nintendo - Wii.dat`） |

- 型番・価格・吸い出しは 461 件すべてにある。
- maru-chang が英字表記の作品は、同じ発売日に双方 1 件ずつ残ったもので照合し（45 件、要確認レポートに出る）、
  同日に複数並ぶもの 12 件は [`data/wii/overrides/matches.csv`](data/wii/overrides/matches.csv) で手動対応した。
- 同梱版でしか売られていない作品（Wii Fit のバランスWiiボード同梱など）は同梱版の価格のまま。MADB の価格が maru-chang より
  3 割以上高いもの 11 件はスペシャルパック・本体同梱パック等とみて maru-chang の価格にしている（太鼓の達人Wii、
  ギターヒーロー3 は周辺機器同梱が通常版の可能性があり要確認）。
- 2014年4月以降の発売分は消費税 8% で換算する。

### 非売品（`jp_not_for_sale.csv`）・別リスト

Wikipedia の「非売品」節の 4 件：AQUARIUS BASEBALL（アクエリアスのキャンペーン景品）、ザ・ワールド・オブ・ゴールデンエッグス
NISSAN NOTE オリジナルバージョン（日産ノート試乗キャンペーン景品）、エキサイト猛マシン（クラブニンテンドー景品）、
天空の機士ロデア（Wii U 用ソフトの初回生産分特典として同梱された Wii 版）。

Redump の `Taikenban`（7 件）・`Otameshiban`（1 件）は配布経路が確認できていないため別リストに載せていない（別リストは 0 件）。

### Wiiウェア（`jp_wiiware.csv`）

Wikipedia「Wiiウェアのゲームタイトル一覧」の 210 件（本文は 211 タイトルで、1 件は同ページの非売品節）。
`release_date` は配信開始日、`blocks` は必要ブロック数、`wifi` は Wi-Fi 対応、`classic_controller` はクラシックコントローラ対応。

## N64

NINTENDO 64 用として日本で発売されたソフト（1996〜2001年）。`id` は `n64-jp-<連番>`（発売順）。

### 出典

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元 | ja.wikipedia「NINTENDO 64のゲームタイトル一覧」（本文の記載どおり 198 件。スーパーマリオ64 とウエーブレース64 の振動パック対応バージョンを別の行として含む） |
| 価格（・型番の補助） | メディア芸術データベース（機種「NINTENDO 64」） |
| 型番・発売日の照合 | MAME ソフトウェアリスト `hash/n64.xml` |
| 型番の検証・ハッシュ | No-Intro DAT（libretro 収録の `Nintendo - Nintendo 64.dat`。DB Export は未取得） |

- maru-chang には N64 の一覧が無いため、照合は Wikipedia・MADB・MAME の 3 つ。
- 型番は `NUS-XXXJ-JPN`。198 件すべてにあり（MAME で照合できない 3 件は [`data/n64/overrides/matches.csv`](data/n64/overrides/matches.csv)
  で補った。うち CITY TOUR GRANDPRIX は No-Intro のゲームコード）。
- 価格は MADB だけが出典のため 144 件。54 件は価格なし。発売は 1997年3月までが消費税 3%、以降 5% で、すべて税抜表示の時代。
- 周辺機器同梱ソフト（ピカチュウげんきでチュウ＋VRS など）は本リストに含む。
- 非売品は未調査（Wikipedia の一覧に非売品の節が無いため、各作品の記事の確認が必要）。
- No-Intro の `GameCube`（GC 用『ゼルダコレクション』等に収録された ROM）は `collection` として扱う。

### 64DD（`jp_64dd.csv`）

64DD（磁気ディスクドライブ）用ソフト 10 件の別リスト（Wikipedia の「発売された64DDのタイトル」）。
ランドネットディスク（通信サービス用）を含む。ハッシュ（No-Intro の 64DD DAT）は未収録。

## SFC

スーパーファミコン用として日本で発売されたソフト（1990〜2000年）。`id` は `sfc-jp-<連番>`（発売順）。
サテラビュー（BS 放送で配信されたソフト）は対象外。

### 出典

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元 | ja.wikipedia「スーパーファミコンのゲームタイトル一覧」（日本の発売日がある行。本文の記載どおり 1,447 件、年別件数も一致） |
| 価格（・型番の補助） | メディア芸術データベース（機種「スーパーファミコン」） |
| 型番・発売日の照合 | MAME ソフトウェアリスト `hash/snes.xml`・`hash/snes_strom.xml`（スーファミターボ） |
| ハッシュ | No-Intro DAT（libretro 収録の SNES・Sufami Turbo。DB Export は未取得） |
| ニンテンドウパワー | ja.wikipedia「ニンテンドウパワーのゲームタイトル一覧」スーパーファミコンの表 |

- 本リストは 1,422 件。ニンテンドウパワーの書き換え専用タイトル 25 件（ピクロスNP、スーパーパンチアウト!!、
  ダービースタリオン98 など）は別リストに移した。
- `media` 列: `cartridge` / `sufami_turbo`（スーファミターボ専用ソフト 13 件。型番は `SFT-0101-JPN` 形式）。
- 型番は初期が `SHVC-FZ` のような 2〜3 文字、後期が `SHVC-XXXJ-JPN`。型番なし 38 件、価格なし 98 件。
- maru-chang に SFC の一覧は無いため、照合は Wikipedia・MADB・MAME の 3 つ。消費税は 1997年3月まで 3%、以降 5%（税抜表示）。
- 発売日: MADB と MAME がそろって Wikipedia と異なる日付を持つものが 9 件ある（牧場物語 1996-08-06 → 両出典は 08-09 など）。
  Wikipedia の誤りの可能性が高いが、現時点では修正せず要確認レポートに出している。

### 非売品（`jp_not_for_sale.csv`）・別リスト

Wikipedia「その他」節の 6 件を振り分けた。

| 振り分け先 | 内容 |
|---|---|
| 非売品（3 件） | もと子ちゃんのワンダーキッチン（味の素マヨネーズの懸賞品）、パチンコ鉄人七番勝負（パチンコ店の景品）、鮫亀キャラデータ集（大会景品） |
| 別リスト `business`（3 件） | ゲットインザホール（ゴルフシミュレータ専用）、JRA PAT／JRA PAT ワイド対応版（NTT データ通信セット専用の競馬投票ソフト） |

No-Intro の `Sample`・`Auto Demo`・`Enhancement Chip` は製品版から除き、`Capcom Town`・`Columbus Circle`（後年の再発売）は
`collection` とした。別リストはほかに試作品 6 件。

### ニンテンドウパワー（`jp_nintendo_power.csv`）

GB と同じ形式の別リスト（179 件、うち書き換え専用 26 件）。No-Intro の `(NP)` の吸い出し 50 件のうち 48 件を
対応づけた（書き換え専用タイトルは [`data/sfc/overrides/np_dump_matches.csv`](data/sfc/overrides/np_dump_matches.csv)）。

## FC

ファミリーコンピュータ（ROM カセット）として日本で発売されたソフト（1983〜1994年）。`id` は `fc-jp-<連番>`（発売順）。
ディスクシステムは別リスト（[`data/fc/disk_system/`](data/fc/disk_system/)、`id` は `fds-jp-<連番>`）。
非ライセンス品（当時のもの・後年の同人ソフト）とファミコン通信アダプタ用カードは対象外。

### 出典

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元 | ja.wikipedia「ファミリーコンピュータのゲームタイトル一覧」（日本の発売日がある行。本文の記載どおり 1,053 件、年別件数も一致）、「ファミリーコンピュータ ディスクシステムのゲームタイトル一覧」（198 件、年別件数も一致） |
| 価格（・型番の補助） | メディア芸術データベース（機種「ファミリーコンピュータ」。カセット 415 件・ディスクカード 26 件しかない） |
| 型番・発売日の照合 | MAME ソフトウェアリスト `hash/nes.xml`・`nes_datach.xml`・`nes_kstudio.xml`、ディスクは `famicom_flop.xml` |
| ハッシュ | No-Intro DAT（libretro 収録の NES・Famicom Disk System。DB Export は未取得） |

- 周辺機器の専用・同梱ソフト（データック、カラオケスタジオ、ファミリートレーナー、ロボット、ファミリーベーシックなど）は本リストに含む。
- 型番は会社ごとに形式が違う（`HVC-SM`、`NAM-NXV-4900`、`TFC-KD-4900`、`IF-02` など）ため、表記のまま載せる。
  優先順位は他機種と同じく MAME → MADB。両者で表記が違うもの（MAME `NAM-NXV-4900`／MADB `NXV-4900` など 30 件）は
  要確認レポートに出している。MAME が独自に付けた番号（`DATACH-…` など）は採らない。
- 価格は MADB にあるものだけ（FC 367 件、ディスク 23 件。他は空欄）。1989年3月以前の発売は `price_tax` を `税なし` とした。
- 題名の表記が出典ごとに大きく違う（『ダブルドラゴン』と MAME の『双截龍』など）ため、FC では同じ発売日に照合できていない行と
  候補がちょうど1件ずつ残ったときに組にしている（要確認レポートに「同日1件のみで照合」と出す。誤りの 2 件は
  `overrides/matches.csv` で外した）。
- 発売日: MADB と MAME がそろって Wikipedia と異なるものが 5 件ある（ロードランナー 1984-07-20 → 両出典は 07-31、
  バンゲリング ベイ、激突四駆バトル、井崎脩五郎の競馬必勝学、テクモボウル）。現時点では修正せず要確認レポートに出している。

### ハッシュ

- FC は iNES ヘッダーを除いた ROM 本体（No-Intro の `.unh`）のハッシュ。ヘッダー付き（`.nes`）は載せない。
- FC の ROM にはゲームコードが無く、No-Intro の DAT にもシリアルが無いため、吸い出しとタイトルは
  MAME のチップ別（PRG・CHR）の CRC をつないだ CRC、No-Intro 名、手動対応（`overrides/dump_matches.csv`）で結びつけた。
  『スーパーマリオブラザーズ』など日米共通の `(World)` の吸い出しも含む。製品版の吸い出しがあるのは 1,052/1,053 件
  （無いのは『ベストプレープロ野球 新データ』）。
- ディスクシステムは `.fds`（`.qd` は載せない）。ディスク内のゲームコードの先頭3文字と型番の末尾（`SSD-ADA` ↔ `ADA`）で
  結びつけ、198 件すべてに吸い出しがある。ディスクの版（No-Intro の `DV n`）は `revision` 列に `DV 2` のように入れる。
  書き換えで作られたディスク（`Disk Writer`）は製品版の別の吸い出しとして同じタイトルに結びつけている。

### ディスクシステム（`data/fc/disk_system/jp_titles.csv`）

本リストと同じ列に、Wikipedia の表の列から次を加えた。

| 列 | 内容 |
|---|---|
| `sales_channel` | `both`（書き換え・パッケージ両方、154 件）／`rewrite_only`（書き換え専用、34 件）／`package_only`（パッケージ販売専用、10 件） |
| `port_of_cartridge` | ROM カセット版からの移植なら `yes` |
| `single_sided` | 片面ソフトなら `yes` |

価格（`price_yen`）は MADB のパッケージ版の価格。書き換え料金の出典は無い。

### 非売品（`jp_not_for_sale.csv`）・別リスト

Wikipedia の「非売品」節（FC 10 行・ディスク 5 行）を振り分けた。それ以外の調査は後回し
（No-Intro には『Tag Team Pro-Wrestling Special』『安田火災 セーフティラリー』の Not for Resale 版などもある）。

| 振り分け先 | 内容 |
|---|---|
| FC 非売品（9 件） | NHK学園 スペーススクール 算数 4〜6年 上下（6 件・`educational`）、SPACE COLLEGE（`educational`）、ドンキーコングJR.&算数レッスン（ファミコンテレビC1 同梱・`bundled`）、ファミリースクール（第一生命の販促品・`promotional`） |
| ディスク非売品（4 件） | オールナイトニッポン スーパーマリオブラザーズ、ゴルフJAPANコースの景品（チャンピオンズコース・プロフェッショナルコースの2種）、プライズカード ゴルフスペシャルコース（いずれも `prize`） |
| ディスク別リスト | FMCカードチェッカー（`business`）、惑星アトン外伝（国税庁の展示・税務署で遊べた。`event_demo`） |
| 対象外 | ファミコレADV シュタインズ・ゲート（2018年・配布なし）、Nintendo Campus Challenge／Nintendo World Championships（北米の大会用） |

吸い出しがあるのは、NHK学園は 3 本（5年上・6年上・6年下）。ゴルフJAPANコースの景品は No-Intro のシリアル `GSJE` が
プロフェッショナルコースに当たる。別リストにはほかに試作品（FC 9 件・ディスク 12 件）。

## MD

メガドライブ（カートリッジ）として日本で発売されたソフト（1988〜1996年）。`id` は `md-jp-<連番>`（発売順）。
メガCD（[`data/md/mega_cd/`](data/md/mega_cd/)、`mcd-jp-…`）とスーパー32X（[`data/md/32x/`](data/md/32x/)、`32x-jp-…`）は
別リストで、列は本リストと同じ。メガLD・キッズコンピュータ ピコ・非ライセンス品は対象外。

### 出典

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元 | ja.wikipedia「メガドライブのゲームタイトル一覧」（セガ公式のソフトウェア一覧が出典。日本 468 件・年別件数とも本文と一致）、「メガCDのゲームタイトル一覧」（114 件）、「スーパー32Xのゲームタイトル一覧」（18 件） |
| 価格（・型番の補助） | メディア芸術データベース（機種「メガドライブ」。カートリッジのうち型番 `GM-` は 32X、CD-ROM はメガCD に振り分け） |
| 型番・発売日の照合 | MAME ソフトウェアリスト `hash/megadriv.xml`・`megacd.xml`・`32x.xml` |
| ハッシュ | No-Intro DAT（libretro 収録の Mega Drive・32X）、Redump DAT（libretro 収録の Mega-CD） |

- Wikipedia の 468 件のうち、配信専用の 46 件（ゲーム図書館 36・セガチャンネル 8・MEGAターミナル 2）は
  [`jp_online.csv`](data/md/jp_online.csv)（`service` 列）に分け、本リストは 422 件。『コラムス』のように
  カートリッジでも発売されたものは本リストに残す。配信専用リストにはハッシュを付けていない。
- 型番は表記のまま（セガ `G-4128`、ライセンシー `T-66013`、32X `GM-4002`、エレクトロニック・アーツ・ビクター `EM20003`）。
  MAME の `G-5514 (Jpn), MK-1135-50 (Euro)` のような並記からは日本版の部分を取る。
  MAME と MADB で番号が違うもの（ヴァーミリオン、アウトランなど本リスト 5 件・メガCD 3 件）は要確認レポートに出している。
- ROM ヘッダのコードはパッケージの型番と一致しないことが多い（獣王記 `G-4001` ↔ `00054002-00`、32X は `MK-84508-00`）ため、
  型番の検証にも吸い出しとの対応にも使わない。吸い出しは MAME の CRC・No-Intro 名・手動対応で結びつけた
  （本リスト・メガCD・32X とも全タイトルに製品版の吸い出しがある）。メガCD は Redump のシリアル（レーベル面の型番）で結びつける。
- 価格は本リスト 398 件・メガCD 101 件。32X は MADB に 2 件しかなく 1 件だけ。1989年3月以前の発売（5 件）は `税なし`。
- メガCD のハッシュは libretro 版 Redump DAT に載っている最初のトラック（データトラック）のもの。
- No-Intro の `Sega Game Toshokan`・`Sega Channel` の吸い出しは `dump_kind` を `online`、メガドライブミニ・ゲームのかんづめ・
  セガエイジスなどの収録版は `collection` とした。
- 非売品の調査は後回し（本体の一覧に「非売品」節が無い）。メガCD の「その他」節の 2 件は、ワンダーメガ コレクション
  （ワンダーメガ本体に付属）を非売品（`bundled`）、SING!!（ゲームを収録した市販の音楽アルバム）をメガCD の一覧に追加した。

## PCE

PCエンジンとして日本で発売されたソフト（1987〜1999年）。`id` は `pce-jp-<連番>`（発売順）。HuCARD と CD-ROM は1つのリストで、
`format` 列で区別する。PC-FX・LD-ROM²（レーザーアクティブ）・北米の TurboGrafx 専用ソフトは対象外。

### 出典

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元・規格 | ja.wikipedia「PCエンジンのゲームタイトル一覧」の HuCARD 系・CD-ROM 系の2つの表（日本 666 件。本文の規格別件数と一致） |
| 価格（・型番の補助） | メディア芸術データベース（機種「PCエンジン」） |
| 型番・発売日の照合 | MAME ソフトウェアリスト `hash/pce.xml`（日本版のみのリスト）・`sgx.xml`・`pcecd.xml` |
| ハッシュ | No-Intro DAT（libretro 収録の PC Engine・SuperGrafx）、Redump DAT（libretro 収録の PC Engine CD） |

| 列 | 内容 |
|---|---|
| `format` | `hucard`（279）／`supergrafx`（スーパーグラフィックス専用、5）／`cd_rom2`（120）／`super_cd_rom2`（252）／`arcade_card`（アーケードカード専用、12）。両対応ソフトはパッケージの表記による（Wikipedia の分類どおり） |
| `genre` | Wikipedia の「種類」列の略号（ACT・ADV・RPG・SLG・STG など） |

- 668 件 = Wikipedia の 666 件 ＋「体験版・雑誌/ムック付録」節の 2 件。『スーパーCD-ROM²体験ソフト集』（定価 1,000 円）と
  『スナッチャー パイロットディスク』（安価で発売）は市販品だったので本リストに入れた（`overrides/extra_titles.csv`）。
- 型番は表記のまま（ハドソン `HC62005`、NEC `H49G-1001`、`NAPR-1051`、CD `HCD0008` など）。ハイフン・空白の有無の違いは照合では
  同じとみなす。MAME と MADB で違うもの 18 件（MADB の `TPO2008` のような O と 0 の誤記が多い）は要確認レポートに出している。
- 価格は 418 件（他は空欄）。1989年3月以前の発売は `税なし`。
- 発売日: MADB と MAME がそろって Wikipedia と異なるものが 6 件（スペースインベーダーズ 復活の日、ゴールデンアックス、
  ROMカラオケ Vol.5、レミングス、三國志III、聖戦士伝承・雀卓の騎士）。修正せず要確認レポートに出している。

### ハッシュ

- HuCARD・スーパーグラフィックスは No-Intro、CD は Redump のデータトラック（通常 Track 02。libretro 版 DAT に載っている1本）。
- CD は Redump のシリアル（レーベル面の型番）で結びつける。HuCARD は DAT にシリアルが無いため MAME の CRC・名前・手動対応で結びつけた。
  製品版の吸い出しが無いのは 3 件（ROMカラオケ Vol.5、パラディオン、真怨霊戦記）。
- libretro 版 Redump DAT には同名の game が複数あることがある。同じハッシュならシリアルを `;` でつないで1つにまとめ
  （GC のシリアル違い、PCE CD『うる星やつら』の HCD0011・HCD0012 など）、ハッシュが違えば ROM のファイル名（`(Alt)` など）を名前にして別の吸い出しとして残す。
  別の DAT に同名がある場合（HuCARD 版と CD 版の『ドラえもん のび太のドラビアンナイト』）は CD 側に ` [2]` を付ける。

### 非売品（`jp_not_for_sale.csv`）・別リスト

| 振り分け先 | 内容 |
|---|---|
| 非売品（15 件） | 天外魔境 電々の伝（ハドソン会報誌の定期購読会員などに配布・`member`）、雑誌・ムックの付録 14 件（PCエンジンハイパーカタログ1〜6、DUO-RX 発売記念ハイパーカタログ、DUO COMIC 爆れつハンター、秋山仁の数学ミステリー、でべろスターターキット アセンブラ編・BASIC 編、DEVELO Magazine、PC Engine FAN Special CD-ROM² Vol. 1、もってけたまご。`supplement`） |
| 別リスト `event_demo`（1 件） | ハイテク王国（ハドソン全国キャラバン大会の会場用。吸い出しは見つからない） |
| 販売経路不明 [`jp_other.csv`](data/pce/jp_other.csv)（6 件） | Wikipedia「その他」節の NECホームエレクトロニクスの幼児向け学習ソフト（あっちこっちどっち など） |

付録の『でべろスターターキット アセンブラ編』は Redump で製品版『ヴァージン・ドリーム』と同じシリアルになっているため、
`overrides/dump_matches.csv` で製品版に結びつけないようにした（`title_id` が `-`）。その他の非売品（Redump にある『天外魔境 ZIRIA』の非売品版など）の調査は後回し。

## SS

セガサターンとして日本で発売されたソフト（1994〜2000年）。`id` は `ss-jp-<連番>`（発売順）。Wikipedia と同じく廉価版
（サタコレなど）は本リストに入れず、その吸い出しは `collection` として元のタイトルに結びつける。

### 出典

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元 | ja.wikipedia「セガサターンのゲームタイトル一覧」（セガ公式のソフトウェア一覧が出典。本文の記載は 1,057 件だが表は 1,058 行で、1997年が 1 行多い） |
| 価格（・型番の補助） | メディア芸術データベース（機種「セガサターン」） |
| 型番・発売日の照合 | MAME ソフトウェアリスト `hash/saturn.xml` |
| ハッシュ | Redump DAT（libretro 収録の Sega Saturn。データトラック） |

- `age_rating` 列: Wikipedia の備考に「X指定」とあれば `X`（22 件）、「18歳以上推奨」とあれば `18+`（92 件）。
- 型番は表記のまま（セガ `GS-9001`、ライセンシー `T-14301G`）。海外版（`T-…H`、`MK-…`）やセガの商品番号 `610-…` は優先しない。
  MAME と MADB で番号が違うもの 11 件は要確認レポートに出している。
- 吸い出しは Redump のシリアル（型番）で結びつけ、MAME に無いタイトルなど 69 件は `overrides/dump_matches.csv` で手動対応。
  複数枚組は1行にまとめる（ディスクごとの呼び名 `(Game Disc)` やマスタリングの印 `(2M)` は組の判定で無視し、同じ番号の
  ディスクが複数あるものはまとめない）。製品版の吸い出しが無いのは 20 件で、大半はバリューセットやベストコレクションなどのセット商品
  （単体では NiGHTS、バーチャレーシング、スコーチャーが libretro 版 DAT に無い）。
- 発売日: MADB と MAME がそろって Wikipedia と異なるものが 5 件（アイドル麻雀ファイナルロマンス2、アースワーム・ジム2、
  出世麻雀 大接待、ウィザーズハーモニー2、ファーランドサーガ 時の道標）。修正せず要確認レポートに出している。

### 非売品（`jp_not_for_sale.csv`）・別リスト

Wikipedia「非売品」節の 29 件について配布経路を調べ、出典（Wikipedia の本文・各作品の記事、富士通の報道資料、4Gamer、
Sega Retro）で経路を確認できたものだけ載せた。Sega Retro（ファンのデータベース）だけを根拠にしたものは `notes` にそう書いている。

| 振り分け先 | 内容 |
|---|---|
| 非売品（6 件） | シャイニングフォース3 プレミアムディスク（応募券をそろえて応募）、ジャワティオリジナル バーチャファイターキッズ（ジャワティーの景品）、ソウルハッカーズ EXTRAダンジョン（『悪魔全書 第二集』のはがきで抽選）、デリソバデラックス（東京フレンドパークIIの視聴者プレゼント）、Dragon's Dream（クライアント CD を申込者に無償配布・`free_distribution`）、BAROQUE REPORT CD DATA FILE（店頭配布の冊子のはがきで入手・`promotional`）、
BIG THANKS スーパー競輪（競輪50周年記念イベントの来場者に配布・`event`）、でべろマガジンVol.2（雑誌の付録・`supplement`）、
パッドニフティ（市販のセガサターンモデムに同梱・`bundled`） |
| 別リスト `store_demo`（33 件） | フラッシュ・セガサターン（Wikipedia ではソフト販売店向けのデモ集。Sega Retro はセガクラブ会員への無料配布とする）。Redump にある お近づき編・Vol.1〜32 を1巻1行で |
| 載せていない（経路が未確認） | オレゴン&ベーシック welcome to アイフルホーム、きゃんバニ日めくりカレンダー、ファイナルロマンス 着せかえディスク、アイアンフック、雀帝 原画集、セガサターンインターネット（Vol.1・Vol.2・スペシャルディスク）、帝国華撃団隊員名簿（Sega Retro も「報道関係者に配布（?）」と留保）、電波少年的ゲーム2、バーチャファイターCGポートレート（コレクション・デュラル）、ハイムワルツ、野村ホームトレード（「一般販売せず配布」とあるが対象不明）、ジグソーパズルカタログ、ルース。通販サイトの商品説明・個人ブログ・検索結果の抜粋でしか経路が分からないものもここに含めた |
| 市販品だった | ワープロソフト EGWORD ver1.0（プリンタ同梱で発売）・ver2.0（発売。Wikipedia「EGWORD」）、ピクトフラッシュ どんどん（Sega Retro では定価 15,800 円） |

Redump の `(Java Tea Original)` は製品版『バーチャファイターキッズ』に結びつけない（非売品として扱う）。

## PS

PlayStation（初代）として日本で発売されたソフト（1994〜2004年）。`id` は `ps-jp-<連番>`（発売順）。

### 出典

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元 | ja.wikipedia「PlayStationのゲームタイトル一覧」の年別 9 ページ（全 3,289 件。各ページの記載件数の合計と一致）。再販の廉価版（PlayStation the Best など）は載っていないが、SIMPLE1500 など最初から廉価で出たシリーズや一部の廉価レーベル（本格派DE1,300円、Major Wave など）は載っている |
| 価格（・型番の補助） | メディア芸術データベース（機種「プレイステーション」） |
| 型番・発売日の照合 | MAME ソフトウェアリスト `hash/psx.xml`（日本版は約 1,000 件と一部だけ） |
| 型番の補完 | psxdatacenter.com の日本版の作品別ページ（4,813 件。型番・発売日・ローマ字／英語の題名） |
| ハッシュ | Redump DAT（libretro 収録の Sony PlayStation。データトラック） |

- 型番は表記のまま（SCE `SCPS-10001`、他社 `SLPS-01234`・`SLPM-86001` など）。複数枚組は先頭ディスクの型番で、枚数は
  吸い出し一覧の `discs` 列。型番があるのは 2,860 件（MADB・MAME で 2,072 件、psxdatacenter で 788 件を補完）。
- psxdatacenter には日本語の題名が無いので、Wikipedia の題名を pykakasi でローマ字にし、発売日が同じ作品のうち題名が
  十分似ている（0.5 以上）ものだけを採った（`model_number_source` が `psxdatacenter`。0.7 未満は要確認レポートに出す）。
  - SIMPLE1500・SuperLite1500 などのシリーズ物は、共通のシリーズ名だけで似ていると判定されないよう、シリーズ名を除いた
    部分どうしも 0.5 以上似ていることを求め、巻数（Vol.）が違うものは採らない。
  - 同じ発売日に残った行と候補が1件ずつでも、題名が似ていなければ組にしない（試すと約半数が別作品だったため）。
- 吸い出しは Redump のシリアル（型番）で結びつけるので、型番の無いタイトルには吸い出しも付かない（製品版の吸い出しがあるのは 2,781 件）。
  名前での手動対応は行っていない。
- 価格は 2,809 件。消費税は発売日に応じて 3%・5%、2004年4月以降は総額表示。
- 再販の印（`PlayStation the Best`、`PSone Books`、`Major Wave`、`Honkakuha de 1300`、`Artdink Best Choice` など）の吸い出しは `collection`。
  体験版（`Demo n`・`Taikenban`）は製品版に結びつけない。
- 要確認レポートでは、MAME の収録が少ないため「MAME未照合」は出さない。MADB と MAME がそろって Wikipedia と異なる発売日は
  2 件（くるみミラクル、プリズムコート）。
- 非売品・体験版の調査は後回し（Wikipedia に「非売品」節が無い）。

## PS2

PlayStation 2 として日本で発売されたソフト（2000〜2013年）。`id` は `ps2-jp-<連番>`（発売順）。

### 出典

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元 | ja.wikipedia「PlayStation 2のゲームタイトル一覧」の年別ページ（2000〜2007年）と一覧ページ本体の 2008〜2013年の節。本文の記載は 2,927 件で、表は 2,930 行 |
| 価格（・型番の補助） | メディア芸術データベース（機種「プレイステーション2」） |
| ハッシュ | Redump DAT（libretro 収録の Sony PlayStation 2） |

- MAME に PS2 のソフトウェアリストは無いため、型番は MADB（906 件）と psxdatacenter.com の日本版一覧（238 件）から取り、
  型番があるのは 1,144 件（無いものは許容。合意済み）。psxdatacenter には日本語の題名も発売日も無いので、Wikipedia の題名を
  pykakasi でローマ字にして、とても似ていて（0.85 以上）ほかに候補の無いものだけ採った（`model_number_source` が `psxdatacenter`。シリーズ物の扱いは PS と同じ）。
  吸い出しは Redump のシリアル（型番）で結びつけるので、製品版の吸い出しがあるのは 1,112 件。
- 価格は 2,689 件（無いものは許容）。2004年4月以降は総額表示（`税込`）。
- 型番の形式は PS と同じ（`SLPM-66213` など。複数枚組は先頭ディスク）。
- Wikipedia の表で発売日の欄が空の『ドラゴンクエストVIII』は、作品の記事の 2004年11月27日にした（`platforms.py` の `date_fixes`）。
- Redump の版番号（`v1.01`・`v2.00` など）は `revision` 列。`PlayStation 2 the Best` は `collection`。店頭用体験版
  （`Tentou-you Taikenban`・`Tentou Taikenban`）は別リストの `store_demo`、その他の体験版（`Taikenban`）は載せない。
- 非売品（Wikipedia「非売品」節のマクドナルドオリジナル ハッピーディスクを含む）と CERO 年齢区分は後回し。

## PS3

PlayStation 3 のパッケージソフトとして日本で発売されたもの（2006〜2018年）。`id` は `ps3-jp-<連番>`（発売順）。
配信専用タイトルは別リスト [`jp_psn.csv`](data/ps3/jp_psn.csv)（299 件。ハッシュなし）。ゲームアーカイブス等の旧作配信は対象外。

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元・オンライン・3D | ja.wikipedia「PlayStation 3のゲームタイトル一覧」の「パッケージタイトル」「配信専用タイトル」の表（本文の記載は 976 件で、表は 982 行。廉価版は載っていない） |
| 価格（・型番の補助） | メディア芸術データベース（機種「プレイステーション3」。ダウンロードコンテンツは除く） |
| ハッシュ | Redump DAT（libretro 収録の Sony PlayStation 3） |

| 列 | 内容 |
|---|---|
| `online` | 一覧の「オ」列。`yes`＝オンラインプレイ対応（451 件）、`only`＝オンライン専用（20 件） |
| `stereo3d` | 一覧の「3」列。`yes`＝3D 立体視対応（46 件） |

- 型番（`BLJM-60001`・`BLJS-10001`・`BCJS-30001` など）の出典は MADB の 148 件だけで、型番があるのは 97 件。
  吸い出しは型番で結びつけるので、製品版の吸い出しがあるのも 96 件（型番・価格・ハッシュが無いことは許容。合意済み）。
- 価格は 857 件。MADB の表記（税込・税抜）のまま。
- 一覧のタイトルの後に付いている説明の無い「*」は除いた。
- 非売品と CERO 年齢区分は後回し。

## GG

ゲームギアとして日本で発売されたソフト（1990〜1996年）。`id` は `gg-jp-<連番>`（発売順）。

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元 | ja.wikipedia「ゲームギアのゲームタイトル一覧」（セガ公式の一覧が出典。日本 196 件、本文と一致） |
| 価格（・型番の補助） | メディア芸術データベース（機種「ゲームギア」） |
| 型番・発売日の照合 | MAME ソフトウェアリスト `hash/gamegear.xml` |
| ハッシュ | No-Intro DAT（libretro 収録の Sega Game Gear） |

- 非ライセンス品・マスターシステムのソフト（コンバーター経由）・TV チューナーは対象外。キッズギア同梱版は通常版と同じ行。
- 本体同梱でしか売られなかった『なぞぷよ』は本リストに入れ、価格は同梱版のもの。キャラクターパック（本体同梱版）は単体版の行に含めた。
- 型番は表記のまま（セガ `G-3327`、ライセンシー `T-44017`）。MAME の並記からは日本版を取り、再販の名作コレクションの型番は採らない。
- No-Intro にシリアルが無いので、吸い出しは MAME の CRC・名前・手動対応（13 件）で結びつけた。製品版の吸い出しが無いのは
  『T2 ジャッジメントディ』の 1 件。日米共通の `(World)` などの吸い出しも含む。
- 『颯爽少年英雄伝 コカ・コーラキッド』の景品のプラスワンセット（本体とのセット）は別のソフトではないので非売品リストに入れていない
  （Wikipedia の備考に記載）。その他の非売品の調査は後回し。

## SG

SC-3000・SG-1000（SG-1000II を含む）として日本で発売されたゲームソフト（1983〜1987年）。SG-1000 互換のオセロマルチビジョン用
（ツクダオリジナル発売）も同じ一覧に載っているので本リストに入れた。`id` は `sg1000-jp-<連番>`（発売順）。

| 列 | 内容 |
|---|---|
| `system` | `sc_sg`（セガ発売の SC-3000／SG-1000 用。66 件）/ `othello_mv`（ツクダオリジナル発売のオセロマルチビジョン用。8 件） |
| `media` | `cartridge`（ゲームカートリッジ For SC/SG）/ `card`（セガ マイカード）/ `cartridge;card`（カートリッジの後にマイカードで再販。5 件） |
| `card_model_number` | マイカードで再販されたものの、マイカードの型番（`model_number` はカートリッジの型番） |
| `release_date_text` | Wikipedia の発売時期の表記そのまま |

| 用途 | 出典 |
|---|---|
| タイトル・発売時期・発売元・媒体 | ja.wikipedia「SG-1000のゲームタイトル一覧」の「タイトルリスト」の表（86 行のうち未発売 12 行を除いた 74 件） |
| 価格（・型番の補助） | メディア芸術データベース（機種「SC-3000,SG-1000」など。12 件で価格は 3 件だけ） |
| 型番の照合 | MAME ソフトウェアリスト `hash/sg1000.xml`（発売日の記録は無い） |
| ハッシュ | No-Intro DAT（libretro 収録の Sega SG-1000） |

- 発売時期は日まで分かるものが少ない（『ゲームマシン』の記事などが出典で、セガハード大百科にも明確な発売日が無い）。`release_date` は
  分かる精度にした: 日まで（6 件）は `YYYY-MM-DD`、月まで（上旬・中旬・下旬を含む。59 件）は `YYYY-MM`、季節（「1986年夏」）・
  範囲（「1983年11-12月」）・疑問符付きは `YYYY`（9 件）。元の表記は `release_date_text`。
- 本文の年ごとの本数（1984年のカートリッジ 16 本など）と表の行数が 1 件合わない（表の 1984年のカートリッジは 15 件）。Wikipedia の表のとおりにした。
- MAME に発売日が無いので、題名がとても似ている（0.8 以上）ものだけを照合し、残りは `overrides/matches.csv` で手動対応した（日本語題名の
  表記が違うもの、マイカード版・台湾版と区別が必要なものなど 14 件）。
- 型番は表記のまま（カートリッジ `G-1033`、マイカード `C-33`、オセロマルチビジョン `OM-G004`）。型番が無いのは『ロレッタの肖像』の 1 件
  （MAME・No-Intro とも収録なし。吸い出しも無い）。
- 価格は 2 件（倉庫番・チャンピオンシップロードランナー。無いものは許容）。全て消費税導入前の発売なので `税なし`。
  チャンピオンボクシングの MADB の価格（4,300円）はマイカード版のものなので採らない。
- 吸い出しは日本版と日本・海外共通の版（`(Japan, Europe)` など）。台湾版は載せない。マイカード再販版は No-Intro で区別されていないので同じ行に含まれる。
- 未発売・発売不明のタイトル、カセットテープのソフト（MAME の `sc3000_cass`）は対象外。EPマイカード（書き換え可能なマイカードの計画）の
  対象ラインナップは備考にだけ残る。非売品の調査は後回し（Wikipedia に「非売品」節が無い）。

### BASIC・教育用ソフト（別リスト）

SC-3000 専用の BASIC（7 件）と教育用ソフト（19 件）は `jp_non_game.csv`（`category` が `basic` / `education`）。
No-Intro に無いため、型番とハッシュは MAME の `hash/sc3000_cart.xml` から取った（`scripts/build_mame_list.py`。対応は
`overrides/non_game_mame.csv` で手で決めた）。

- 教育用ソフト 16 件に型番（`E-101` など）と吸い出し（`jp_non_game_rom_dumps.csv`。MAME の別版〈40k map など〉を含め 20 行。
  `hash_source` は `MAME`）がある。
- BASIC は MAME の版（「BASIC Level 2」「version 1.0b」など）と製品名（Level IIA・IIB など）の対応が決められないため結びつけていない。
- 物理（運動と力編・エネルギー編）は MAME に無い。発売不明のミュージック(SK)は載せない。

## SMS

セガ・マークIII とマスターシステムとして日本で発売されたソフト（1985〜1989年）。両機は同じソフトが動くので 1 本のリストにまとめた。
SG-1000・SC-3000 のソフト（マークIII でも動く）はここに含めず、別のリストにする。`id` は `sms-jp-<連番>`（発売順）。

| 列 | 内容 |
|---|---|
| `media` | `card`（マイカード マークIII）/ `cartridge`（セガのゴールドカートリッジ・サリオのシルバーカートリッジ） |
| `capacity` | 容量（カードは全て `256k`。カートリッジは `1M`・`2M`・`4M`） |
| `fm_sound` | FM 音源対応（`yes`。Wikipedia の「FM音源」欄。41 件） |

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元・媒体・FM 音源 | ja.wikipedia「セガ・マークIIIのゲームタイトル一覧」の「発売されたタイトル」の表（日本 83 件。セガハード大百科の一覧が出典で、発売年ごとの表の合計とも一致） |
| 価格（・型番の補助） | メディア芸術データベース（機種「SEGAマーク3」「SEGAマーク3,セガ・マスターシステム」。25 件で価格は 8 件だけ） |
| 型番・発売日の照合 | MAME ソフトウェアリスト `hash/sms.xml` |
| ハッシュ | No-Intro DAT（libretro 収録の Sega Master System - Mark III） |

- 媒体の欄は地域ごとに上付き文字で分かれている（例: `Ca`〈日欧米〉と `256k`〈欧伯〉）ので、日本の値を採った。カード 14 件、カートリッジ 69 件。
- 型番は表記のまま（ゴールドカートリッジ `G-1301`、マイカード `C-501`、サリオ `S-001`）。MAME の並記（`G-1305, 5055, 41008`）の
  数字だけのものは海外版なので採らない。型番が無いのは『ソロモンの鍵 王女リヒタの涙』（サリオ。MAME は `002` だけ）の 1 件。
- マイカードの MAME の記録には日本語の題名が無く自動で照合できないため、同日・同型番のものを `overrides/matches.csv` で手動対応した（16 件）。
- 価格は 8 件（無いものは許容）。全て消費税導入前の発売なので `税なし`。
- 発売日は Wikipedia を採る。MADB・MAME と異なるものは要確認レポートに出す（6 件。『スペースハリアー』は MADB・MAME とも 1986年12月21日）。
- 吸い出しは MAME の CRC・名前で結びつけ、全 83 件にある。日本・海外共通の `(World)` などの吸い出しも含む（23 行）。
  セガエイジス・セガ3D復刻アーカイブスに収録されたもの（`Sega Ages`・`Sega 3D Classics`）は `collection`。
- Wikipedia「その他」節の『ゲームでチェック！交通安全』（セガと東京海上火災保険が交通安全キャンペーン用に共同開発した非売品）は
  別リストの `business`。No-Intro では `(Proto)` だが、手動の行（`overrides/non_retail_manual.csv`）を優先し、自動の `prototype` の行は作らない。
  別リストのほかの 2 件は No-Intro の試作品（チョップリフター、Color & Switch Test）。非売品の調査は後回し。
- 発売されなかったタイトルは対象外。

## CV

エポック社のカセットビジョン（1981年発売）用のソフト。一覧の記事も MADB・MAME・No-Intro の記録も無いため、ja.wikipedia「カセットビジョン」の
「ソフトウェア」節の箇条書き（11 作品）から手で作った（`data/cv/jp_titles.csv`。生成スクリプトは無い）。`id` は記事の並び順
（カセットビジョンJr.対応 8 作品、専用 3 作品の順。発売日が分からないものがあるため厳密な発売順ではない）。

- `jr_compat` はカセットビジョンJr.対応（`yes`。8 件）。
- 発売日は Wikipedia の記述で確かめられたものだけ（きこりの与作 1981年7月30日〈本体と同時のローンチタイトル〉、ギャラクシアン 1981年8月10日、
  モンスターマンション 1982年、エレベーターパニック 1984年8月）。ほかの 7 件は空欄（`sources` 列に根拠の記事）。
- 価格は本体の記事の記述（エレベーターパニックは 3,980円、ほかは 4,980円）。消費税導入前なので `税なし`。
- 型番・ハッシュは出典が無く空欄（カセットごとにマイコンを内蔵した作りで、MAME・No-Intro に記録が無い）。
- 販売中止の『グランドチャンピオン』は対象外。

## プレイディア

バンダイのプレイディア（1994年発売）用のソフト。`id` は `playdia-jp-<連番>`（発売順）。

| 用途 | 出典 |
|---|---|
| タイトル・発売日・品番 | ja.wikipedia「プレイディア」の「ソフト一覧」の表（一覧の記事は無い）。33 件で、本文の年ごとの本数（11・16・6）と一致 |

- 型番は表の品番（`BAPD-01`〜、`BKPD-01`〜、家なき子の `VPRJ-09722`）で全 33 件にある（MADB・MAME に記録が無いので、enrich.py は
  Wikipedia の品番の列〈`wiki_model`〉を使う）。
- 発売元・価格・ハッシュは出典が無く空欄（合意済み。MADB・MAME に項目が無く、libretro の Redump DAT にも無い）。
- 非売品は Wikipedia「非売品」節の 7 件のうち、配布経路の書かれた 2 件（祐実とトコトンプレイディア〈キャンペーン景品・5,000名〉、
  ゴー!ゴー!アックマン・プラネット〈Vジャンプの懸賞・200名〉。いずれも `prize`）。店頭販促用の「Playdia サンプルソフト」（`BS-002`）は
  別リストの `store_demo`（どちらも手で管理）。経路の記述の無い 4 件は後回し。
- 業務用の「みちゃ王」用ディスクは対象外。

## SCV

エポック社のスーパーカセットビジョン（1984年発売）用のソフト。他社の参入は無く、全てエポック社の発売。`id` は `scv-jp-<連番>`（カセットの通し番号の順）。

| 用途 | 出典 |
|---|---|
| タイトル・発売時期・通し番号・キャッチフレーズ | ja.wikipedia「スーパーカセットビジョン用ソフト」（表ではなく作品ごとの節。30 件で、本体の記事の「30タイトル」と一致） |
| ハッシュ | No-Intro DAT（libretro 収録の Epoch - Super Cassette Vision） |

- 作品ごとの節は `fetch_wikipedia_list.py` の `per_section`（節の見出しが題名、節の冒頭の「1984年7月発売」が発売時期）で読む。
- 発売日は分かる精度（`YYYY-MM`、季節・範囲〈「1985年秋」「1985年末 - 1986年初頭ごろ」〉は最初の年、ドラゴンボールのみ日まで）で、
  元の表記は `release_date_text`。『ベーシック入門』（BASIC 言語ソフト）は発売時期の記述が無く空欄。
- `cassette_no` はカセットの通し番号（節の順番。記事の注記に「節の番号はゲームカセットの通し番号に合わせてある」とある）。
- `catchphrase` は各カセットのキャッチフレーズ（記事にあるもの。26 件）。
- 価格・型番は出典が無く空欄（MADB に項目が無く、MAME `hash/scv.xml` にも型番・発売日が無い）。
- 吸い出しは全 30 件にある。MAME に日本語の題名が無いため、No-Intro の名前で手動対応した（`overrides/dump_matches.csv`）。
  日本版と日仏共通版。フランスだけの版は載せない。
- 発売中止の 3 作品は対象外。非売品の調査は後回し。

## VB

バーチャルボーイとして日本で発売されたソフト（1995年）。`id` は `vb-jp-<連番>`（発売順）。

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元・容量 | ja.wikipedia「バーチャルボーイ」の「ソフトウェア」節の表（一覧の記事は無い）。日本で発売された 19 件（本文と一致） |
| 価格（・型番の補助） | メディア芸術データベース（機種「バーチャルボーイ」。13 件で価格は 4 件） |
| 型番・発売日の照合 | MAME ソフトウェアリスト `hash/vboy.xml` |
| ハッシュ | No-Intro DAT（libretro 収録の Nintendo - Virtual Boy） |

- `capacity` は容量（`4M`・`8M`・`16M`）。
- 型番は GB と同じ形の `VUE-VMTJ-JPN` にそろえた（MADB のパッケージ表記 `VUE-P-VMTJ`、MAME の `VUE-VMTJ-JPN`）。全 19 件にある。
- 価格は 4 件（MADB。無いものは許容）。
- 吸い出しは全 19 件にある。日本版と日米共通版（`(Japan, USA)`）。自作ソフト（`(World)`）・Switch Online 版（ZERO RACERS・D-HOPPER。
  当時は発売されず Nintendo Classics で配信されたもので、本リストにも入れない）は載せない。日本の試作品 2 件（ニコちゃんバトル、
  Space Pinball）は別リストの `prototype`。
- 非売品の調査は後回し。発売されなかったソフトは対象外。

## PSP

PlayStation Portable のパッケージ（UMD）ソフトとして日本で発売されたもの（2004〜2016年）。`id` は `psp-jp-<連番>`（発売順）。

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元・DL 欄 | ja.wikipedia「PlayStation Portableのゲームタイトル一覧」の表から、日本の発売日のある行（1,564 件。うちパッケージ 1,460 件で、本文の表と一致） |
| 価格（・型番の補助） | メディア芸術データベース（機種「プレイステーション・ポータブル」の媒体「UMD」。2,621 件） |
| ハッシュ | Redump DAT（libretro 収録の Sony - PlayStation Portable。UMD） |

- 本リストはパッケージの 1,460 件。「DL」欄が ▲・△ の配信専用 104 件は別リスト `jp_download.csv`（`--list download`。ハッシュは後回し）。
- `vita_compat` は PS Vita で遊べる（DL 欄の ●・○。774 件）、`umd_passport` は UMD Passport 対応（●。381 件）。
- 型番は表記のまま（`ULJM-05001`・`ULJS-00001`・`UCJS-10001` など。MADB の `ULJM 05001` もそろえる）。MADB の型番は約 300 件なので、
  Redump の題名とシリアルで補った（日本語の題名をローマ字にして 0.75 以上似ていてほかに候補の無いもの 473 件。確認した範囲で誤りは無かった）。
  型番は 771 件で、無いものは許容（合意済み。手動の対応はしていない）。
- 価格は 1,357 件（MADB。総額表示）。the Best・限定版・本体同梱版・パックは行にしない。
- 吸い出しは Redump のシリアル（＝型番）で結びつけ、753 件にある（型番の無いタイトルには付かない）。日本版と日本を含む共通版
  （`(Japan, Asia)`・`(Japan, Korea)` など）。`v1.01` などは `revision` 列。`PSP the Best`・`Rockstar Classics` は `collection`。
  マイク同梱などの `Doukonban` は同じタイトル。販売経路の記録の無い `Taikenban` は載せない。
- 非売品は Wikipedia の『みんなのGOLF ポータブル コカ・コーラ スペシャル エディション』（Coke Style キャンペーンで 1,300 人に配布。`prize`。吸い出しあり）。
  No-Intro（配信版）の店頭デモ（`Kiosk Demo`）などは後回し。
- CERO の年齢区分は後回し。発売されなかったタイトルは対象外。

## DC

ドリームキャストとして日本で発売されたソフト（1998〜2007年）。`id` は `dc-jp-<連番>`（発売順）。

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元 | ja.wikipedia「ドリームキャストのゲームタイトル一覧」の表から、日本の発売日のある行（497 件。本文の年ごとの本数と一致。出典はセガハード大百科） |
| 価格（・型番の補助） | メディア芸術データベース（機種「ドリームキャスト」。670 件） |
| 型番・発売日の照合 | MAME ソフトウェアリスト `hash/dc.xml` |
| ハッシュ | Redump DAT（libretro 収録の Sega - Dreamcast） |

- 型番は表記のまま（セガ `HDR-0001`、ライセンシー `T-1201M`、セガのその他 `610-7055`）。MADB・MAME で決まらないものは Redump のレーベル面の
  シリアルで補った（自動 25 件。手動は `overrides/matches.csv`）。Redump に同じ題名で型番が 2 つあるもの（初回限定版と通常版とみられる。
  『シェンムーII』『パンドラの夢』など 15 件）は通常版を決められないので型番を空にし、吸い出しだけ名前で結びつけた（`overrides/dump_matches.csv`）。
  型番は 481 件。
- 価格は 411 件（MADB。2004年4月以降は総額表示）。ドリコレ（廉価版）・限定版・本体などとのセット・同梱版は行にしない。
- 吸い出しは Redump のシリアル（＝型番）で結びつけ、495 件にある。日本版と日本を含む共通版。複数枚組は 1 行。`@barai`（ネットワーク経由の
  課金で遊ぶ版。エターナルアルカディア・ハンドレッドソード）は `dump_kind` が `online`。吸い出しが無いのは『サクラ大戦』（2000年版）と
  『パチンコの殿堂 CRエナジー』。
- 店頭体験版（`Tentou Taikenban`・`Tentou-you Taikenban`・`Tentou-you Demo Movie`）は別リストの `store_demo`（22 件）。販売経路の記録の無い
  体験版（`Taikenban`）は載せない。東京ゲームショウのディスク・ドリームパスポート・雑誌付録（ドリマガGD など）・トヨタの「ドリキャッチ」・
  JRA PAT などの調査は後回し。
- 非売品は Wikipedia の『ハローキティのガーデンパニック』（「Hello Kitty ドリームキャストセット」に付属。`bundled`）の 1 件。
- 年齢区分は後回し。非ライセンスタイトル（2007年以降の同人・インディー）・発売されなかったタイトルは対象外。

## Xbox 360

Xbox 360 のパッケージソフトとして日本で発売されたもの（2005〜2021年）。`id` は `x360-jp-<連番>`（発売順）。

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元・媒体・後方互換 | ja.wikipedia「Xbox 360のゲームタイトル一覧」の表から、日本の発売日のある行（723 行。本文の合計 725 件とは 2011年・2012年で 1 件ずつ合わないが、表の行のとおりにした） |
| 価格・型番 | メディア芸術データベース（機種「Xbox 360」。「ダウンロードコンテンツ」は照合に使わない） |
| ハッシュ | Redump DAT（libretro 収録の Microsoft - Xbox 360） |

- 本リストは「媒体」欄が ◎（パッケージとダウンロード）と無印（パッケージ）の 699 件。ダウンロードだけで出た ○ の 24 件は別リスト
  `jp_download.csv`（`--list download`）。Xbox Live Arcade（別ページ）は後回し。「Xbox用タイトル」節（初代 Xbox のソフトの配信）は対象外。

| 列 | 内容 |
|---|---|
| `download_too` | ダウンロード版もある（◎。225 件） |
| `xone_compat` | Xbox One 以降の後方互換に対応（226 件） |
| `kinect` | 備考の「Kinect専用」→ `required`（34 件）、「Kinect対応」→ `supported`（14 件） |

- 型番は MADB のパッケージの品番（Xbox と同じ形）で 58 件。無いものは許容（合意済み）。
- 価格は 571 件（MADB）。プラチナコレクション・初回限定版・コレクターズエディション・本体やコントローラーとの同梱版（プレミアムパック）は
  行にしない。自動照合でこれらが当たったものは通常版に直し、通常版が MADB に無いもの（ブルードラゴン、Forza Motorsport 2 など 9 件）は
  価格なし（`overrides/matches.csv`）。
- 吸い出しは Xbox と同じく題名で結びつけた。自動 159 件（`review/dat_title_matches.csv`）、手動 414 件（`overrides/dump_matches.csv`）で、
  吸い出しのあるタイトルは 573 件。複数枚組（インストール用・プレイ用ディスクを含む）は 1 行。コール オブ デューティの字幕版と
  吹き替え版（`Jimakuban`・`Fukikaeban`）は Wikipedia の行（字幕版）に両方を入れた。日本版と日本を含む共通版。
  モンスターハンター フロンティアの各パッケージは版の区別がつかないため G1 を除き結びつけていない。
- CERO の年齢区分・非売品は後回し。発売されなかったタイトルは対象外。

## Xbox

Xbox として日本で発売されたソフト（2002〜2006年）。`id` は `xbox-jp-<連番>`（発売順）。

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元・互換 | ja.wikipedia「Xboxのゲームタイトル一覧」の表から、日本の発売日のある行（222 件。本文の年ごとの本数と一致。廉価版は載っていない） |
| 価格・型番 | メディア芸術データベース（機種「Xbox」。270 件） |
| ハッシュ | Redump DAT（libretro 収録の Microsoft - Xbox） |

| 列 | 内容 |
|---|---|
| `x360_compat` | Xbox 360 で遊べる（Wikipedia の「互換」欄の★。日本の公式サイトの一覧が出典） |
| `xone_compat` | Xbox One・Xbox Series X/S で遊べる（◆） |
| `world_collection` | 「Xboxワールドコレクション」（英語版に日本語マニュアルを付けたもの。Wikipedia の備考から） |

- 型番は MADB のパッケージの品番（`M5F-00012` の形。`A4K 00001` のような区切りの違いはそろえた）で 60 件。無いものは許容（合意済み）。
  Redump のシリアル（`MS-055` などソフト内部のタイトル ID）は品番ではないので型番に使わず、吸い出し一覧の `game_code` に残る。
- 価格は 179 件（MADB。2004年4月以降は総額表示）。プラチナコレクション（廉価版）・初回限定版・スペシャルパック・Xbox Live 同梱版は
  行にしない。『R:RACING EVOLUTION』は MADB に初回限定版しか無いので価格なし。
- 吸い出しは、Redump のシリアルが型番と違うため題名で結びつけた。日本を含む地域の吸い出しを題名ごとにまとめ、日本語の題名を
  ローマ字にしてとても似ていてほかに候補の無いもの（58 件）は自動（`review/dat_title_matches.csv`）、残りは題名を見て手で対応した
  （152 件。`overrides/dump_matches.csv`）。吸い出しのあるタイトルは 210 件。日本版と日本を含む共通版（`(USA, Japan)`・`(Japan, Korea)`・
  `(Japan, Asia)`・`World`）。体験版・店頭デモ・東京ゲームショウのディスクなどは載せない（非売品は後回し）。
- CERO の年齢区分は後回し。発売されなかったタイトルは対象外。

## 3DO

3DO として日本で発売されたソフト（1994〜1996年）。`id` は `3do-jp-<連番>`（発売順）。

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元 | ja.wikipedia「3DOのゲームタイトル一覧」の「発売されたタイトル」の表から、日本の発売日のある行（214 件。本文の年ごとの本数と一致） |
| 価格（・型番の補助） | メディア芸術データベース（機種「3DO」。215 件） |
| 型番の照合 | MAME ソフトウェアリスト `hash/3do.xml`（日本版は 10 件ほど） |
| ハッシュ | Redump DAT（libretro 収録の The 3DO Company - 3DO） |

- 型番は表記のまま。松下系の流通は `FZ-SJ1351` のような `FZ-`、三洋系は `IMP-SA0701` のような `IMP-` で始まる（Wikipedia）。
  このほかメーカー独自の型番（`E3D-7023`・`NX-950101`・`I3D-7002`・`VZ002` など）がある。`channel` 列は型番から決めた流通系統
  （`panasonic` 163 件・`sanyo` 16 件。それ以外の型番・型番の無いものは空）。
- MADB・MAME で型番が決まるのは 63 件ほどなので、残りは Redump のレーベル面のシリアルで補った。日本語の題名をローマ字にして
  Redump の題名ととても似ていてほかに候補の無いもの（32 件。類似度 0.85 以上。`model_number_source` が `Redump`）は自動で、
  カタカナ表記の英題などで似ない 115 件は題名を見て手で対応した（`overrides/matches.csv`）。型番が無いのは Redump にも
  シリアルの無いもの・収録の無いものの 6 件。
- 価格は 200 件（MADB。全て税抜）。本体同梱の「ポリスノーツ マウスセット」は行にしない。MADB の「バイリンガル版」（ファッティーベア・
  パットパットなど）は日本で出た版そのもの。
- 年齢区分は出典に無いので列にしていない（後回し）。
- 吸い出しは Redump のシリアルで結びつけ、211 件にある。日本版と日本を含む共通版（`(Japan, Korea)`・`(USA, Japan)`・`World`）。
  複数枚組は 1 行（`discs` 列）で、ディスクごとの副題（ESPN Golf の `(Shot Yousei Kouza Vol. 1)` など）も除いてまとめる（`disc_subtitles`）。
  シリアルの無いコープス・キラー・サプリーム・ウォリアー・DOOM は名前で手動対応した（`overrides/dump_matches.csv`）。
- 非売品: Wikipedia の日本の非売品 2 件（ヒッチコックに挑戦〈トヨタの販促用とされる〉、バッテリーナビ〈古河電池。自動車部品店の
  店頭用とされる〉）は配布経路を確かめられる資料が読めなかったため、まだ載せていない。Redump には Wikipedia に無い日本の
  非売品・業務用ディスク（3DO REAL のサンプラーCD、Live! 3DO Magazine CD-ROM 1〜11、トヨペットの RV World など）もあり、合わせて後回し。
- 発売されなかったタイトル、海外だけのデモ集は対象外。

## PC-FX

PC-FX として日本で発売されたソフト（1994〜1998年）。`id` は `pcfx-jp-<連番>`（発売順）。

| 用途 | 出典 |
|---|---|
| タイトル・発売日・販売・ジャンル・年齢制限 | ja.wikipedia「PC-FXのゲームタイトル一覧」の「発売されたタイトル」の表（62 件。本文の年ごとの本数と一致） |
| 価格（・型番の補助） | メディア芸術データベース（機種「PC-FX」。43 件） |
| 型番・発売日の照合 | MAME ソフトウェアリスト `hash/pcfx.xml`（27 件） |
| ハッシュ | Redump DAT（libretro 収録の NEC PC-FX） |

- `genre` は Wikipedia のジャンル（`ADV`・`SLG`・`アニメ` など）。`age_rating` は「年齢制限」欄（`18推奨` → `18+`、`18禁` → `X`。各 4 件）。
  アニメフリークFX（アニメの情報ディスク）・ボイスパラダイスも表にあるので本リスト。
- 型番は表記のまま（`FXNHE626`・`FXHUD401`・`FXNKT601` など。MADB の `FXNHE 626` やバーコード付きの表記はそろえた）。MADB・MAME で
  決まるのは 26 件だけなので、35 件は Redump のレーベル面のシリアルを題名で手動対応して入れた（`overrides/matches.csv`）。
  型番が無いのは Redump にも無い『カクテルパック』の 1 件（吸い出しも無い）。
- 価格は 40 件（MADB。無いものは許容）。
- 吸い出しは Redump のシリアルで結びつけた。複数枚組は 1 行（`discs` 列）。ディスクごとに副題が付く組（天地無用!魎皇鬼FX の
  `(Disc A) (Hakua Kaikou)` など）も 1 行にまとめる（`platforms.py` の `disc_subtitles`。PS などではこの位置に版の印が来るので PC-FX だけ）。
  販売経路の記録の無い `(Sample)`（銀河お嬢様伝説ユナFX）、PC 用拡張ボード PC-FXGA のソフト（Same Game FX など 3 件）は載せない。
- 非売品は Wikipedia「その他」節の雑誌付録 4 件（PC Engine FAN Special☆CD-ROM Vol. 2・3、SUPER PC Engine FAN DELUXE の付録 2 件。
  いずれも `supplement`。吸い出しあり）。同じシリーズの Vol. 1 は PCE の非売品リストにある。その他の調査は後回し。
- 発売されなかったタイトルは対象外。

## ネオジオ

家庭用ネオジオ（ROM カートリッジ。AES）として日本で発売されたソフト（1990〜2004年）。ネオジオCD は別リスト（`data/neogeo/cd/`）。
`id` は `neogeo-jp-<連番>` / `neocd-jp-<連番>`（発売順）。

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元・ジャンル | ja.wikipedia「ネオジオのゲームタイトル一覧」の「家庭用ネオジオのタイトル」（117 件）と「ネオジオCDのタイトル」（97 件）の表（いずれも本文の件数と一致） |
| 価格（・型番の補助） | メディア芸術データベース（機種「ネオジオ」「ネオジオCD」） |
| 型番・発売日の照合 | MAME ソフトウェアリスト `hash/neogeo.xml`（業務用 MVS と家庭用 AES が混在）/ `hash/neocd.xml` |
| ハッシュ | ROM: MAME `hash/neogeo.xml` の ROM チップごと（No-Intro に DAT が無い）。CD: Redump DAT（libretro 収録の SNK Neo Geo CD） |

列:

| 列 | 内容 |
|---|---|
| `genre` | Wikipedia のジャンル（ROM のみ） |
| `cd_version` / `rom_version` | もう一方（ネオジオCD / ROM）でも発売されたもの（Wikipedia の「NGCD」「NG」欄） |
| `rental` | 1990年の発売（レンタル用。店頭での販売は 1991年7月1日の廉価版から。備考にも記載）。11 件 |

### ROM

- 型番は家庭用の `NGH-001`（後期は `NGH-2650` のように 4 桁）。MAME の業務用の型番（`NGM-`）・業務用だけの版は使わない。MAME の発売日が
  「`19900426 (MVS), 19910701 (AES)`」のように並ぶものは家庭用の日付を採る。型番が無いのは、MAME に家庭用の記録が無い『サイバーリップ』『戦国伝承2001』の 2 件。
- 1990年の 11 件は、MADB・MAME とも販売開始の 1991年7月1日で記録されているので手動で対応した（価格は MADB の廉価版のもの）。
  手動対応は `overrides/matches.csv`（18 件）。
- 価格は全 117 件（MADB。全て税抜）。
- 吸い出し一覧（`jp_rom_dumps.csv`）はほかの機種と形が違い、MAME の ROM チップ（`dataarea`: `maincpu`・`fixed`・`audiocpu`・
  `ymsnd:adpcma`・`sprites` など）ごとに 1 行（`hash_source` は `MAME`）。家庭用（`NGH`）の別版も含む。
  `scripts/build_mame_list.py neogeo main neogeo` で作る。
- 『ショックトルーパーズ セカンドスカッド』は Wikipedia が 1998年6月24日、MADB・MAME が 1999年6月24日（要確認レポート）。

### ネオジオCD

- 型番は表記のまま（SNK `NGCD-083`、ADK `ADCD-102`、データイースト `DECD-`、`AICD-`）。全 97 件にある。
  『ファイヤースープレックス』は MADB・Redump の `NGCD-043` を採った（MAME の `NGCD-034` は誤記とみられる）。
  ADKワールド・『幕末浪漫第二幕 月華の剣士』は Redump のレーベル面のシリアルを型番にした（`overrides/matches.csv`）。
- MADB には同じソフトが媒体「CD-ROM」と「Compact Disc」の 2 件で載っていることがあり、価格はどちらか一方にだけある。価格は 74 件。
  「限定版」（龍虎の拳外伝）は行にしない。
- 吸い出しは Redump のシリアルで結びつけ、全 97 件にある。日本版と日本を含む共通版（`World`）。2019年の自作ソフト（Xeno Crisis）、
  海外版（`Export`）だけのものは載せない。

ネオジオステーション（PS3・PSP での配信）は対象外。非売品の調査は後回し。発売されなかったタイトルは対象外。

## NGP/NGPC

ネオジオポケット・ネオジオポケットカラーは 1 本のリストにまとめ、`compat` 列で区別する。`id` は `ngp-jp-<連番>`（発売順）。

| `compat` | 種類 | 件数 |
|---|---|---|
| `ngp` | ネオジオポケット（モノクロ） | 9 |
| `ngpc_compatible` | ネオジオポケットカラー対応 | 39 |
| `ngpc_only` | ネオジオポケットカラー専用 | 34 |

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元 | ja.wikipedia「ネオジオポケットのゲームタイトル一覧」の 3 つの表（日本 82 件。各節の発売年一覧の合計と一致。追加要素の無い廉価版は載っていない） |
| 価格（・型番の補助） | メディア芸術データベース（機種「ネオジオポケット」） |
| 型番・発売日の照合 | MAME ソフトウェアリスト `hash/ngp.xml` / `hash/ngpc.xml` |
| ハッシュ | No-Intro DAT（libretro 収録の SNK Neo Geo Pocket / Neo Geo Pocket Color） |

- 型番は大文字にそろえた（MAME の `NeoP00010`、MADB の `NEOP00040` → `NEOP00010` の形）。型番が無いのは MAME に日本版の記録が無い
  『どこでも麻雀』『ネオ・トゥエンティワン』『ネオ・バカラ』の 3 件。型番の形が全地域共通なので、MAME の海外だけの版（`(Europe, USA)` など）は照合に使わない。
- MADB のネオジオポケットベストコレクション（廉価版）・限定BOX（本体同梱を含む）・キャンペーン版（KOF R-2、バイオモーター ユニトロン）は
  行にせず、価格は通常版のもの（82 件。全て税抜）。限定版・キャンペーン版の扱いの調査は後回し。
- 自動で照合できなかったもの（表記の違い、発売日の違い、限定スペシャルBOX が当たる『サムライスピリッツ!』など）は
  `overrides/matches.csv` で手動対応した（13 件）。
- 発売日は Wikipedia を採る。MADB・MAME と異なるものは要確認レポートに出す（11 件。『ベースボールスターズ』は Wikipedia がローンチタイトルとして
  1998年10月28日、MADB・MAME は 1998年11月26日など）。
- ダイヴ アラート（バーン編・レベッカ編）、カードファイターズ（SNK・CAPCOM サポーターズバージョン）は別タイトル。
- 吸い出しは日本版と日本を含む共通版（`(Japan, Europe)`・`(World)`）。北米・欧州だけの版、配布経路の記録の無い `(Demo 1)`・`(Demo 2)`、
  試作品は載せない。`v0B` などの版は `revision` 列。全 82 件に吸い出しがある。MAME と No-Intro で CRC が異なるものが多い
  （フラッシュメモリの保存領域の違いとみられる）ため、17 件は名前で手動対応した（`overrides/dump_matches.csv`）。
- 非売品の調査は後回し（Wikipedia に「非売品」節が無い）。発売されなかったタイトルは対象外。

## WS/WSC

ワンダースワン・ワンダースワンカラーは 1 本のリストにまとめ、`compat` 列で区別する（スワンクリスタル専用のソフトは無い）。
`id` は `ws-jp-<連番>`（発売順）。

| `compat` | 種類 | 件数 |
|---|---|---|
| `ws` | ワンダースワン（モノクロ） | 111 |
| `wsc_compatible` | ワンダースワンカラー対応（モノクロ機でも動く） | 20 |
| `wsc_only` | ワンダースワンカラー専用 | 71 |

| 用途 | 出典 |
|---|---|
| タイトル・発売日・発売元 | ja.wikipedia「ワンダースワンのゲームタイトル一覧」の 3 つの表（108・20・70 件で計 198 件。本文の「全198タイトル」と一致。ベスト版は載っていない） |
| 価格（・型番の補助） | メディア芸術データベース（機種「ワンダースワン」。カラーも含む） |
| 型番・発売日の照合 | MAME ソフトウェアリスト `hash/wswan.xml` / `hash/wscolor.xml`（説明に地域が無いので全件を日本版とし、`(Asia)` だけ除く） |
| ハッシュ | No-Intro DAT（libretro 収録の Bandai WonderSwan / WonderSwan Color） |

- 本リストは Wikipedia の 198 件に、「専用カートリッジが付属する周辺機器」節の 4 件（ワンダーボーグ、モバイルワンダーゲート、
  ワンダーウィッチ、mama Mitte'）を加えた 202 件（`overrides/extra_titles.csv`）。本表にあるハンディーソナー・デジタルパートナーも本リスト。
  ワンダーボーグの発売日は先行発売の 2000年6月23日（一般発売は同年12月7日）。
- 型番は表記のまま（`SWJ-BAN001`、カラー専用・カラー対応の多くは `SWJ-BANC01` のように C 付き。末尾は 16 進）。
  mama Mitte' は `MM-280`、JUDGEMENT SILVERSWORD は `WWGP2001A3`。MADB の `SWJ-SUMCO7` のような O と 0 の誤記は 0 にそろえた。
  ワンダーボーグ・モバイルワンダーゲートの型番は MAME が記録する付属カートリッジのもの。型番が無いのはワンダーウィッチと Dicing Knight. の 2 件。
- MADB にある初回限定版・本体同梱版・ハードお買い得版・ワンダーウェーブ同梱版・通信ケーブル同梱版などは行にせず、価格は通常版のもの
  （通常版が MADB に無い『ファイナルファンタジーII』などは同梱版の価格を採らない）。価格は 181 件（無いものは許容）。
- 照合では「for WonderSwan」と「for ワンダースワン」を同じとみなす。自動で照合できなかったもの（カタカナと英字で表記が違う同日の
  『BUFFERS EVOLUTION』と「バッファーズエボリューション」、MAME の発売日が年月までの『ワンダースタジアム』など）は
  `overrides/matches.csv` で手動対応した（23 件）。
- 発売日は Wikipedia を採る。MADB・MAME と異なるものは要確認レポートに出す（13 件。『名探偵コナン 夕暮れの皇女』『ミスタードリラー』は
  MADB・MAME とも 2001年4月5日、JUDGEMENT SILVERSWORD は 2004年2月5日）。
- No-Intro にシリアルが無いので、吸い出しは MAME の CRC・名前・手動対応（6 件）で結びつけた。日本版だけを載せ、WonderWitch の自作ソフト、
  香港版・韓国版、販売経路の記録の無い `(Sample)` は載せない。`Rev 1`・`Rev 5C21` などは `revision` 列。
  製品版の吸い出しが無いのはワンダーウィッチ（No-Intro に無い）と mama Mitte' の 2 件。
- 非売品は Wikipedia「非売品」節の 3 件（SDガンダム オペレーションU.C. スペシャルパッケージ〈ガシャポンの抽選プレゼント〉、
  デジモンアドベンチャー キャンペーン限定バージョン、スターハーツ 体験版〈ファミ通の抽選プレゼント〉。いずれも `prize`）。
  吸い出しがあるのは後の 2 件。その他の調査は後回し。
- 「その他」節の会場限定販売の 2 件（TENORI-ON〈岩井俊雄の個展会場〉、ピリオドの無い Dicing Knight〈WWGP2003 最終選考会場〉）は
  `jp_other.csv`（手で管理。`nointro_name` に吸い出し名）。発売されなかったタイトルは対象外。

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

python3 scripts/fetch_wikipedia_list.py wii
python3 scripts/fetch_wikipedia_list.py wii --list wiiware  # → data/wii/jp_wiiware.csv
python3 scripts/enrich.py wii                  # maru-chang は 5 秒間隔で 28 ページ取得
python3 scripts/build_dumps.py wii

python3 scripts/fetch_wikipedia_list.py n64
python3 scripts/fetch_wikipedia_list.py n64 --list 64dd   # → data/n64/jp_64dd.csv
python3 scripts/enrich.py n64
python3 scripts/build_dumps.py n64

python3 scripts/fetch_wikipedia_list.py sfc
python3 scripts/enrich.py sfc                  # ニンテンドウパワー書き換え専用タイトルはここで除く
python3 scripts/build_nintendo_power.py sfc
python3 scripts/build_dumps.py sfc

python3 scripts/fetch_wikipedia_list.py fc
python3 scripts/enrich.py fc
python3 scripts/build_dumps.py fc
python3 scripts/fetch_wikipedia_list.py fds    # ディスクシステム → data/fc/disk_system/
python3 scripts/enrich.py fds
python3 scripts/build_dumps.py fds

python3 scripts/fetch_wikipedia_list.py md
python3 scripts/fetch_wikipedia_list.py md --list online   # 配信専用 → data/md/jp_online.csv
python3 scripts/enrich.py md
python3 scripts/build_dumps.py md
python3 scripts/fetch_wikipedia_list.py mcd    # メガCD → data/md/mega_cd/
python3 scripts/enrich.py mcd
python3 scripts/build_dumps.py mcd
python3 scripts/fetch_wikipedia_list.py 32x    # スーパー32X → data/md/32x/
python3 scripts/enrich.py 32x
python3 scripts/build_dumps.py 32x

python3 scripts/fetch_wikipedia_list.py pce
python3 scripts/fetch_wikipedia_list.py pce --list other   # 「その他」節 → data/pce/jp_other.csv
python3 scripts/enrich.py pce
python3 scripts/build_dumps.py pce

python3 scripts/fetch_wikipedia_list.py ss
python3 scripts/enrich.py ss
python3 scripts/build_dumps.py ss

python3 scripts/fetch_wikipedia_list.py ps     # 年別 9 ページ
python3 scripts/enrich.py ps
python3 scripts/build_dumps.py ps

python3 scripts/fetch_wikipedia_list.py gg
python3 scripts/enrich.py gg
python3 scripts/build_dumps.py gg

python3 scripts/fetch_wikipedia_list.py sg1000
python3 scripts/fetch_wikipedia_list.py sg1000 --list non_game   # BASIC・教育用ソフト → data/sg1000/jp_non_game.csv
python3 scripts/enrich.py sg1000
python3 scripts/build_dumps.py sg1000
python3 scripts/build_mame_list.py sg1000 non_game sc3000_cart  # 別リストに MAME の型番・ハッシュ

python3 scripts/fetch_wikipedia_list.py sms
python3 scripts/enrich.py sms
python3 scripts/build_dumps.py sms

python3 scripts/fetch_wikipedia_list.py playdia   # 本体の記事の表（1段下の見出し）
python3 scripts/enrich.py playdia

python3 scripts/fetch_wikipedia_list.py scv  # 作品ごとの節の記事
python3 scripts/enrich.py scv
python3 scripts/build_dumps.py scv

python3 scripts/fetch_wikipedia_list.py vb   # バーチャルボーイ（本体の記事の表）
python3 scripts/enrich.py vb
python3 scripts/build_dumps.py vb

python3 scripts/fetch_wikipedia_list.py psp
python3 scripts/fetch_wikipedia_list.py psp --list download   # 配信専用 → data/psp/jp_download.csv
python3 scripts/enrich.py psp
python3 scripts/build_dumps.py psp

python3 scripts/fetch_wikipedia_list.py dc
python3 scripts/enrich.py dc
python3 scripts/build_dumps.py dc

python3 scripts/fetch_wikipedia_list.py x360
python3 scripts/fetch_wikipedia_list.py x360 --list download   # ダウンロード専売 → data/x360/jp_download.csv
python3 scripts/enrich.py x360
python3 scripts/build_dumps.py x360

python3 scripts/fetch_wikipedia_list.py xbox
python3 scripts/enrich.py xbox                 # 吸い出しの題名での照合 → review/dat_title_matches.csv
python3 scripts/build_dumps.py xbox

python3 scripts/fetch_wikipedia_list.py 3do
python3 scripts/enrich.py 3do                  # Redump の題名から型番を補う（dat_title_models）
python3 scripts/build_dumps.py 3do

python3 scripts/fetch_wikipedia_list.py pcfx
python3 scripts/enrich.py pcfx
python3 scripts/build_dumps.py pcfx

python3 scripts/fetch_wikipedia_list.py neogeo
python3 scripts/enrich.py neogeo
python3 scripts/build_mame_list.py neogeo main neogeo   # ROM チップごとのハッシュ（MAME）→ jp_rom_dumps.csv
python3 scripts/fetch_wikipedia_list.py neocd   # ネオジオCD → data/neogeo/cd/
python3 scripts/enrich.py neocd
python3 scripts/build_dumps.py neocd

python3 scripts/fetch_wikipedia_list.py ngp
python3 scripts/enrich.py ngp
python3 scripts/build_dumps.py ngp

python3 scripts/fetch_wikipedia_list.py ws
python3 scripts/enrich.py ws
python3 scripts/build_dumps.py ws

python3 scripts/fetch_psxdatacenter.py          # psxdatacenter.com（PS1・PS2 の型番）。2 秒間隔、PS1 は約 3〜4 時間
python3 scripts/fetch_wikipedia_list.py ps2
python3 scripts/enrich.py ps2
python3 scripts/build_dumps.py ps2

python3 scripts/fetch_wikipedia_list.py ps3
python3 scripts/fetch_wikipedia_list.py ps3 --list psn   # 配信専用 → data/ps3/jp_psn.csv
python3 scripts/enrich.py ps3
python3 scripts/build_dumps.py ps3
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
