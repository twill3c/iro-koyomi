"""季語表(F-06)。

**色に依存しない独立基盤**。色票・色名に関する型や定数をここに持ち込まない(N-06)。

2026-08-23: saijiki-lens が独立プロジェクトとして着工した。ただし本表を移管はしない。
両者は目的が違うためである — こちらは**色名の由来語**(若菜・紅梅・山吹・苅安・朽葉)を
集めた 53 語、あちらは**七十二候が名指す事物**(露・菊・蝶・紅葉・時雨)を集めた 70 語で、
重なりは小さい。同じものの二重管理ではないので、それぞれが自分の表を持つ。
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

KIGO_TSV = Path("data/curated/saijiki/kigo.tsv")

# 歳時記の並び。新年を年頭に置き、季内は通季(三)を先頭にする
SEASONS = {"新年": 0, "春": 1, "夏": 2, "秋": 3, "冬": 4}
PHASES = {"三": 0, "初": 1, "仲": 2, "晩": 3}


@dataclass(frozen=True)
class Kigo:
    name: str
    reading: str
    season: str
    phase: str
    note: str = ""


def parse_kigo_row(row: list[str]) -> Kigo:
    name, reading, season, phase = (c.strip() for c in row[:4])
    note = row[4].strip() if len(row) > 4 else ""
    if season not in SEASONS:
        raise ValueError(f"未知の季節: {season!r}({name})")
    if phase not in PHASES:
        raise ValueError(f"未知の時候: {phase!r}({name})")
    return Kigo(name=name, reading=reading, season=season, phase=phase, note=note)


def calendar_order(kigo: Kigo) -> tuple[int, int, str]:
    return (SEASONS[kigo.season], PHASES[kigo.phase], kigo.reading)


def load_kigo(path: Path = KIGO_TSV) -> list[Kigo]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            rows.append(parse_kigo_row(line.split("\t")))
    return rows
