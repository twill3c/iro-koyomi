"""季語表(F-06)。

**色に依存しない独立基盤**。将来 saijiki-lens として切り出せるよう、
色票・色名に関する型や定数をここに持ち込まない(N-06)。
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
