"""機種ごとの設定。新しい機種はここに追加する。"""
import re
import unicodedata

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


def _wii_models(text):
    """'RVL-RSPJ-JPN'、'RVL-P-RSPJ(JPN)'、'RVL-SFWJ-JPN-B0' などを 'RVL-RSPJ-JPN' にそろえる。"""
    out = []
    for m in re.finditer(r"\bRVL-(?:P-)?([A-Z0-9]{3}J)(?![A-Z0-9])", text.upper()):
        model = f"RVL-{m.group(1)}-JPN"
        if model not in out:
            out.append(model)
    return out


def _wii_code(model):
    m = re.fullmatch(r"RVL-([A-Z0-9]{3}J)-JPN", model or "")
    return m.group(1) if m else ""


def _wii_normalize_code(c):
    m = re.search(r"RVL-([A-Z0-9]{3}J)", c or "")
    return m.group(1) if m else ""


def _n64_models(text):
    """'NUS-NSMJ-JPN'、'NUS-P-NSMJ(JPN)' などを 'NUS-NSMJ-JPN' にそろえる。64DD は NUD-。"""
    out = []
    for m in re.finditer(r"\b(NUS|NUD)-(?:P-)?([A-Z0-9]{3}J)(?![A-Z0-9])", text.upper()):
        model = f"{m.group(1)}-{m.group(2)}-JPN"
        if model not in out:
            out.append(model)
    return out


def _n64_code(model):
    m = re.fullmatch(r"(?:NUS|NUD)-([A-Z0-9]{3}J)-JPN", model or "")
    return m.group(1) if m else ""


def _sfc_models(text):
    """SFC の日本版の型番。初期は 'SHVC-FZ' のような2〜3文字、後期は 'SHVC-ATGJ-JPN'。
    スーファミターボは 'SFT-0101-JPN'。メーカー独自の番号（'HUMAN No. 138' など）は含めない。"""
    out = []
    t = text.upper()
    for m in re.finditer(r"\bSHVC-(?:P-)?([A-Z0-9]{3}J)(?![A-Z0-9])|\bSHVC-([A-Z0-9]{2,3})(?![A-Z0-9-])|\bSFT-(\d{4})-JPN", t):
        if m.group(1):
            model = f"SHVC-{m.group(1)}-JPN"
        elif m.group(2):
            model = f"SHVC-{m.group(2)}"
        else:
            model = f"SFT-{m.group(3)}-JPN"
        if model not in out:
            out.append(model)
    return out


def _sfc_code(model):
    m = re.fullmatch(r"SHVC-([A-Z0-9]{3}J)-JPN", model or "")
    return m.group(1) if m else ""


def _sfc_media(row):
    return "sufami_turbo" if row.get("title", "").startswith("スーファミターボ専用") else "cartridge"


def _fc_models(text):
    """FC・ディスクシステムの型番。会社ごとに形式がばらばら（'HVC-ZL'、'BAN-HDR'、'IF-02'、'FMC-ZEL' など）なので
    表記のまま取り出す。MAME が独自に付けたもの（'DATACH-…'、'BA-KARAOKE-…'）は型番ではないので除く。"""
    out = []
    for tok in re.split(r"[\s/,、／;・]+", (text or "").upper()):
        tok = tok.strip("()（）[]")
        if (re.fullmatch(r"[A-Z0-9]+(?:-[A-Z0-9.]+)+", tok) and not re.match(r"DATACH-|BA-KARAOKE|NES-", tok)
                and not re.search(r"-(USA|CAN|EEC|EUR|NOE|FRG|FRA|GBR|UKV|ESP|ITA|SCN|AUS|HOL)$", tok)):
            if tok not in out:
                out.append(tok)
    return out


def _fds_channel(row):
    """Wikipedia の「販路」列: 書=書き換え専用、パ=パッケージ販売専用、空欄=両方。"""
    v = row.get("d_channel", "")
    return "rewrite_only" if "書" in v else "package_only" if "パ" in v else "both"


def _circle(col):
    return lambda row: "yes" if re.search(r"[○◯〇]", row.get(col, "")) else ""


def _md_models(text):
    """メガドライブ・メガCD・32X の型番（セガ 'G-4128'、ライセンシー 'T-66013'、32X 'GM-4002'、
    エレクトロニック・アーツ・ビクター 'EM20003'）。
    MAME の 'G-5514 (Jpn), MK-1135-50 (Euro)' のような並記からは海外版の部分を除く。"""
    out = []
    for part in re.split(r",|;|/", text or ""):
        if re.search(r"\((Euro|Eur|USA|US|Kor|Bra|Asia)", part, re.I):
            continue
        for m in re.finditer(r"(?<![A-Z0-9-])((?:GM|G|T)-\d{4,6}|EM\d{5})(?![\d])", part.upper()):
            if m.group(1) not in out:
                out.append(m.group(1))
    return out


def _md_jp_models(serial):
    """MAME で説明に Japan が無くても、シリアルに '(Jpn)' とあれば日本版。"""
    return _md_models(serial) if re.search(r"jpn", serial or "", re.I) else []


def _md_code(serial):
    """Redump のシリアル（ディスクのレーベル面の型番。'T-93175'）を型番の形にそろえる。"""
    s = (serial or "").replace(" ", "")
    m = re.match(r"((?:GM|G|T)-\d{4,6})", s)
    return m.group(1) if m else ""


def _md_service(row):
    """配信専用タイトルのサービス（本リストに載せないもの）。"""
    n = row.get("notes", "")
    if re.search(r"『ゲーム図書館』(配信タイトル|でのみ配信)", n):
        return "game_toshokan"
    if "MEGAターミナル必須" in n:
        return "mega_terminal"
    if re.search(r"(^|\s|日本では)セガチャンネル専用", n) and "北米ではセガチャンネル専用" not in n:
        return "sega_channel"
    return ""


_MD_TABLE = {"page": "メガドライブのゲームタイトル一覧", "section": "発売されたライセンスゲームタイトル",
             "table_id": "softwarelist", "columns": ("jp", "na", "eu", "br", "title", "publisher", "notes")}


def _pce_models(text):
    """PCエンジンの型番（'HC62005'、'H49G-1001'、'NAPR-1051'、'HCD0008'、'TJCD1018' など。会社ごとに形式が違う）。
    MAME の 'TICD6006 (R-660034)' のような括弧内の別番号や、'HCD0012 / HCD0011 (w/ audio CD)' の2つ目は採らない。"""
    out = []
    for part in re.split(r"[,/;]", re.sub(r"\([^)]*\)", "", (text or "").upper())):
        for m in re.finditer(r"(?<![A-Z0-9-])([A-Z][A-Z0-9]{1,4}[- ]?\d{3,6}[A-Z]?)(?![A-Z0-9])", part):
            if m.group(1) not in out:
                out.append(m.group(1))
    return out


def _pce_key(model):
    """型番のハイフン・空白の有無の違い（'NAPR-1051' と 'NAPR1051'）を照合では同じとみなす。"""
    return re.sub(r"[- ]", "", model or "")


_PCE_FORMATS = {"HC": "hucard", "SG": "supergrafx", "CR": "cd_rom2", "SC": "super_cd_rom2", "AC": "arcade_card"}


def _pce_format(row):
    return "/".join(_PCE_FORMATS[c] for c in re.findall(r"HC|SG|CR|SC|AC", row.get("d_format", "")))


def _ss_models(text):
    """セガサターンの型番。セガ 'GS-9001'、ライセンシー 'T-14301G'（末尾 G が日本版）、Hiサターン等 'HSS-…'、
    セガの商品番号 '610-6xxx'、ビクター 'VS010-J1'。セガ・ライセンシーの型番を優先し、海外版（'T-…H'、'MK-…'）は採らない。"""
    found = []
    for part in re.split(r"[,/]", (text or "").upper()):
        part = re.sub(r"\((?!VS)[^)]*\)", "", part)
        for m in re.finditer(r"(?<![A-Z0-9-])(GS-\d{4}|T-\d{4,5}G|HSS-\d{4}|610-\d{4,5}(?:-\d{2,3})?|VS\d{3}-J\d)(?![A-Z0-9])",
                             part):
            if m.group(1) not in found:
                found.append(m.group(1))
    rank = lambda c: 0 if re.match(r"GS-|T-", c) else 1 if c.startswith("HSS") else 2
    return sorted(found, key=rank)


def _ss_code(serial):
    """Redump のシリアル（'T-15013G'、'GS-9001'、'T-4305G-50' など）を型番の形に。"""
    m = _ss_models(re.sub(r"-\d{1,2}$", "", serial or ""))
    return m[0] if m else ""


def _age_rating(row):
    """Wikipedia の備考の年齢区分（X指定=18歳未満購入禁止、18歳以上推奨）。"""
    n = row.get("notes", "")
    return "X" if "X指定" in n else "18+" if "18歳以上推奨" in n else ""


def _ps_models(text):
    """PS1 の日本版の型番（SCE 'SCPS-10001'、他社 'SLPS-01234' / 'SLPM-86001'、ほか 'SIPS-'・'PAPX-' など）。
    複数枚組の範囲表記（'SLPS-01234~6'）や Redump のディスク番号付き（'SLPS-01234-5'）からは先頭の型番を取る。
    海外版（SLUS・SLES・SCES など）は採らない。"""
    out = []
    for m in re.finditer(r"(?<![A-Z])(SCPS|SLPS|SLPM|SCPM|SIPS|PAPX|SCZS|SCAJ|PBPX|PCPX|SCCS)[- ]?(\d{5})", (text or "").upper()):
        c = f"{m.group(1)}-{m.group(2)}"
        if c not in out:
            out.append(c)
    return out


def _ps_code(serial):
    m = _ps_models(serial)
    return m[0] if m else ""


def _ps3_models(text):
    """PS3 の日本版の型番（'BLJM-60001'、'BLJS-10001'、'BCJS-30001'、配信の 'NPJA-00001' など）。"""
    out = []
    for m in re.finditer(r"(?<![A-Z])(BLJM|BLJS|BCJS|BCJM|BLJX|BCJX|BCJB|NPJA|NPJB)[- _]?(\d{5})", (text or "").upper()):
        c = f"{m.group(1)}-{m.group(2)}"
        if c not in out:
            out.append(c)
    return out


def _ps3_code(serial):
    m = _ps3_models(serial)
    return m[0] if m else ""


def _mark(col):
    """一覧の「●=対応、○=専用」の列を 'yes' / 'only' に。"""
    return lambda row: "only" if "○" in row.get(col, "") else "yes" if "●" in row.get(col, "") else ""


def _gg_models(text):
    """ゲームギアの型番（セガ 'G-3327'、ライセンシー 'T-44017'）。MAME の並記からは日本版（'(JPN)' 付きがあればそれ）を取り、
    再販の名作コレクション（'(Meisaku Collection)'）の型番は採らない。"""
    parts = [p for p in re.split(r",", text or "") if "Meisaku" not in p]
    if any("JPN" in p for p in parts):
        parts = [p for p in parts if "JPN" in p]
    out = []
    for p in parts:
        for m in re.finditer(r"(?<![A-Z0-9-])([GT]-\d{4,6})(?!\d)", p.upper()):
            if m.group(1) not in out:
                out.append(m.group(1))
    return out


def _ws_models(text):
    """ワンダースワンの型番。'SWJ-BAN001'（モノクロ・カラー対応）、'SWJ-BANC01'（カラー専用は多くが C 付き。
    末尾 3 文字は 16 進）、mama Mitte' の 'MM-280'、WWGP 入賞作の 'WWGP2001A3'。
    MADB の 'SWJ-SUMCO7' のような O と 0 の誤記は 0 にそろえる。"""
    out = []
    for m in re.finditer(r"\b(?:SWJ-([A-Z]{3})([0-9A-Z]{3})|(MM-\d{3})|(WWGP\d{4}[A-Z0-9]{2}))\b", (text or "").upper()):
        code = f"SWJ-{m.group(1)}{m.group(2).replace('O', '0')}" if m.group(1) else (m.group(3) or m.group(4))
        if code not in out:
            out.append(code)
    return out


def _sms_models(text):
    """マークIII／マスターシステムの日本版の型番。セガのゴールドカートリッジ 'G-1301'、マイカード マークIII 'C-501'、
    サリオのシルバーカートリッジ 'S-001'。MAME の並記（'G-1305, 5055, 41008'）の数字だけのものは海外版なので採らない。"""
    out = []
    for m in re.finditer(r"(?<![A-Z0-9-])([GCS])\s*-\s*(\d{3,4})(?!\d)", unicodedata.normalize("NFKC", text or "").upper()):
        code = f"{m.group(1)}-{m.group(2)}"
        if code not in out:
            out.append(code)
    return out


def _sms_media(row):
    """媒体の欄（'Ca<sup>日欧米</sup><br />256k<sup>欧伯</sup>' → 'Ca日欧米 256k欧伯'）から日本版のものを取る。
    地域の付かない値は全地域共通。Ca はマイカード マークIII（256キロビット）、ほかはカートリッジの容量。"""
    raw = re.sub(r'^.*\|', "", row.get("media_raw", ""))
    for tok in raw.split():
        m = re.fullmatch(r"(Ca|\d+[kM])([日米欧伯]*)", tok)
        if m and (not m.group(2) or "日" in m.group(2)):
            return m.group(1)
    return ""


def _sg_models(text):
    """SC-3000／SG-1000 の型番。カートリッジ 'G-1033'、マイカード 'C-33'、オセロマルチビジョン 'OM-G004'、
    SC-3000 の教育用ソフト 'E-101'。MADB の全角（'Ｇ-1011'）やハイフン抜け（'G1033'）もそろえる。"""
    out = []
    for m in re.finditer(r"(?<![A-Z0-9-])(OM-G|G|C|E)-?(\d{2,4})(?!\d)", unicodedata.normalize("NFKC", text or "").upper()):
        code = f"{m.group(1)}-{m.group(2)}" if m.group(1) != "OM-G" else f"OM-G{m.group(2)}"
        if code not in out:
            out.append(code)
    return out


def _sg_date(row):
    """発売日の表記（release_date_text）から分かる精度の日付にする。日まであれば YYYY-MM-DD、
    月まで（上旬・中旬・下旬を含む）なら YYYY-MM、季節・範囲（「11-12月」）・疑問符付きは YYYY。"""
    t = row.get("release_date_text", "")
    y = re.match(r"(\d{4})年", t)
    if not y:
        return ""
    if "?" in t or "？" in t:
        return y.group(1)
    m = re.fullmatch(r"(\d{4})年(\d{1,2})月(\d{1,2})日", t)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.match(r"(\d{4})年(\d{1,2})月", t)
    return f"{m.group(1)}-{int(m.group(2)):02d}" if m else y.group(1)


def _sg_media(row):
    """媒体の欄（Ca＝ゲームカートリッジ For SC/SG、Mc＝セガ マイカード）。両方に○があるのはカートリッジの後にマイカードで再販されたもの。"""
    media = [name for col, name in (("ca", "cartridge"), ("mc", "card")) if re.search(r"[○◯〇]", row.get(col, ""))]
    return ";".join(media)


def _sg_card_model(row):
    """カートリッジの後にマイカードで再販されたものの、マイカードの型番（'C-33'）。"""
    if "cartridge" not in row.get("media", "") or "card" not in row.get("media", ""):
        return ""
    return next((c for c in row.get("_codes", []) if c.startswith("C-") and c != row.get("model_number")), "")


def _ngp_models(text):
    """ネオジオポケットの型番。MAME は 'NeoP00010'、MADB は 'NEOP00040' と書くので大文字にそろえる。"""
    out = []
    for m in re.finditer(r"(?<![A-Z0-9])NEOP\d{5}(?!\d)", (text or "").upper()):
        if m.group(0) not in out:
            out.append(m.group(0))
    return out


def _neogeo_models(text):
    """家庭用ネオジオ（AES）の型番 'NGH-001'・'NGH-2650'。業務用（MVS）の 'NGM-' は採らない。"""
    out = []
    for m in re.finditer(r"(?<![A-Z0-9-])NGH-\d{3,4}(?!\d)", unicodedata.normalize("NFKC", text or "").upper()):
        if m.group(0) not in out:
            out.append(m.group(0))
    return out


def _neocd_models(text):
    """ネオジオCD の型番。SNK 'NGCD-083'、ADK 'ADCD-102'、データイースト 'DECD-'、アイレム？ 'AICD-'。
    Redump の末尾 'E'（海外版 'NGCD-096E'）は日本版の型番と別のものとして残す。"""
    out = []
    for m in re.finditer(r"(?<![A-Z0-9-])([A-Z]{2}CD-[0-9A-Z]{3,5})(?![0-9A-Z])", unicodedata.normalize("NFKC", text or "").upper()):
        if m.group(1) not in out:
            out.append(m.group(1))
    return out


def _neogeo_rental(row):
    """1990年の家庭用ネオジオはレンタル用。店頭での販売は 1991年7月1日（廉価版）から。"""
    return "yes" if row.get("release_date", "") < "1991-07-01" else ""


def _pcfx_models(text):
    """PC-FX の型番（'FXNHE626'、'FXHUD401'、'FXNKT601' など）。MADB の 'FXNHE 626' やバーコード付きの表記、
    Redump の枚数付き（'FXNHE627-2'）・末尾 A（'FXHUD405A'）からは型番だけを取る。PC-FXGA 用（'GANHE'）は採らない。"""
    out = []
    for m in re.finditer(r"(?<![A-Z])(FX[A-Z]{3}) ?(\d{3})", unicodedata.normalize("NFKC", text or "").upper()):
        code = m.group(1) + m.group(2)
        if code not in out:
            out.append(code)
    return out


def _cell_value(s):
    """表のセルに残った書式指定（'style="text-align:center" | SLG'）を除く。"""
    return re.sub(r'^\s*[a-z]+="[^"]*"\s*\|\s*', "", s or "").strip()


def _3do_models(text):
    """3DO の日本版の型番。松下系 'FZ-SJ1351'（'FZ-SJ-1351' もそろえる）、三洋系 'IMP-SA0701'、ほか MADB の
    'AMCD1234'・'PCRA-12345'・'VZ123'。Redump の枚数付き（'FZ-SJ1234-1'）・末尾の印（'FZ-SJ1234R'）からは型番だけを取る。"""
    out = []
    t = unicodedata.normalize("NFKC", text or "").upper()
    for m in re.finditer(r"(?<![A-Z0-9])(?:FZ-?SJ-?(\d{4})|IMP-(S[A-Z])(\d{4})|AMCD(\d{4})|PCRA-(\d{5})|VZ(\d{3}))(?!\d)", t):
        if m.group(1):
            code = f"FZ-SJ{m.group(1)}"
        elif m.group(2):
            code = f"IMP-{m.group(2)}{m.group(3)}"
        elif m.group(4):
            code = f"AMCD{m.group(4)}"
        elif m.group(5):
            code = f"PCRA-{m.group(5)}"
        else:
            code = f"VZ{m.group(6)}"
        if code not in out:
            out.append(code)
    return out


def _3do_channel(row):
    """流通系統。松下系の型番は FZ-、三洋系は IMP- で始まる（Wikipedia「3DOのゲームタイトル一覧」）。"""
    m = row.get("model_number", "")
    return "panasonic" if m.startswith("FZ-") else "sanyo" if m.startswith("IMP-") else ""


def _xbox_models(text):
    """Xbox のパッケージの品番（'M5F-00012'）。MADB の 'A4K 00001'・'55F00001' のような区切りの違いをそろえる。
    Redump のシリアル（'MS-055'。ソフト内部のタイトル ID）は品番ではないので対象にならない。"""
    out = []
    for m in re.finditer(r"(?<![A-Z0-9])([A-Z0-9]{3})[- ]?(\d{5})(?![0-9A-Z])", unicodedata.normalize("NFKC", text or "").upper()):
        code = f"{m.group(1)}-{m.group(2)}"
        if code not in out:
            out.append(code)
    return out


_X360_COLUMNS = ("jp", "na", "eu", "title", "publisher", "media", "notes", "bc", "refs")
_X360_DERIVE = {
    "download_too": lambda r: "yes" if "◎" in r.get("media", "") else "",   # パッケージとダウンロードの両方で発売
    "xone_compat": lambda r: "yes" if re.match(r"\s*[○〇]", r.get("bc", "")) else "",
    "kinect": lambda r: "required" if "Kinect専用" in r.get("notes", "") else "supported" if "Kinect対応" in r.get("notes", "") else "",
}


def _dc_models(text):
    """ドリームキャストの型番。セガ 'HDR-0001'（'HADR-0092' も）、ライセンシー 'T-1201M'・'T-46701M'、セガのその他 '610-7055'。
    Redump の枚数付き（'T-1210M-0'）からは型番だけを取る。"""
    out = []
    t = unicodedata.normalize("NFKC", text or "").upper()
    for m in re.finditer(r"(?<![A-Z0-9-])(HA?DR-\d{4}|T-\d{4,5}M|610-\d{4})(?![0-9])", t):
        if m.group(1) not in out:
            out.append(m.group(1))
    return out


def _psp_models(text):
    """PSP の日本版の型番（'ULJM-05001'・'ULJS-00001'・'UCJS-10001'・'UCJM'・'UCJB'・'UCJX' など）。MADB の 'ULJM 05001'・'ULJM05001'
    もそろえる。日本・アジア共通の UMD に並ぶアジア版の型番（'ULAS-'・'UCAS-'）、配信版（'NPJH-'）は採らない。"""
    out = []
    for m in re.finditer(r"(?<![A-Z])(U[CL]J[A-Z])[- ]?(\d{5})(?!\d)", unicodedata.normalize("NFKC", text or "").upper()):
        code = f"{m.group(1)}-{m.group(2)}"
        if code not in out:
            out.append(code)
    return out


_PSP_COLUMNS = ("jp", "na", "eu", "title", "publisher", "dl", "notes", "refs")
_PSP_DERIVE = {
    "vita_compat": lambda r: "yes" if re.search(r"[●○▲]", r.get("dl", "")) else "",   # PS Vita で遊べる
    "umd_passport": lambda r: "yes" if "●" in r.get("dl", "") else "",
}


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
    # NINTENDO 64。64DD のソフトは別リスト（jp_64dd.csv）
    "n64": {
        "name": "NINTENDO 64",
        "dir": ROOT / "data" / "n64",
        "id_prefix": "n64-jp",
        "wikipedia": {
            "tables": [
                {"page": "NINTENDO 64のゲームタイトル一覧", "section": "発売されたNINTENDO 64のタイトル",
                 "table_id": "softwarelist", "columns": ("jp", "na", "eu", "title", "publisher", "notes")},
            ],
        },
        "extra_lists": {
            "64dd": {
                "out": "jp_64dd.csv",
                "id_suffix": "64dd",
                "tables": [{"page": "NINTENDO 64のゲームタイトル一覧", "section": "発売された64DDのタイトル",
                            "columns": ("jp", "title", "publisher", "notes")}],
            },
        },
        "madb_platforms": ["NINTENDO 64"],
        "mame_lists": ["n64"],
        "mame_jp_models": _n64_models,
        "nointro_dats": ["Nintendo - Nintendo 64"],
        "nointro_export": ["Nintendo 64 (DB Export)"],
        "nointro_export_fallback": {"Nintendo 64 (DB Export)": "Nintendo - Nintendo 64"},
        "models_from": _n64_models,
        "models_from_serial": lambda s: [f"NUS-{s}-JPN"] if re.fullmatch(r"[A-Z0-9]{3}J", s) else [],
        "code_of": _n64_code,
        "normalize_code": _gba_normalize_code,
    },
    # スーパーファミコン。ニンテンドウパワーは別リスト、サテラビューは対象外。
    # スーファミターボ用ソフトは本リストに含め、media 列で区別する
    "sfc": {
        "name": "スーパーファミコン",
        "dir": ROOT / "data" / "sfc",
        "id_prefix": "sfc-jp",
        "wikipedia": {
            "tables": [
                {"page": "スーパーファミコンのゲームタイトル一覧", "section": "発売されたタイトル",
                 "table_id": "softwarelist", "columns": ("jp", "na", "eu", "title", "publisher", "notes")},
            ],
        },
        "extra_columns": ["media"],
        "derive": {"media": _sfc_media},
        "madb_platforms": ["スーパーファミコン"],
        "mame_lists": ["snes", "snes_strom"],
        "mame_jp_models": _sfc_models,
        "nointro_dats": ["Nintendo - Super Nintendo Entertainment System", "Nintendo - Sufami Turbo"],
        "nointro_export": ["Super Nintendo Entertainment System (DB Export)", "Sufami Turbo (DB Export)"],
        "nointro_export_fallback": {
            "Super Nintendo Entertainment System (DB Export)": "Nintendo - Super Nintendo Entertainment System",
            "Sufami Turbo (DB Export)": "Nintendo - Sufami Turbo"},
        "models_from": _sfc_models,
        "models_from_serial": lambda s: [],   # DAT にシリアルがほぼ無いので型番の検証には使わない
        "code_of": _sfc_code,
        "normalize_code": _gba_normalize_code,
        "nintendo_power": {"page": "ニンテンドウパワーのゲームタイトル一覧", "section": "スーパーファミコン"},
    },
    # Wii（ディスクソフト）。Wiiウェアは別リスト、バーチャルコンソール・Wiiチャンネルは対象外
    # ファミリーコンピュータ（ROM カセット）。ディスクシステムは別リスト（機種キー fds、data/fc/disk_system/）。
    # 型番は会社ごとの表記のまま。ハッシュは iNES ヘッダーを除いた ROM 本体（No-Intro の .unh）
    "fc": {
        "name": "ファミリーコンピュータ",
        "dir": ROOT / "data" / "fc",
        "id_prefix": "fc-jp",
        "wikipedia": {
            "tables": [
                {"page": "ファミリーコンピュータのゲームタイトル一覧", "section": "発売されたタイトル",
                 "table_id": "softwarelist", "columns": ("jp", "na", "eu", "title", "publisher", "notes", "refs")},
            ],
        },
        "madb_platforms": ["ファミリーコンピュータ"],
        "madb_filter": lambda x: "ディスクカード" not in x["media_format"],
        "mame_lists": ["nes", "nes_datach", "nes_kstudio"],
        "mame_jp_models": _fc_models,   # 'Super Mario Bros. (World)' のように日米共通のもの（シリアルに HVC-SM）
        "dump_world": True,
        "nointro_dats": ["Nintendo - Nintendo Entertainment System"],
        "nointro_export": ["Nintendo Entertainment System (Headerless) (DB Export)"],
        "nointro_export_fallback": {
            "Nintendo Entertainment System (Headerless) (DB Export)": "Nintendo - Nintendo Entertainment System"},
        "models_from": _fc_models,
        "models_from_serial": lambda s: [],   # DAT にシリアルが無い
        "code_of": lambda m: "",               # ROM にゲームコードが無い（吸い出しは名前・CRC で結びつける）
        "normalize_code": lambda c: "",
        "tax_free_before": "1989-04-01",
        "match_date_only": True,
    },
    # ファミリーコンピュータ ディスクシステム（FC の別リスト）。ハッシュは .fds（No-Intro。.qd は採らない）
    "fds": {
        "name": "ディスクシステム",
        "dir": ROOT / "data" / "fc" / "disk_system",
        "id_prefix": "fds-jp",
        "wikipedia": {
            "tables": [
                {"page": "ファミリーコンピュータ ディスクシステムのゲームタイトル一覧", "section": "発売されたタイトル",
                 "table_id": "softwarelist",
                 "columns": ("jp", "title", "publisher", "d_port", "d_single", "d_channel", "notes")},
            ],
        },
        "extra_columns": ["sales_channel", "port_of_cartridge", "single_sided"],
        "derive": {"sales_channel": _fds_channel, "port_of_cartridge": _circle("d_port"),
                   "single_sided": _circle("d_single")},
        "madb_platforms": ["ファミリーコンピュータ"],
        "madb_filter": lambda x: "ディスクカード" in x["media_format"],   # パッケージ版の価格（書き換え料金の出典は無い）
        "mame_lists": ["famicom_flop"],
        "mame_jp_models": lambda s: [s] if s else [],   # 説明に (Japan) が無い（全て日本のソフト）
        "nointro_dats": ["Nintendo - Family Computer Disk System"],
        "nointro_export": ["Family Computer Disk System (FDS) (DB Export)"],
        "nointro_export_fallback": {
            "Family Computer Disk System (FDS) (DB Export)": "Nintendo - Family Computer Disk System"},
        "models_from": _fc_models,
        "models_from_serial": lambda s: [],   # DAT のシリアルはディスク内のゲームコード（'GFJE'）で型番ではない
        # ディスク内のゲームコードの先頭3文字は、たいてい型番の末尾と同じ（'SSD-ADA' ↔ 'ADA'、'FSC-GFJE' ↔ 'GFJE'）
        "code_of": lambda m: m.split("-")[-1][:3] if m and "-" in m else "",
        "normalize_code": lambda c: c[:3] if re.fullmatch(r"[A-Z0-9]{3,4}", c) else "",
        "media": "disk",
        "tax_free_before": "1989-04-01",
        "match_date_only": True,
    },
    # メガドライブ（カートリッジ）。メガCD・スーパー32X は別リスト（機種キー mcd・32x、data/md/ の下）。
    # ゲーム図書館・セガチャンネル・MEGAターミナルの配信専用タイトルは jp_online.csv（--list online）
    "md": {
        "name": "メガドライブ",
        "dir": ROOT / "data" / "md",
        "id_prefix": "md-jp",
        "wikipedia": {"tables": [{**_MD_TABLE, "row_filter": lambda r: not _md_service(r)}]},
        "extra_lists": {
            "online": {
                "out": "jp_online.csv",
                "id_suffix": "online",
                "tables": [{**_MD_TABLE, "row_filter": _md_service, "derive": {"service": _md_service}}],
            },
        },
        "madb_platforms": ["メガドライブ"],
        "madb_filter": lambda x: "カートリッジ" in x["media_format"] and not x["product_id"].startswith("GM-"),
        "mame_lists": ["megadriv"],
        "mame_jp_models": _md_jp_models,
        "nointro_dats": ["Sega - Mega Drive - Genesis"],
        "nointro_export": ["Sega - Mega Drive - Genesis (DB Export)"],
        "nointro_export_fallback": {"Sega - Mega Drive - Genesis (DB Export)": "Sega - Mega Drive - Genesis"},
        "models_from": _md_models,
        # ROM ヘッダのコードはパッケージの型番と一致しないことが多い（獣王記 G-4001 ↔ '00054002-00'、
        # 32X は 'MK-84508-00'）ため、型番の検証にも吸い出しとの対応にも使わない（MAME の CRC と名前で結びつける）
        "models_from_serial": lambda s: [],
        "code_of": lambda m: "",
        "normalize_code": lambda c: "",
        "dump_world": True,
        "tax_free_before": "1989-04-01",
    },
    # メガCD（メガドライブの別リスト）。ハッシュは Redump（libretro 収録 DAT）
    "mcd": {
        "name": "メガCD",
        "dir": ROOT / "data" / "md" / "mega_cd",
        "id_prefix": "mcd-jp",
        "wikipedia": {"tables": [{"page": "メガCDのゲームタイトル一覧", "section": "発売されたタイトル",
                                  "table_id": "softwarelist",
                                  "columns": ("jp", "na", "eu", "title", "publisher", "notes")}]},
        "madb_platforms": ["メガドライブ"],
        "madb_filter": lambda x: "カートリッジ" not in x["media_format"],
        "mame_lists": ["megacd"],
        "mame_jp_models": _md_jp_models,
        "nointro_dats": ["redump:Sega - Mega-CD - Sega CD"],
        "nointro_export": ["Sega - Mega-CD (Redump)"],
        "nointro_export_fallback": {"Sega - Mega-CD (Redump)": "redump:Sega - Mega-CD - Sega CD"},
        "models_from": _md_models,
        "models_from_serial": lambda s: [c for c in [_md_code(s)] if c],
        "code_of": lambda m: m or "",
        "normalize_code": _md_code,
        "hash_source": "Redump",
        "media": "disc",
    },
    # スーパー32X（メガドライブの別リスト）。MADB では型番 GM- のカートリッジ
    "32x": {
        "name": "スーパー32X",
        "dir": ROOT / "data" / "md" / "32x",
        "id_prefix": "32x-jp",
        "wikipedia": {"tables": [{"page": "スーパー32Xのゲームタイトル一覧", "section": "発売されたタイトル",
                                  "table_id": "softwarelist",
                                  "columns": ("jp", "na", "eu", "br", "title", "publisher", "notes")}]},
        "madb_platforms": ["メガドライブ"],
        "madb_filter": lambda x: x["product_id"].startswith("GM-"),
        "mame_lists": ["32x"],
        "mame_jp_models": _md_jp_models,
        "nointro_dats": ["Sega - 32X"],
        "nointro_export": ["Sega - 32X (DB Export)"],
        "nointro_export_fallback": {"Sega - 32X (DB Export)": "Sega - 32X"},
        "models_from": _md_models,
        # ROM ヘッダのコードはパッケージの型番と一致しないことが多い（獣王記 G-4001 ↔ '00054002-00'、
        # 32X は 'MK-84508-00'）ため、型番の検証にも吸い出しとの対応にも使わない（MAME の CRC と名前で結びつける）
        "models_from_serial": lambda s: [],
        "code_of": lambda m: "",
        "normalize_code": lambda c: "",
        "dump_world": True,
    },
    # PCエンジン。HuCARD と CD-ROM は1つのリストで format 列で区別する（Wikipedia の「規格」列）。
    # Wikipedia「その他」節（販売経路が分からない幼児向けソフト）は jp_other.csv（--list other）
    "pce": {
        "name": "PCエンジン",
        "dir": ROOT / "data" / "pce",
        "id_prefix": "pce-jp",
        "wikipedia": {"tables": [
            {"page": "PCエンジンのゲームタイトル一覧", "section": "発売されたタイトル", "table_id": table_id,
             "columns": ("jp", "na", "title", "publisher", "d_format", "genre", "notes", "refs")}
            for table_id in ("softwarelist", "softwarelist2")]},
        "extra_lists": {
            "other": {
                "out": "jp_other.csv",
                "id_suffix": "other",
                "tables": [{"page": "PCエンジンのゲームタイトル一覧", "section": "その他",
                            "columns": ("jp", "title", "publisher", "d_format", "notes", "refs"),
                            "derive": {"format": _pce_format}}],
            },
        },
        "extra_columns": ["format", "genre"],
        "derive": {"format": _pce_format},
        "madb_platforms": ["PCエンジン"],
        "mame_lists": ["pce", "sgx", "pcecd"],
        "mame_all_japanese": ["pce", "sgx"],   # 日本版だけのリスト（説明に地域が無い）
        "models_from": _pce_models,
        "models_from_serial": lambda s: _pce_models(s),
        "model_key": _pce_key,
        # 型番の No-Intro・Redump での確認は CD だけ（HuCARD の DAT にはシリアルが無い）
        "nointro_model_check": lambda r: "cd" in r.get("format", "") or "arcade" in r.get("format", ""),
        "nointro_dats": ["NEC - PC Engine - TurboGrafx 16", "NEC - PC Engine SuperGrafx",
                         "redump:NEC - PC Engine CD - TurboGrafx-CD"],
        "nointro_export": ["NEC - PC Engine - TurboGrafx 16 (DB Export)", "NEC - PC Engine SuperGrafx (DB Export)",
                           "NEC - PC Engine CD (Redump)"],
        "nointro_export_fallback": {
            "NEC - PC Engine - TurboGrafx 16 (DB Export)": "NEC - PC Engine - TurboGrafx 16",
            "NEC - PC Engine SuperGrafx (DB Export)": "NEC - PC Engine SuperGrafx",
            "NEC - PC Engine CD (Redump)": "redump:NEC - PC Engine CD - TurboGrafx-CD"},
        # CD は Redump のシリアル（レーベル面の型番）で結びつける。HuCARD は DAT にシリアルが無い
        "code_of": _pce_key,
        "normalize_code": _pce_key,
        "tax_free_before": "1989-04-01",
    },
    # セガサターン。age_rating は Wikipedia の備考（X指定・18歳以上推奨）から
    "ss": {
        "name": "セガサターン",
        "dir": ROOT / "data" / "ss",
        "id_prefix": "ss-jp",
        "wikipedia": {"tables": [{"page": "セガサターンのゲームタイトル一覧", "section": "発売されたタイトル",
                                  "table_id": "softwarelist",
                                  "columns": ("jp", "na", "eu", "title", "publisher", "notes", "refs")}]},
        "extra_columns": ["age_rating"],
        "derive": {"age_rating": _age_rating},
        "madb_platforms": ["セガサターン"],
        "mame_lists": ["saturn"],
        "mame_jp_models": _ss_models,   # 説明に地域の無い日本版（'Waku Waku 7'、シリアル T-1516G）
        "models_from": _ss_models,
        "models_from_serial": lambda s: [c for c in [_ss_code(s)] if c],
        "code_of": _ss_code,
        "normalize_code": _ss_code,
        "nointro_dats": ["redump:Sega - Saturn"],
        "nointro_export": ["Sega - Saturn (Redump)"],
        "nointro_export_fallback": {"Sega - Saturn (Redump)": "redump:Sega - Saturn"},
        "hash_source": "Redump",
        "media": "disc",
    },
    # PlayStation（初代）。Wikipedia の年別ページ（再販の廉価版は載っていない）。型番は複数枚組でも先頭ディスクのもの
    "ps": {
        "name": "PlayStation",
        "dir": ROOT / "data" / "ps",
        "id_prefix": "ps-jp",
        "wikipedia": {"tables": [
            {"page": "PlayStationのゲームタイトル一覧 (1994年-1995年)", "section": "1994年（全17タイトル）", "year": "1994"},
            {"page": "PlayStationのゲームタイトル一覧 (1994年-1995年)", "section": "1995年（全132タイトル）", "year": "1995"},
        ] + [{"page": f"PlayStationのゲームタイトル一覧 ({y}年)", "section": f"{y}年", "year": str(y)}
             for y in range(1996, 2003)] + [
            {"page": "PlayStationのゲームタイトル一覧 (2003年-2004年)", "section": "2003年-2004年"},
        ]},
        "madb_platforms": ["プレイステーション"],
        "mame_lists": ["psx"],
        "mame_partial": True,   # MAME の psx リストは日本版の3分の1ほどしか無いので「MAME未照合」は報告しない
        "psxdc": "ps1",   # psxdatacenter.com の作品別ページ（発売日つき）で型番を補う
        "mame_jp_models": _ps_models,
        "models_from": _ps_models,
        "models_from_serial": lambda s: [c for c in [_ps_code(s)] if c],
        "code_of": _ps_code,
        "normalize_code": _ps_code,
        "nointro_dats": ["redump:Sony - PlayStation"],
        "nointro_export": ["Sony - PlayStation (Redump)"],
        "nointro_export_fallback": {"Sony - PlayStation (Redump)": "redump:Sony - PlayStation"},
        "hash_source": "Redump",
        "media": "disc",
        "tax_inclusive_from": "2004-04-01",
    },
    # PlayStation 2。2000〜2007年は年別ページ、2008年以降は一覧の本体ページの節。型番は PS と同じ形式（複数枚組は先頭）
    "ps2": {
        "name": "PlayStation 2",
        "dir": ROOT / "data" / "ps2",
        "id_prefix": "ps2-jp",
        "wikipedia": {
            # 2004年のページで発売日の欄が空になっている（作品の記事では 2004年11月27日）
            "date_fixes": {"ドラゴンクエストVIII 空と海と大地と呪われし姫君": "2004-11-27"},
            "tables": [
            {"page": "PlayStation 2のゲームタイトル一覧 (2000年-2001年)", "section": "2000年（全122タイトル）", "year": "2000"},
            {"page": "PlayStation 2のゲームタイトル一覧 (2000年-2001年)", "section": "2001年（全228タイトル）", "year": "2001"},
        ] + [{"page": f"PlayStation 2のゲームタイトル一覧 ({y}年)", "section": "発売されたタイトル", "year": str(y)}
             for y in range(2002, 2007)] + [
            {"page": "PlayStation 2のゲームタイトル一覧 (2007年)", "section": "2007年", "year": "2007"},
        ] + [{"page": "PlayStation 2のゲームタイトル一覧", "section": sec, "year": sec[:4]}
             for sec in ("2008年（全149タイトル）", "2009年（全78タイトル）", "2010年（全40タイトル）",
                         "2011年（全6タイトル）", "2013年（全1タイトル）")]},
        "madb_platforms": ["プレイステーション2"],
        "mame_lists": [],
        "psxdc": "ps2",   # psxdatacenter.com の一覧（題名だけで照合）で型番を補う
        "models_from": _ps_models,
        "models_from_serial": lambda s: [c for c in [_ps_code(s)] if c],
        "code_of": _ps_code,
        "normalize_code": _ps_code,
        "nointro_dats": ["redump:Sony - PlayStation 2"],
        "nointro_export": ["Sony - PlayStation 2 (Redump)"],
        "nointro_export_fallback": {"Sony - PlayStation 2 (Redump)": "redump:Sony - PlayStation 2"},
        "hash_source": "Redump",
        "media": "disc",
        "tax_inclusive_from": "2004-04-01",
    },
    # PlayStation 3。配信専用タイトルは jp_psn.csv（--list psn）。online / stereo3d は一覧の「オ」「3」列
    "ps3": {
        "name": "PlayStation 3",
        "dir": ROOT / "data" / "ps3",
        "id_prefix": "ps3-jp",
        "wikipedia": {"tables": [{"page": "PlayStation 3のゲームタイトル一覧", "section": "パッケージタイトル",
                                  "columns": ("jp", "title", "publisher", "d_online", "d_3d", "notes", "refs"),
                                  # タイトルのリンクの後に説明の無い「*」が付いている
                                  "strip_title_mark": "*"}]},
        "extra_lists": {
            "psn": {
                "out": "jp_psn.csv",
                "id_suffix": "psn",
                "tables": [{"page": "PlayStation 3のゲームタイトル一覧", "section": "配信専用タイトル",
                            "columns": ("jp", "title", "publisher", "d_online", "notes", "refs"),
                            "derive": {"online": _mark("d_online")}, "strip_title_mark": "*"}],
            },
        },
        "extra_columns": ["online", "stereo3d"],
        "derive": {"online": _mark("d_online"), "stereo3d": _mark("d_3d")},
        "madb_platforms": ["プレイステーション3"],
        "madb_filter": lambda x: "ダウンロード" not in x["media_format"],
        "mame_lists": [],
        "models_from": _ps3_models,
        "models_from_serial": lambda s: [c for c in [_ps3_code(s)] if c],
        "code_of": _ps3_code,
        "normalize_code": _ps3_code,
        "nointro_dats": ["redump:Sony - PlayStation 3"],
        "nointro_export": ["Sony - PlayStation 3 (Redump)"],
        "nointro_export_fallback": {"Sony - PlayStation 3 (Redump)": "redump:Sony - PlayStation 3"},
        "hash_source": "Redump",
        "media": "disc",
        "tax_inclusive_from": "2004-04-01",
    },
    # ゲームギア
    "gg": {
        "name": "ゲームギア",
        "dir": ROOT / "data" / "gg",
        "id_prefix": "gg-jp",
        "wikipedia": {"tables": [{"page": "ゲームギアのゲームタイトル一覧", "section": "発売されたタイトル",
                                  "table_id": "softwarelist",
                                  "columns": ("jp", "na", "eu", "title", "publisher", "notes", "refs")}]},
        "madb_platforms": ["ゲームギア"],
        "mame_lists": ["gamegear"],
        "mame_jp_models": _gg_models,   # 日米共通の "(World)" など（米国版の型番は数字だけなので含まれない）
        "nointro_dats": ["Sega - Game Gear"],
        "nointro_export": ["Sega - Game Gear (DB Export)"],
        "nointro_export_fallback": {"Sega - Game Gear (DB Export)": "Sega - Game Gear"},
        "models_from": _gg_models,
        "models_from_serial": lambda s: [],   # DAT にシリアルが無い
        "code_of": lambda m: "",
        "normalize_code": lambda c: "",
        "dump_world": True,
        "tax_free_before": "1989-04-01",
    },
    # SC-3000／SG-1000（オセロマルチビジョン用を含む）。system 列で sc_sg / othello_mv（ツクダオリジナル）を区別する。
    # 発売日は日まで分からないものが多く、分かる精度（YYYY-MM-DD / YYYY-MM / YYYY）にして元の表記を release_date_text に残す
    "sg1000": {
        "name": "SC-3000／SG-1000",
        "dir": ROOT / "data" / "sg1000",
        "id_prefix": "sg1000-jp",
        "wikipedia": {"tables": [{
            "page": "SG-1000のゲームタイトル一覧", "section": "タイトルリスト", "strip_comments": True, "date_text": True,
            "columns": ("jp", "title", "publisher", "ca", "mc", "notes", "refs"),
            "row_filter": lambda r: r["release_date_text"] != "",   # {{Unreleased}}（未発売）・{{Unknown}}
            "derive": {"release_date": _sg_date, "media": _sg_media,
                       # 表示名の無いリンク [[ドロール_(ゲーム)]] の曖昧さ回避の部分（記事名がそのまま題名になる）
                       "title": lambda r: re.sub(r"[ _]*[(（]ゲーム[)）]$", "", r["title"]),
                       "system": lambda r: "othello_mv" if "ツクダ" in r["publisher"] else "sc_sg"},
        }]},
        # BASIC ソフト・教育用ソフト（SC-3000 専用。ゲームではない）は jp_non_game.csv（--list non_game）
        "extra_lists": {
            "non_game": {
                "out": "jp_non_game.csv",
                "id_suffix": "ng",
                "tables": [{"page": "SG-1000のゲームタイトル一覧", "section": sec, "strip_comments": True,
                            "date_text": True, "columns": ("jp", "title", "publisher", "ca", "mc", "notes", "refs"),
                            "row_filter": lambda r: r["release_date_text"] != "",
                            "derive": {"release_date": _sg_date, "category": lambda r, c=cat: c}}
                           for sec, cat in (("BASICソフト", "basic"), ("教育用ソフト", "education"))],
            },
        },
        "extra_columns": ["release_date_text", "system", "media", "card_model_number"],
        "derive": {"card_model_number": _sg_card_model},
        "madb_platforms": ["SC-3000,SG-1000", "SG-1000,SC-3000", "SEGAマーク3,SC-3000,SG-1000"],
        "mame_lists": ["sg1000"],
        "match_undated": 0.8,   # MAME に発売日が無く、Wikipedia も日まで分からないものが多い
        "models_from": _sg_models,
        "models_from_serial": lambda s: [],   # DAT にシリアルが無い
        "code_of": lambda m: "",
        "normalize_code": lambda c: "",
        "nointro_dats": ["Sega - SG-1000"],
        "nointro_export": ["Sega - SG-1000 (DB Export)"],
        "nointro_export_fallback": {"Sega - SG-1000 (DB Export)": "Sega - SG-1000"},
        "dump_world": True,
        "tax_free_before": "1989-04-01",
    },
    # セガ・マークIII／マスターシステム（日本で発売された 83 件。SG-1000 は別リスト）。
    # media は card（マイカード マークIII）/ cartridge、capacity は容量、fm_sound は FM 音源対応（Wikipedia の「FM音源」欄）
    "sms": {
        "name": "セガ・マークIII／マスターシステム",
        "dir": ROOT / "data" / "sms",
        "id_prefix": "sms-jp",
        "wikipedia": {"tables": [{
            "page": "セガ・マークIIIのゲームタイトル一覧", "section": "発売されたタイトル", "table_id": "softwarelist",
            "columns": ("jp", "na", "eu", "br", "title", "publisher", "media_raw", "fm", "notes"),
            "derive": {
                # 発売元の欄の地域の上付き文字（'セガ<sup>日欧</sup>' → 'セガ日欧'）を除く
                "publisher": lambda r: re.sub(r"[日米欧伯]+$", "", r["publisher"]),
                "media": lambda r: {"Ca": "card"}.get(_sms_media(r), "cartridge" if _sms_media(r) else ""),
                "capacity": lambda r: "256k" if _sms_media(r) == "Ca" else _sms_media(r),
                "fm_sound": lambda r: "yes" if re.search(r"[○◯〇]", r.get("fm", "")) else "",
            }}]},
        "extra_columns": ["media", "capacity", "fm_sound"],
        "madb_platforms": ["SEGAマーク3", "SEGAマーク3,セガ・マスターシステム"],
        "mame_lists": ["sms"],
        "mame_jp_models": _sms_models,   # 'After Burner (World)' など。海外版の型番は数字だけなので含まれない
        "models_from": _sms_models,
        "models_from_serial": lambda s: [],   # DAT にシリアルが無い
        "code_of": lambda m: "",
        "normalize_code": lambda c: "",
        "nointro_dats": ["Sega - Master System - Mark III"],
        "nointro_export": ["Sega - Master System - Mark III (DB Export)"],
        "nointro_export_fallback": {"Sega - Master System - Mark III (DB Export)": "Sega - Master System - Mark III"},
        "dump_world": True,
        "tax_free_before": "1989-04-01",
    },
    # ネオジオポケット／ネオジオポケットカラー。compat 列で ngp（モノクロ）/ ngpc_compatible（カラー対応）/ ngpc_only（カラー専用）
    "ngp": {
        "name": "ネオジオポケット／ネオジオポケットカラー",
        "dir": ROOT / "data" / "ngp",
        "id_prefix": "ngp-jp",
        "wikipedia": {"tables": [
            {"page": "ネオジオポケットのゲームタイトル一覧", "section": "ネオジオポケットのタイトル",
             "columns": ("jp", "title", "publisher", "notes"), "extra": {"compat": "ngp"}},
            {"page": "ネオジオポケットのゲームタイトル一覧", "section": "ネオジオポケットカラー対応のタイトル",
             "columns": ("jp", "na", "eu", "title", "publisher", "notes", "refs"), "extra": {"compat": "ngpc_compatible"}},
            {"page": "ネオジオポケットのゲームタイトル一覧", "section": "ネオジオポケットカラー専用のタイトル",
             "columns": ("jp", "na", "eu", "title", "publisher", "notes", "refs"), "extra": {"compat": "ngpc_only"}},
        ]},
        "extra_columns": ["compat"],
        "madb_platforms": ["ネオジオポケット"],
        "mame_lists": ["ngp", "ngpc"],
        "mame_jp_models": _ngp_models,   # 日本を含む共通版 '(World)'
        "models_from": _ngp_models,
        "models_from_serial": lambda s: [],   # DAT にシリアルが無い
        "code_of": lambda m: "",
        "normalize_code": lambda c: "",
        "nointro_dats": ["SNK - Neo Geo Pocket", "SNK - Neo Geo Pocket Color"],
        "nointro_export": ["SNK - Neo Geo Pocket (DB Export)", "SNK - Neo Geo Pocket Color (DB Export)"],
        "nointro_export_fallback": {"SNK - Neo Geo Pocket (DB Export)": "SNK - Neo Geo Pocket",
                                    "SNK - Neo Geo Pocket Color (DB Export)": "SNK - Neo Geo Pocket Color"},
        "dump_world": True,
    },
    # 家庭用ネオジオ（ROM。AES）。ネオジオCD は別リスト（neocd → data/neogeo/cd）。
    # ハッシュは No-Intro に無いため MAME neogeo.xml の ROM チップごと（scripts/build_mame_list.py ... --main）
    "neogeo": {
        "name": "ネオジオ",
        "dir": ROOT / "data" / "neogeo",
        "id_prefix": "neogeo-jp",
        "wikipedia": {"tables": [{
            "page": "ネオジオのゲームタイトル一覧", "section": "家庭用ネオジオのタイトル",
            "columns": ("jp", "title", "publisher", "genre", "ngcd", "notes", "refs"),
            "derive": {"cd_version": lambda r: "yes" if re.search(r"[○◯〇]", r.get("ngcd", "")) else "",
                       "rental": _neogeo_rental,
                       "notes": lambda r: (r["notes"] + (" " if r["notes"] else "") + "1991年7月1日に販売開始（廉価版）")
                       if _neogeo_rental(r) else r["notes"]},
        }]},
        "extra_columns": ["genre", "cd_version", "rental"],
        "madb_platforms": ["ネオジオ"],
        "mame_lists": ["neogeo"],
        "mame_all_japanese": ["neogeo"],   # 説明に地域が無い
        "mame_filter": lambda m: bool(_neogeo_models(m["serial"])),   # 家庭用（NGH-）の型番があるものだけ
        "mame_clone_filter": lambda serial: bool(_neogeo_models(serial)),   # 吸い出しも家庭用の版だけ
        "models_from": _neogeo_models,
        "models_from_serial": lambda s: [],
        "code_of": lambda m: "",
        "normalize_code": lambda c: "",
        "nointro_dats": [],
    },
    # ネオジオCD（ネオジオの別リスト）
    "neocd": {
        "name": "ネオジオCD",
        "dir": ROOT / "data" / "neogeo" / "cd",
        "id_prefix": "neocd-jp",
        "wikipedia": {"tables": [{
            "page": "ネオジオのゲームタイトル一覧", "section": "ネオジオCDのタイトル",
            "columns": ("jp", "title", "publisher", "ng", "notes", "refs"),
            "derive": {"rom_version": lambda r: "yes" if re.search(r"[○◯〇]", r.get("ng", "")) else ""},
        }]},
        "extra_columns": ["rom_version"],
        "madb_platforms": ["ネオジオCD"],
        "mame_lists": ["neocd"],
        "models_from": _neocd_models,
        "models_from_serial": _neocd_models,
        "code_of": lambda m: m or "",
        "normalize_code": lambda c: (_neocd_models(c) or [""])[0],
        "nointro_dats": ["redump:SNK - Neo Geo CD"],
        "nointro_export": ["SNK - Neo Geo CD (Redump)"],
        "nointro_export_fallback": {"SNK - Neo Geo CD (Redump)": "redump:SNK - Neo Geo CD"},
        "dump_world": True,
        "hash_source": "Redump",
        "media": "disc",
    },
    # PC-FX。age_rating は Wikipedia の「年齢制限」欄（18推奨 → 18+、18禁 → X）。雑誌付録（「その他」節）は非売品リスト
    "pcfx": {
        "name": "PC-FX",
        "dir": ROOT / "data" / "pcfx",
        "id_prefix": "pcfx-jp",
        "wikipedia": {"tables": [{
            "page": "PC-FXのゲームタイトル一覧", "section": "発売されたタイトル",
            "columns": ("jp", "title", "publisher", "genre", "age", "notes"),
            "derive": {"genre": lambda r: _cell_value(r["genre"]),
                       "age_rating": lambda r: {"18推奨": "18+", "18禁": "X"}.get(_cell_value(r.get("age", "")), "")},
        }]},
        "extra_columns": ["genre", "age_rating"],
        "madb_platforms": ["PC-FX"],
        "mame_lists": ["pcfx"],
        "mame_all_japanese": ["pcfx"],
        "models_from": _pcfx_models,
        "models_from_serial": _pcfx_models,
        "code_of": lambda m: m or "",
        "normalize_code": lambda c: (_pcfx_models(c) or [""])[0],
        "nointro_dats": ["redump:NEC - PC-FX"],
        "nointro_export": ["NEC - PC-FX (Redump)"],
        "nointro_export_fallback": {"NEC - PC-FX (Redump)": "redump:NEC - PC-FX"},
        "disc_subtitles": True,   # 複数枚組のディスクごとの副題（'(Disc A) (Hakua Kaikou)'）を組の判定で除く
        "hash_source": "Redump",
        "media": "disc",
    },
    # PSP。本リストはパッケージ（UMD）。配信専用（「DL」欄の ▲・△）は別リスト jp_download.csv（--list download）
    "psp": {
        "name": "PlayStation Portable",
        "dir": ROOT / "data" / "psp",
        "id_prefix": "psp-jp",
        "wikipedia": {"tables": [{
            "page": "PlayStation Portableのゲームタイトル一覧", "section": "発売されたタイトル", "table_id": "softwarelist",
            "columns": _PSP_COLUMNS, "row_filter": lambda r: not re.search(r"[▲△]", r.get("dl", "")), "derive": _PSP_DERIVE}]},
        "extra_lists": {
            "download": {
                "out": "jp_download.csv",
                "id_suffix": "dl",
                "tables": [{"page": "PlayStation Portableのゲームタイトル一覧", "section": "発売されたタイトル",
                            "table_id": "softwarelist", "columns": _PSP_COLUMNS,
                            "row_filter": lambda r: bool(re.search(r"[▲△]", r.get("dl", ""))), "derive": _PSP_DERIVE}],
            },
        },
        "extra_columns": ["vita_compat", "umd_passport"],
        "madb_platforms": ["プレイステーション・ポータブル"],
        "madb_filter": lambda x: x["media_format"] == "UMD",
        "mame_lists": [],
        "models_from": _psp_models,
        "models_from_serial": _psp_models,
        "code_of": lambda m: m or "",
        "normalize_code": lambda c: (_psp_models(c) or [""])[0],
        "dat_title_models": True,   # MADB で型番の決まらない行は Redump の題名とシリアルで補う（決まらないものは許容）
        "dat_title_sim": 0.75,
        "nointro_dats": ["redump:Sony - PlayStation Portable"],
        "nointro_export": ["Sony - PlayStation Portable (Redump)"],
        "nointro_export_fallback": {"Sony - PlayStation Portable (Redump)": "redump:Sony - PlayStation Portable"},
        "dump_world": True,
        "tax_inclusive_from": "2004-04-01",
        "hash_source": "Redump",
        "media": "disc",
    },
    # ドリームキャスト
    "dc": {
        "name": "ドリームキャスト",
        "dir": ROOT / "data" / "dc",
        "id_prefix": "dc-jp",
        "wikipedia": {"tables": [{"page": "ドリームキャストのゲームタイトル一覧", "section": "発売されたタイトル",
                                  "table_id": "softwarelist",
                                  "columns": ("jp", "na", "eu", "title", "publisher", "notes", "refs")}]},
        "madb_platforms": ["ドリームキャスト"],
        "mame_lists": ["dc"],
        "mame_jp_models": _dc_models,
        "models_from": _dc_models,
        "models_from_serial": _dc_models,
        "code_of": lambda m: m or "",
        "normalize_code": lambda c: (_dc_models(c) or [""])[0],
        "dat_title_models": True,   # MADB・MAME で型番の決まらない行は Redump の題名とシリアルで補う
        "nointro_dats": ["redump:Sega - Dreamcast"],
        "nointro_export": ["Sega - Dreamcast (Redump)"],
        "nointro_export_fallback": {"Sega - Dreamcast (Redump)": "redump:Sega - Dreamcast"},
        "dump_world": True,
        "tax_inclusive_from": "2004-04-01",
        "hash_source": "Redump",
        "media": "disc",
    },
    # Xbox 360。本リストはパッケージで出たもの（「媒体」欄が ◎〈パッケージとダウンロード〉と無印）。ダウンロードのみ（○）は
    # 別リスト jp_download.csv（--list download）。xone_compat は Xbox One 以降の後方互換、kinect は備考の「Kinect専用／対応」
    "x360": {
        "name": "Xbox 360",
        "dir": ROOT / "data" / "x360",
        "id_prefix": "x360-jp",
        "wikipedia": {"tables": [{
            "page": "Xbox 360のゲームタイトル一覧", "section": "発売されたタイトル", "table_id": "softwarelist",
            "columns": _X360_COLUMNS, "row_filter": lambda r: "○" not in r.get("media", ""),
            "derive": _X360_DERIVE}]},
        "extra_lists": {
            "download": {
                "out": "jp_download.csv",
                "id_suffix": "dl",
                "tables": [{"page": "Xbox 360のゲームタイトル一覧", "section": "発売されたタイトル", "table_id": "softwarelist",
                            "columns": _X360_COLUMNS, "row_filter": lambda r: "○" in r.get("media", ""),
                            "derive": _X360_DERIVE}],
            },
        },
        "extra_columns": ["download_too", "xone_compat", "kinect"],
        "madb_platforms": ["Xbox 360"],
        "madb_filter": lambda x: x["media_format"] != "ダウンロードコンテンツ",
        "mame_lists": [],
        "models_from": _xbox_models,
        "models_from_serial": lambda s: [],
        "code_of": lambda m: "",
        "normalize_code": lambda c: "",
        "dat_title_link": True,
        "nointro_dats": ["redump:Microsoft - Xbox 360"],
        "nointro_export": ["Microsoft - Xbox 360 (Redump)"],
        "nointro_export_fallback": {"Microsoft - Xbox 360 (Redump)": "redump:Microsoft - Xbox 360"},
        "dump_world": True,
        "tax_inclusive_from": "2004-04-01",
        "hash_source": "Redump",
        "media": "disc",
    },
    # Xbox。x360_compat（★: Xbox 360 で遊べる）・xone_compat（◆: Xbox One 以降）・world_collection（英語版＋日本語マニュアル）
    "xbox": {
        "name": "Xbox",
        "dir": ROOT / "data" / "xbox",
        "id_prefix": "xbox-jp",
        "wikipedia": {"tables": [{
            "page": "Xboxのゲームタイトル一覧", "section": "発売されたタイトル", "table_id": "softwarelist",
            "columns": ("jp", "na", "eu", "title", "publisher", "compat", "notes", "refs"),
            "derive": {"x360_compat": lambda r: "yes" if "★" in r.get("compat", "") else "",
                       "xone_compat": lambda r: "yes" if "◆" in r.get("compat", "") else "",
                       "world_collection": lambda r: "yes" if "ワールドコレクション" in r.get("notes", "") else ""},
        }]},
        "extra_columns": ["x360_compat", "xone_compat", "world_collection"],
        "madb_platforms": ["Xbox"],
        "mame_lists": [],
        "models_from": _xbox_models,
        "models_from_serial": lambda s: [],
        "code_of": lambda m: "",
        "normalize_code": lambda c: "",
        "dat_title_link": True,
        "nointro_dats": ["redump:Microsoft - Xbox"],
        "nointro_export": ["Microsoft - Xbox (Redump)"],
        "nointro_export_fallback": {"Microsoft - Xbox (Redump)": "redump:Microsoft - Xbox"},
        "dump_world": True,
        "tax_inclusive_from": "2004-04-01",
        "hash_source": "Redump",
        "media": "disc",
    },
    # 3DO。channel は型番から決まる流通系統（panasonic / sanyo）
    "3do": {
        "name": "3DO",
        "dir": ROOT / "data" / "3do",
        "id_prefix": "3do-jp",
        "wikipedia": {"tables": [{
            "page": "3DOのゲームタイトル一覧", "section": "発売されたタイトル", "table_id": "softwarelist",
            "columns": ("jp", "na", "eu", "title", "publisher", "notes", "refs"),
        }]},
        "extra_columns": ["channel"],
        "derive": {"channel": _3do_channel},
        "madb_platforms": ["3DO"],
        "mame_lists": ["3do"],
        "models_from": _3do_models,
        "models_from_serial": _3do_models,
        "code_of": lambda m: m or "",
        # FZ-・IMP- 以外の型番（'E3D-7023'・'NX-950101' など。overrides で Redump のシリアルどおりに入れたもの）は
        # シリアルそのままで結びつける（枚数付き 'MC-700-1' の末尾は除く）
        "normalize_code": lambda c: (_3do_models(c) or [re.sub(r"-\d$", "", (c or "").strip())])[0],
        "dat_title_models": True,
        "nointro_dats": ["redump:The 3DO Company - 3DO"],
        "nointro_export": ["3DO (Redump)"],
        "nointro_export_fallback": {"3DO (Redump)": "redump:The 3DO Company - 3DO"},
        "dump_world": True,
        "disc_subtitles": True,
        "hash_source": "Redump",
        "media": "disc",
    },
    # ワンダースワン／ワンダースワンカラー（スワンクリスタル専用ソフトは無い）。1本のリストにまとめ、compat 列で
    # ws（モノクロ）/ wsc_compatible（カラー対応）/ wsc_only（カラー専用）を区別する
    "ws": {
        "name": "ワンダースワン／ワンダースワンカラー",
        "dir": ROOT / "data" / "ws",
        "id_prefix": "ws-jp",
        "wikipedia": {"tables": [
            {"page": "ワンダースワンのゲームタイトル一覧", "section": sec, "extra": {"compat": compat}}
            for sec, compat in (("ワンダースワンのタイトル", "ws"),
                                ("ワンダースワンカラー対応のタイトル", "wsc_compatible"),
                                ("ワンダースワンカラー専用のタイトル", "wsc_only"))]},
        "extra_columns": ["compat"],
        "madb_platforms": ["ワンダースワン"],
        "mame_lists": ["wswan", "wscolor"],
        "mame_all_japanese": ["wswan", "wscolor"],   # 説明に地域が無い（アジア版は説明の '(Asia)' で除く）
        "models_from": _ws_models,
        "models_from_serial": lambda s: [],   # DAT にシリアルが無い
        "code_of": lambda m: "",
        "normalize_code": lambda c: "",
        "nointro_dats": ["Bandai - WonderSwan", "Bandai - WonderSwan Color"],
        "nointro_export": ["Bandai - WonderSwan (DB Export)", "Bandai - WonderSwan Color (DB Export)"],
        "nointro_export_fallback": {"Bandai - WonderSwan (DB Export)": "Bandai - WonderSwan",
                                    "Bandai - WonderSwan Color (DB Export)": "Bandai - WonderSwan Color"},
    },
    "wii": {
        "name": "Wii",
        "dir": ROOT / "data" / "wii",
        "id_prefix": "wii-jp",
        "wikipedia": {
            "tables": [
                {"page": "Wiiのゲームタイトル一覧", "section": "発売されたタイトル",
                 "table_id": "softwarelist", "columns": ("jp", "na", "eu", "title", "publisher", "notes")},
            ],
        },
        "extra_lists": {
            "wiiware": {
                "out": "jp_wiiware.csv",
                "id_suffix": "wiiware",
                "tables": [{"page": "Wiiウェアのゲームタイトル一覧", "section": "配信されたタイトル",
                            "columns": ("jp", "title", "publisher", "blocks", "wifi", "classic_controller", "notes")}],
            },
        },
        "madb_platforms": ["Wii"],
        "mame_lists": [],
        "nointro_dats": ["redump:Nintendo - Wii"],
        "nointro_export": ["Wii (Redump)"],
        "nointro_export_fallback": {"Wii (Redump)": "redump:Nintendo - Wii"},
        "models_from": _wii_models,
        "models_from_serial": _wii_models,
        "code_of": _wii_code,
        "normalize_code": _wii_normalize_code,
        "maru": {
            "url": "https://maru-chang.com/gamedb/gamelist.php/Wiilineup/{page}",
            "pages": 28,          # 1,372 件（バーチャルコンソール・Wiiウェア・チャンネルを含む）
            "interval": 5,
            "cache_dir": "maru-chang-wii",
            "require_model": True,
            # ディスクソフト（型番 RVL-R*** / RVL-S***）だけを型番つきで使う
            "model": lambda code: f"{code}-JPN" if re.fullmatch(r"RVL-[RS][A-Z0-9]{2}J", code) else "",
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
