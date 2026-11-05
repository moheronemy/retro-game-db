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
}


def get(key):
    if key not in PLATFORMS:
        raise SystemExit(f"未対応の機種: {key}（対応: {', '.join(PLATFORMS)}）")
    return PLATFORMS[key]
