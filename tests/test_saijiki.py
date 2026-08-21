"""T-050/T-051 — 季語表と歳時記順(F-06 / N-06)。

季語データは色に依存しない独立の基盤として持つ(将来 saijiki-lens へ切り出す)。
"""
import pathlib

import pytest

from pipeline.saijiki.kigo import Kigo, calendar_order, load_kigo, parse_kigo_row

ROWS = [
    ["桜", "さくら", "春", "晩", ""],
    ["卯の花", "うのはな", "夏", "初", ""],
    ["月", "つき", "秋", "三", "月そのものが秋の季語"],
    ["朽葉", "くちば", "冬", "三", ""],
    ["若菜", "わかな", "新年", "三", "七草"],
]


def test_t050_parse_and_order():
    kigo = [parse_kigo_row(r) for r in ROWS]
    # 新年 → 春 → 夏 → 秋 → 冬、同季内は 三(通季)→初→仲→晩
    assert [k.name for k in sorted(kigo, key=calendar_order)] == [
        "若菜",
        "桜",
        "卯の花",
        "月",
        "朽葉",
    ]


def test_t050b_unknown_season_is_rejected():
    with pytest.raises(ValueError):
        parse_kigo_row(["架空", "かくう", "梅雨", "初", ""])


def test_t050c_unknown_phase_is_rejected():
    with pytest.raises(ValueError):
        parse_kigo_row(["架空", "かくう", "春", "序", ""])


def test_t050d_real_table_loads_and_is_unique():
    table = load_kigo()
    assert len(table) >= 40
    names = [k.name for k in table]
    assert len(names) == len(set(names)), "季語の重複"
    assert all(isinstance(k, Kigo) for k in table)


def test_t051_saijiki_is_isolated_from_color():
    """N-06: 季語基盤は色モジュールに依存しない(切り出し可能性の維持)。"""
    root = pathlib.Path("pipeline/saijiki")
    for path in root.rglob("*.py"):
        src = path.read_text(encoding="utf-8")
        assert "pipeline.color" not in src, f"{path} が色モジュールを参照している"
        assert "palette" not in src, f"{path} が色票を参照している"


def test_t050e_origins_reference_integrity():
    """由来表の色名は色票に、季語は季語表に必ず存在すること(F-06)。"""
    import json

    from pipeline.match_b import load_origins

    palette = {c["name"] for c in json.loads(
        pathlib.Path("data/colors/palette.json").read_text(encoding="utf-8"))["colors"]}
    kigo = {k.name for k in load_kigo()}
    for o in load_origins():
        assert o.color_name in palette, f"色票に無い色名: {o.color_name}"
        assert o.kigo in kigo, f"季語表に無い季語: {o.kigo}"


def test_t050f_certainty_is_required():
    """certainty 未設定の行は読み込みで拒否されること。"""
    import pytest as _pytest

    from pipeline.match_b import load_origins

    tmp = pathlib.Path("tests/fixtures/bad_origins.tsv")
    tmp.write_text("架空色\t架空\t桜\t\t\n", encoding="utf-8")
    try:
        with _pytest.raises(ValueError):
            load_origins(tmp)
    finally:
        tmp.unlink()
