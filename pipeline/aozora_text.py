"""青空文庫テキストの取得と記法除去。

表示層(原文逐語)と分析層(記法除去済み)の二層原則(Q-01)に従い、
除去は**分析層のみ**に適用する。原文は bronze に無改変で残す。
"""
from __future__ import annotations

import io
import re
import time
import urllib.request
import zipfile
from pathlib import Path

BRONZE = Path("data/bronze")
MIN_INTERVAL_SEC = 0.8  # N-02: 青空文庫への連続アクセス間隔

_RUBY = re.compile(r"《[^》]*》")
_RUBY_MARK = re.compile(r"[｜|]")
_NOTE = re.compile(r"［＃[^］]*］")
_ACCENT = re.compile(r"〔[^〕]*〕")


def strip_notation(text: str) -> str:
    """ルビ・傍点等の注記記法を落とす(分析層用)。"""
    text = _RUBY.sub("", text)
    text = _NOTE.sub("", text)
    text = _RUBY_MARK.sub("", text)
    return text


def fetch_text(url: str, work_id: str, *, sleep: float = MIN_INTERVAL_SEC) -> str:
    """テキスト zip を取得して bronze に保存し、本文を返す(既取得なら再取得しない)。"""
    dest = BRONZE / f"{work_id}.txt"
    if dest.exists():
        return dest.read_text(encoding="utf-8")
    time.sleep(sleep)
    with urllib.request.urlopen(url, timeout=60) as r:
        blob = r.read()
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        name = next(n for n in z.namelist() if n.lower().endswith(".txt"))
        raw = z.read(name).decode("cp932", errors="replace")
    BRONZE.mkdir(parents=True, exist_ok=True)
    dest.write_text(raw, encoding="utf-8")
    return raw


_SEP = "-" * 20
_FOOT = re.compile(r"^底本[：:]")
_PREFACE_HEAD = re.compile(r"^(明治|大正|昭和|序|跋|附|自序)")
_PUNCT = set("。、「」『』（）［］〔〕：；！？…—")


def body_lines(raw: str) -> list[str]:
    """凡例ヘッダと底本フッタを落とし、分析層の行列を返す。"""
    lines = [l.rstrip() for l in strip_notation(raw).splitlines()]
    # ヘッダ: 罫線で囲まれた凡例ブロックの終端まで
    seps = [i for i, l in enumerate(lines) if l.startswith(_SEP)]
    start = seps[1] + 1 if len(seps) >= 2 else 0
    # フッタ: 「底本：」以降
    end = next((i for i, l in enumerate(lines) if _FOOT.match(l)), len(lines))
    return [l for l in lines[start:end]]


def haiku_candidates(raw: str, *, min_len: int = 8, max_len: int = 25) -> list[str]:
    """句候補の保守的抽出(census 用の下限見積り)。

    音数(5-7-5)では判定しない(旧仮名・字余りで落ちるため。F-02)。
    句読点・全角空白(前書きの区切り)・年号始まりの行を落とすだけの規則で、
    **取りこぼす方向に倒す**。
    """
    out = []
    for line in body_lines(raw):
        s = line.strip().replace("　", " ")
        if not (min_len <= len(s) <= max_len):
            continue
        if any(c in _PUNCT for c in s):
            continue
        if " " in s or _PREFACE_HEAD.match(s):
            continue
        out.append(s)
    return out
