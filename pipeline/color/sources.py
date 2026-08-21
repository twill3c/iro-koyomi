"""色票出典の取り込みと出典間差分(F-03 / N-05)。

採用出典は人間承認済みの 2 系統(docs/color_sources_candidates.md):
- en.wikipedia "Traditional colors of Japan"(CC BY-SA 4.0)
- ja.wikipedia「日本の色の一覧」(CC BY-SA 4.0)

**どちらも HEX の典拠を書いていない**。この事実は provenance="記載なし" として保持し、
UI で隠さずに示す(「色名は言葉であって数値ではない」)。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from pipeline.color.space import ciede2000, hex_to_lab

PROVENANCE_UNSTATED = "記載なし"

_LANG = re.compile(r"\{\{lang\|ja\|([^}]*)\}\}")
_TRANSLIT = re.compile(r"\{\{translit\|ja\|([^}]*)\}\}")
_HEX = re.compile(r"#([0-9a-fA-F]{6})")
_LINK = re.compile(r"\[\[(?:[^\]|]*\|)?([^\]|]*)\]\]")
_TAG = re.compile(r"<[^>]*>")


@dataclass(frozen=True)
class ColorEntry:
    name: str
    reading: str
    hex: str
    note: str = ""


@dataclass
class PaletteColor:
    name: str
    hex_by_source: dict[str, str]
    readings: dict[str, str] = field(default_factory=dict)
    notes: dict[str, str] = field(default_factory=dict)
    delta_e: float | None = None
    provenance: str = PROVENANCE_UNSTATED


def _norm_hex(raw: str) -> str:
    return "#" + raw.upper()


def parse_en_wikitext(text: str) -> list[ColorEntry]:
    """en 版は 1 行に色 2 件、各件が名前・ローマ字・英訳・RGB・HEX の 5 セル。"""
    out = []
    cells = [c.strip() for c in text.split("\n|") ]
    pending: list[str] = []
    for cell in cells:
        m = _LANG.search(cell)
        if m:
            pending = [m.group(1).strip()]
            continue
        if not pending:
            continue
        if len(pending) == 1 and _TRANSLIT.search(cell):
            pending.append(_TRANSLIT.search(cell).group(1).strip())
            continue
        if len(pending) == 2:
            pending.append(_LINK.sub(r"\1", cell).strip())
            continue
        if len(pending) == 3 and _HEX.search(cell):
            out.append(
                ColorEntry(
                    name=pending[0],
                    reading=pending[1],
                    hex=_norm_hex(_HEX.search(cell).group(1)),
                    note=pending[2],
                )
            )
            pending = []
    return out


def parse_ja_wikitext(text: str) -> list[ColorEntry]:
    """ja 版は 1 行 1 色。セルは「色見本+HEX」「よみ<br/>色名」「備考」。"""
    out = []
    for line in text.splitlines():
        if not line.startswith("|bgcolor"):
            continue
        cells = line.split("||")
        if len(cells) < 2:
            continue
        m = _HEX.search(cells[0])
        if not m:
            continue
        name_cell = _TAG.sub("\n", cells[1]).strip()
        parts = [p.strip() for p in name_cell.split("\n") if p.strip()]
        reading = parts[0] if parts else ""
        name = _LINK.sub(r"\1", parts[-1]).strip() if parts else ""
        note = _LINK.sub(r"\1", _TAG.sub("", cells[2])).strip() if len(cells) > 2 else ""
        if name:
            out.append(ColorEntry(name=name, reading=reading, hex=_norm_hex(m.group(1)), note=note))
    return out


def build_palette(by_source: dict[str, list[ColorEntry]]) -> list[PaletteColor]:
    """色名で突き合わせ、2 出典に値があるものだけ ΔE2000 を計算する。

    片方にしか無い色の delta_e は **None**(「差が無い」= 0.0 と混同しない)。
    """
    merged: dict[str, PaletteColor] = {}
    for source, entries in by_source.items():
        for e in entries:
            p = merged.setdefault(e.name, PaletteColor(name=e.name, hex_by_source={}))
            p.hex_by_source.setdefault(source, e.hex)
            p.readings.setdefault(source, e.reading)
            if e.note:
                p.notes.setdefault(source, e.note)

    for p in merged.values():
        hexes = list(p.hex_by_source.values())
        if len(hexes) >= 2:
            p.delta_e = ciede2000(hex_to_lab(hexes[0]), hex_to_lab(hexes[1]))
    return list(merged.values())
