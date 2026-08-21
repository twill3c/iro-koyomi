"""著作権ゲート(F-01 / G-05)。

日本の保護期間は 2018 年の 70 年化が**遡及しない**ため、50 年で満了済みの層
(= 1967 年末までに没した作者)のみが確実に PD である。没年不明は不採録とする
(判断を保留した候補を採録に含めない)。
"""
from __future__ import annotations

import re

DEATH_YEAR_CUTOFF = 1967

_YEAR_RE = re.compile(r"^(\d{4})")


def parse_death_year(raw: str | None) -> int | None:
    """青空文庫索引の没年月日表記(``1902-09-19`` / ``1867`` / 空)から西暦年を取る。"""
    if not raw:
        return None
    m = _YEAR_RE.match(raw.strip())
    return int(m.group(1)) if m else None


def is_public_domain(death_year: int | None, copyright_flag: str) -> bool:
    """没年と青空文庫の著作権フラグの**両方**が通ったものだけを PD とみなす。"""
    if death_year is None:
        return False
    if copyright_flag.strip() != "なし":
        return False
    return death_year <= DEATH_YEAR_CUTOFF
