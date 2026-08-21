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
