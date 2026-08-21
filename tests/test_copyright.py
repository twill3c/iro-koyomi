"""T-001 — 著作権ゲート(F-01 / G-05)。

期待値は SPEC の基準「1967 年末までに没した作者に限る」から直接取る。
没年不明は不採録(判断を保留せず落とす)。
"""
import pytest

from pipeline.copyright import DEATH_YEAR_CUTOFF, is_public_domain, parse_death_year


def test_cutoff_year_is_1967():
    # 50 年で満了済みの層。70 年化は遡及しない
    assert DEATH_YEAR_CUTOFF == 1967


@pytest.mark.parametrize(
    "death_year,flag,expected",
    [
        (1902, "なし", True),   # 子規: 十分に古い
        (1967, "なし", True),   # 境界: 1967 年末に満了済み → 採録
        (1968, "なし", False),  # 境界: 1968 年没は 70 年保護 → 不採録
        (1959, "なし", True),   # 虚子
        (None, "なし", False),  # 没年不明は不採録
        (1902, "あり", False),  # 青空側が保護ありとする場合は採録しない(訳者権等)
    ],
)
def test_is_public_domain(death_year, flag, expected):
    assert is_public_domain(death_year, flag) is expected


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("1902-09-19", 1902),
        ("1967-12-31", 1967),
        ("1867", 1867),
        ("", None),
        ("不詳", None),
    ],
)
def test_parse_death_year(raw, expected):
    assert parse_death_year(raw) == expected
