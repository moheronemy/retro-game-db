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
}


def get(key):
    if key not in PLATFORMS:
        raise SystemExit(f"未対応の機種: {key}（対応: {', '.join(PLATFORMS)}）")
    return PLATFORMS[key]
