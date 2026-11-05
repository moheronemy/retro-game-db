"""機種ごとの設定。新しい機種はここに追加する。"""
import re

from common import ROOT


def _gba_models(text):
    """'AGB-P-B9AJ(JPN)' や 'AGB-B9AJ-JPN' から 'AGB-B9AJ-JPN' を得る（ABG/AGP は誤記）。"""
    codes = []
    for m in re.finditer(r"\b(?:AGB|ABG|AGP)-(?:P-)?-?([A-Z0-9]{3}J)\b", text.upper()):
        c = f"AGB-{m.group(1)}-JPN"
        if c not in codes:
            codes.append(c)
    return codes


def _gba_code(model):
    """型番から ROM ヘッダのゲームコード（4文字）を得る。"""
    m = re.fullmatch(r"AGB-([A-Z0-9]{3}J)-JPN", model or "")
    return m.group(1) if m else ""


def _gba_normalize_code(c):
    """No-Intro のシリアルを型番のゲームコードにそろえる。
    日米共通カートリッジは ROM 内のコード末尾が A（例: B85A）、パッケージ型番は J（AGB-B85J-JPN）。"""
    if re.fullmatch(r"[A-Z0-9]{3}A", c):
        return c[:3] + "J"
    return c if re.fullmatch(r"[A-Z0-9]{3}J", c) else ""


def _gb_models(text):
    """GB/GBC の日本版の型番を取り出して正規化する。
    初期は 'DMG-TRA' / 'DMG-WQJ' のような3文字（末尾が地域。日本版は A または J）、
    後期は 'DMG-ACCJ-JPN' / 'CGB-BDLJ-JPN' の4文字。'CGB-P-BK8J(JPN)' のようなパッケージ表記もそろえる。
    海外版（'DMG-TR-USA'、'DMG-104 CHN' など）は含めない。"""
    out = []
    for m in re.finditer(r"\b(DMG|CGB)-(?:P-)?([A-Z0-9]{3}J(?=-JPN|\(JPN\)|$|[\s,;)])|[A-Z0-9]{2}[JA](?=$|[\s,;)(]))",
                         text.upper()):
        prefix, code = m.groups()
        model = f"{prefix}-{code}-JPN" if len(code) == 4 else f"{prefix}-{code}"
        if model not in out:
            out.append(model)
    return out


def _gb_code(model):
    m = re.fullmatch(r"(?:DMG|CGB)-([A-Z0-9]{3}J)-JPN", model or "")
    return m.group(1) if m else ""


def _gb_normalize_code(c):
    return c if re.fullmatch(r"[A-Z0-9]{3}J", c) else ""


def _gb_check(row):
    """カラー対応（黒カートリッジ）は DMG-、カラー専用（透明）は CGB- で始まるのが通例。"""
    m, c = row.get("model_number", ""), row.get("compat", "")
    if (c == "gbc_compatible" and m.startswith("CGB")) or (c == "gbc_only" and m.startswith("DMG")):
        return [f"型番の接頭辞と対応区分が不整合 {c}/{m[:3]}"]
    return []


def _ds_models(text):
    """'NTR-P-AZWJ'、'NTR-AZWJ-JPN'、'TWL-VAAJ-JPN' などを 'NTR-AZWJ-JPN' の形にそろえる。"""
    out = []
    for m in re.finditer(r"\b(NTR|TWL)-(?:P-)?([A-Z0-9]{3}J)(?![A-Z0-9])", text.upper()):
        model = f"{m.group(1)}-{m.group(2)}-JPN"
        if model not in out:
            out.append(model)
    return out


def _ds_code(model):
    m = re.fullmatch(r"(?:NTR|TWL)-([A-Z0-9]{3}J)-JPN", model or "")
    return m.group(1) if m else ""


_DSI_SETS = None


def _ds_compat(row):
    """No-Intro の分類で決める。DSi の DAT（DSi 専用カートリッジ）にあれば dsi_only、
    DS の DAT で 'NDSi Enhanced' とされていれば dsi_enhanced、それ以外は ds。
    型番の TWL- は DSi 専用・DSi 対応の両方に使われているので判定には使わない。"""
    global _DSI_SETS
    if _DSI_SETS is None:
        from common import nointro_dat_text

        def codes(dat, need=None):
            out = set()
            for m in re.finditer(r'game \(\n\tname "([^"]+)"(.*?)\n\)\n', nointro_dat_text(dat), re.S):
                if need is None or need in m.group(1):
                    out.update(re.findall(r'serial "([A-Z0-9]{4})"', m.group(2)))
            return out
        _DSI_SETS = (codes("Nintendo - Nintendo DSi"), codes("Nintendo - Nintendo DS", "NDSi Enhanced"))
    code = _ds_code(row.get("model_number", ""))
    if code and code in _DSI_SETS[0]:
        return "dsi_only"
    if code and code in _DSI_SETS[1]:
        return "dsi_enhanced"
    return "ds"


_DS_PAGE = "ニンテンドーDSのゲームタイトル一覧 ({})"
_DSIWARE_PAGE = "ニンテンドーDSiウェアのタイトル一覧"
_DSIWARE_SECTIONS = {2008: 14, 2009: 170, 2010: 177, 2011: 59, 2012: 39, 2013: 14, 2014: 7, 2015: 14}

def _gc_models(text):
    """'DOL-GENJ-JPN'、'DOL-P-GENJ(JPN)'、Redump の 'DL-DOL-GENJ-JPN' を 'DOL-GENJ-JPN' にそろえる。"""
    out = []
    for m in re.finditer(r"(?:\bDL-)?\bDOL-(?:P-)?([A-Z0-9]{3}J)(?![A-Z0-9])", text.upper()):
        model = f"DOL-{m.group(1)}-JPN"
        if model not in out:
            out.append(model)
    return out


def _gc_code(model):
    m = re.fullmatch(r"DOL-([A-Z0-9]{3}J)-JPN", model or "")
    return m.group(1) if m else ""


def _gc_normalize_code(c):
    """Redump のシリアル（'DL-DOL-GENJ-JPN'）からゲームコードを取り出す。"""
    m = re.search(r"DOL-([A-Z0-9]{3}J)", c or "")
    return m.group(1) if m else ""


_GB_COLUMNS = ("jp", "na", "eu", "title", "publisher", "sgb", "notes")
_GBC_ONLY_COLUMNS = ("jp", "na", "eu", "title", "publisher", "notes")

PLATFORMS = {
    "gba": {
        "name": "ゲームボーイアドバンス",
        "dir": ROOT / "data" / "gba",
        "id_prefix": "gba-jp",
        "wikipedia": {
            "page": "ゲームボーイアドバンスのゲームタイトル一覧",
            "tables": [{"section": "発売されたタイトル", "layout": "simple"}],
        },
        "madb_platforms": ["ゲームボーイアドバンス"],
        "mame_lists": ["gba"],
        "nointro_dats": ["Nintendo - Game Boy Advance"],
        "nointro_export": "Game Boy Advance (DB Export)",
        "models_from": _gba_models,
        "models_from_serial": lambda s: [f"AGB-{s}-JPN"] if re.fullmatch(r"[A-Z0-9]{3}J", s) else [],
        "code_of": _gba_code,
        # No-Intro のシリアルを型番のゲームコードにそろえる。
        # 日米共通カートリッジはROM内のコード末尾が A（例: B85A）、パッケージ型番は J（AGB-B85J-JPN）
        "normalize_code": _gba_normalize_code,
        "maru": {
            "url": "https://maru-chang.com/gamedb/gamelist.php/GBAlineup_new/{page}",
            "pages": 16,          # 795タイトル / 50件ごと
            "interval": 5,        # 秒
            "cache_dir": "maru-chang",
            "model": lambda code: f"{code}-JPN" if re.fullmatch(r"AGB-[A-Z0-9]{3}J", code) else "",
        },
        # 2004年4月の総額表示義務化以降、MADB の「税抜」と maru-chang の「税込」が同額なら税込とする
        "tax_inclusive_from": "2004-04-01",
    },
    # ゲームボーイ／ゲームボーイカラーは1本のリストにまとめ、compat 列で
    # gb（GB専用）/ gbc_compatible（カラー対応）/ gbc_only（カラー専用）を区別する
    "gb": {
        "name": "ゲームボーイ／ゲームボーイカラー",
        "dir": ROOT / "data" / "gb",
        "id_prefix": "gb-jp",
        "wikipedia": {
            "tables": [
                {"page": "ゲームボーイのゲームタイトル一覧", "section": "発売されたタイトル",
                 "table_id": "softwarelist", "columns": _GB_COLUMNS, "extra": {"compat": "gb"}},
                {"page": "ゲームボーイカラーのゲームタイトル一覧", "section": "ゲームボーイカラー対応のタイトル一覧",
                 "table_id": "softwarelist", "columns": _GB_COLUMNS, "extra": {"compat": "gbc_compatible"}},
                {"page": "ゲームボーイカラーのゲームタイトル一覧", "section": "ゲームボーイカラー専用のタイトル一覧",
                 "table_id": "softwarelist2", "columns": _GBC_ONLY_COLUMNS, "extra": {"compat": "gbc_only"}},
            ],
        },
        "extra_columns": ["compat", "sgb"],
        "madb_platforms": ["ゲームボーイ", "ゲームボーイカラー"],
        "mame_lists": ["gameboy", "gbcolor"],
        "nointro_dats": ["Nintendo - Game Boy", "Nintendo - Game Boy Color"],
        "nointro_export": ["Game Boy (DB Export)", "Game Boy Color (DB Export)"],
        "models_from": _gb_models,
        "mame_jp_models": _gb_models,
        "models_from_serial": lambda s: [],   # GB の DAT にはシリアルがほぼ無いので型番の検証には使わない
        "code_of": _gb_code,
        "normalize_code": _gb_normalize_code,
        "check_row": _gb_check,
        "nintendo_power": {"page": "ニンテンドウパワーのゲームタイトル一覧", "section": "ゲームボーイ"},
    },
    # ニンテンドーDS / DS Lite / DSi。compat 列で ds / dsi_enhanced（DSi 対応）/ dsi_only（DSi 専用）を区別する
    "ds": {
        "name": "ニンテンドーDS",
        "dir": ROOT / "data" / "ds",
        "id_prefix": "ds-jp",
        "wikipedia": {
            # 脚注にある任天堂公式サイトの URL からゲームコードを拾う（型番の補完と maru-chang との照合に使う）
            "ref_code": r"nintendo\.co\.jp/ds/software/([a-z0-9]{3}j)/",
            # 年別ページの表は発売日が「1月15日」のように年を省いているので、表ごとに年を与える
            "tables": [
                {"page": _DS_PAGE.format("2004年-2005年"), "section": "2004年（全14タイトル）", "year": "2004"},
                {"page": _DS_PAGE.format("2004年-2005年"), "section": "2005年（全112タイトル）", "year": "2005"},
                {"page": _DS_PAGE.format("2006年"), "section": "2006年", "year": "2006"},
                {"page": _DS_PAGE.format("2007年"), "section": "2007年", "year": "2007"},
                {"page": _DS_PAGE.format("2008年"), "section": "2008年", "year": "2008"},
                {"page": _DS_PAGE.format("2009年"), "section": "2009年", "year": "2009"},
                {"page": _DS_PAGE.format("2010年"), "section": "2010年", "year": "2010"},
                {"page": _DS_PAGE.format("2011年-2012年"), "section": "2011年（全78タイトル）", "year": "2011"},
                {"page": _DS_PAGE.format("2011年-2012年"), "section": "2012年（全34タイトル）", "year": "2012"},
            ],
        },
        # DSiウェア（ダウンロード専用ソフト）は別リスト。fetch_wikipedia_list.py ds --list dsiware
        "extra_lists": {
            "dsiware": {
                "out": "jp_dsiware.csv",
                "id_suffix": "dsiware",
                "tables": [
                    {"page": _DSIWARE_PAGE, "section": f"{y}年（全{n}タイトル）", "year": str(y),
                     "columns": ("jp", "title", "publisher", "blocks", "3ds", "notes")}
                    for y, n in _DSIWARE_SECTIONS.items()
                ],
            },
        },
        "extra_columns": ["compat", "ref_code"],
        "derive": {"compat": _ds_compat},
        "madb_platforms": ["ニンテンドーDS"],
        "mame_lists": [],   # MAME には DS のソフトウェアリストがほぼ無い
        "nointro_dats": ["Nintendo - Nintendo DS", "Nintendo - Nintendo DSi"],
        "nointro_export": ["Nintendo DS (DB Export)", "Nintendo DSi (DB Export)"],
        # DB Export を取得できていない間は libretro 版 DAT で代用する（確認区分・刻印などは無い）
        "nointro_export_fallback": {"Nintendo DS (DB Export)": "Nintendo - Nintendo DS",
                                    "Nintendo DSi (DB Export)": "Nintendo - Nintendo DSi"},
        "models_from": _ds_models,
        "models_from_serial": lambda s: [f"NTR-{s}-JPN", f"TWL-{s}-JPN"] if re.fullmatch(r"[A-Z0-9]{3}J", s) else [],
        "code_of": _ds_code,
        # Wikipedia の脚注から拾ったゲームコードを型番にする（接頭辞は NTR とみなす）
        "ref_code_models": lambda code: f"NTR-{code}-JPN",
        "maru_date_only": True,
        "normalize_code": _gba_normalize_code,
        "maru": {
            "url": "https://maru-chang.com/gamedb/gamelist.php/DSlineup/{page}",
            "pages": 48,
            "interval": 5,
            "cache_dir": "maru-chang-ds",
            "model": lambda code: f"{code}-JPN" if re.fullmatch(r"(?:NTR|TWL)-[A-Z0-9]{3}J", code) else "",
        },
        "tax_inclusive_from": "2004-04-01",
    },
    # ニンテンドー ゲームキューブ。光ディスクなのでハッシュは Redump
    "gc": {
        "name": "ニンテンドー ゲームキューブ",
        "dir": ROOT / "data" / "gc",
        "id_prefix": "gc-jp",
        "wikipedia": {
            "tables": [
                {"page": "ニンテンドー ゲームキューブのゲームタイトル一覧", "section": "発売されたタイトル",
                 "table_id": "softwarelist", "columns": ("jp", "na", "eu", "title", "publisher", "notes")},
            ],
        },
        "madb_platforms": ["ニンテンドーゲームキューブ"],
        "mame_lists": [],
        "nointro_dats": ["redump:Nintendo - GameCube"],
        # Redump には No-Intro のような DB Export が無いので、libretro 収録の Redump DAT を使う
        "nointro_export": ["GameCube (Redump)"],
        "nointro_export_fallback": {"GameCube (Redump)": "redump:Nintendo - GameCube"},
        "models_from": _gc_models,
        "models_from_serial": _gc_models,
        "code_of": _gc_code,
        "normalize_code": _gc_normalize_code,
        "maru": {
            "url": "https://maru-chang.com/gamedb/gamelist.php/GClineup/{page}",
            "pages": 6,
            "interval": 5,
            "cache_dir": "maru-chang-gc",
            "model": lambda code: f"{code}-JPN" if re.fullmatch(r"DOL-[A-Z0-9]{3}J", code) else "",
        },
        "maru_date_only": True,
        "tax_inclusive_from": "2004-04-01",
        "hash_source": "Redump",
        "media": "disc",
    },
}


def get(key):
    if key not in PLATFORMS:
        raise SystemExit(f"未対応の機種: {key}（対応: {', '.join(PLATFORMS)}）")
    return PLATFORMS[key]
