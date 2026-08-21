"""句抽出(F-02)。

青空文庫本文から句候補を保守的に抽出する。判定は**記法を落とす前の原文行**に対して行う:
詞書・前書き・署名は［＃ここから１段階小さな文字］等の範囲注記で囲まれており、
記法を先に除去するとこの手がかりが消える(loop_001 の知見)。

音数(5-7-5)では判定しない。旧仮名・字余りで正しい句を落とすため(SPEC F-02)。
表示層は原文逐語、分析層は記法除去済みの二層で保持する(Q-01)。
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from pipeline.aozora_text import strip_notation

_REGION_START = re.compile(r"［＃ここから(?P<kind>[^］]*)］")
_REGION_END = re.compile(r"［＃ここで[^］]*］")
# 字下げは句そのものに付くことがある(『おくのほそ道』)。除外するのは詞書・見出し・署名の印だけ
_INLINE_MARK = re.compile(r"［＃[^］]*(小さな文字|見出し|中央|地から|上げ)[^］]*］")
_HEADER_SEP = "-" * 20
_FOOTER = re.compile(r"^底本[：:]")
_ERA_HEAD = re.compile(r"^(明治|大正|昭和|平成|序|跋|自序|附|例言|凡例)")

# 詞書・前書きが置かれる範囲注記。この中の行は句として採らない
EXCLUDED_REGIONS = ("小さな文字",)

PUNCT = set("。、「」『』（）［］〔〕：；！？…—〜")
MIN_LEN, MAX_LEN = 8, 30


@dataclass(frozen=True)
class Haiku:
    """表示層(text)と分析層(norm)、および原文への文字オフセット。"""

    text: str
    norm: str
    line_no: int
    start: int
    end: int


def region_stack(lines: list[str]) -> list[frozenset[str]]:
    """行ごとに有効な範囲注記の集合を返す(範囲注記行そのものは終了後の状態を持つ)。"""
    stack: list[str] = []
    out: list[frozenset[str]] = []
    for line in lines:
        m = _REGION_START.search(line)
        if m:
            stack.append(m.group("kind"))
        elif _REGION_END.search(line) and stack:
            stack.pop()
        out.append(frozenset(stack))
    return out


def _body_span(lines: list[str]) -> tuple[int, int]:
    seps = [i for i, l in enumerate(lines) if l.startswith(_HEADER_SEP)]
    start = seps[1] + 1 if len(seps) >= 2 else 0
    end = next((i for i, l in enumerate(lines) if _FOOTER.match(l)), len(lines))
    return start, end


def _is_haiku_line(raw: str, regions: frozenset[str]) -> bool:
    if any(k in r for r in regions for k in EXCLUDED_REGIONS):
        return False
    if _INLINE_MARK.search(raw):
        return False
    s = strip_notation(raw).strip()
    if not (MIN_LEN <= len(s) <= MAX_LEN):
        return False
    if any(c in PUNCT for c in s):
        return False
    if "　" in s or " " in s:          # 前書きは日付と本文を全角空白で区切る
        return False
    return not _ERA_HEAD.match(s)


def extract(raw: str) -> list[Haiku]:
    lines = raw.splitlines()
    body_start, body_end = _body_span(lines)
    # 範囲注記は本文だけで数える。凡例ヘッダは注記の**用例**を含み、
    # そこで開いた領域が閉じられないまま本文全体を覆ってしまう(『牡丹句録』)
    regions = region_stack(lines[body_start:body_end])

    offsets, pos = [], 0
    for line in lines:
        offsets.append(pos)
        pos += len(line) + 1          # splitlines が落とした改行 1 文字

    out = []
    for i in range(body_start, body_end):
        line = lines[i].rstrip()
        if not _is_haiku_line(line, regions[i - body_start]):
            continue
        text = line.strip()
        start = offsets[i] + lines[i].index(text)
        out.append(
            Haiku(
                text=text,
                norm=strip_notation(text).strip(),
                line_no=i,
                start=start,
                end=start + len(text),
            )
        )
    return out
