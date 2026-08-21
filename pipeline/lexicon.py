"""色語辞書と A 層照合(F-05 / F-04)。

A 層の条件は「句に**色語そのもの**が現れる」こと。次の二種のみを色語とする。

- ``basic``: 単独で色を指す基本色語(白・黒・赤・青…)。curated
- ``name``: 色票の色名と完全一致する語(浅葱色・山吹色…)

語源語(山吹・桃・柿)は色への言及ではないので A 層では検出しない(B 層で扱う)。
色を意味しない複合語(紅葉・白粉・紫陽花…)は照合前にマスクする。
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

LEXICON_TSV = Path("data/curated/color_lexicon.tsv")
EXCLUSIONS_TSV = Path("data/curated/color_exclusions.tsv")


@dataclass(frozen=True)
class Term:
    term: str
    kind: str            # basic | name
    color_name: str      # 色票の色名(basic は語そのもの)
    sense_width: bool    # 現代の HEX と語義がずれる語(青=緑を含む 等)


@dataclass(frozen=True)
class Hit:
    term: str
    color_name: str
    start: int
    end: int
    sense_width: bool

    @property
    def connectable(self) -> bool:
        """色票 HEX と結んでよいか。語義幅のある語は結ばない(F-05)。"""
        return not self.sense_width


def _rows(path: Path) -> list[list[str]]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            out.append(line.split("\t"))
    return out


def load_lexicon(path: Path = LEXICON_TSV) -> list[Term]:
    return [
        Term(term=r[0], kind=r[1], color_name=r[2], sense_width=r[3].strip() == "yes")
        for r in _rows(path)
    ]


def load_exclusions(path: Path = EXCLUSIONS_TSV) -> list[str]:
    return [r[0] for r in _rows(path)]


def _masked_spans(text: str, exclusions: list[str]) -> list[tuple[int, int]]:
    spans = []
    for word in exclusions:
        start = text.find(word)
        while start != -1:
            spans.append((start, start + len(word)))
            start = text.find(word, start + 1)
    return spans


def find_color_words(text: str, lexicon: list[Term], exclusions: list[str]) -> list[Hit]:
    """左から最長一致で走査する。マスク領域に重なる一致は採らない。"""
    if not text:
        return []
    masked = _masked_spans(text, exclusions)
    by_len = sorted(lexicon, key=lambda t: -len(t.term))

    hits, i = [], 0
    while i < len(text):
        for term in by_len:
            end = i + len(term.term)
            if text[i:end] != term.term:
                continue
            if any(s < end and i < e for s, e in masked):
                continue
            hits.append(
                Hit(
                    term=term.term,
                    color_name=term.color_name,
                    start=i,
                    end=end,
                    sense_width=term.sense_width,
                )
            )
            i = end - 1
            break
        i += 1
    return hits


# 色名でありながら、句の中では植物・動物そのものを指す語。A 層に入れない(B 層で扱う)
PLANT_NOUNS = {"牡丹", "杜若", "女郎花", "梔子", "苅萱", "蒲萄"}


def build_lexicon(palette_path: Path = Path("data/colors/palette.json")) -> list[Term]:
    """curated の基本色語に、色票の色名を name 語として加える。"""
    import json

    terms = {t.term: t for t in load_lexicon()}
    data = json.loads(palette_path.read_text(encoding="utf-8"))
    for color in data["colors"]:
        name = color["name"]
        if name in terms or name in PLANT_NOUNS:
            continue
        terms[name] = Term(term=name, kind="name", color_name=name, sense_width=False)
    return list(terms.values())
