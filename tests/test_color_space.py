"""T-020〜T-022 — 色空間と色差(F-03 / G-01)。

期待値は**公開既知参照値**から取る。実装からの転記は禁止(TEST_SPEC 実行規約)。
- sRGB→Lab: sRGB(IEC 61966-2-1)の定義と D65 白色点から導かれる周知の値
- ΔE2000: Sharma, Wu, Dalal (2005) の検証データ 34 対(tests/fixtures/ciede2000_sharma.tsv)
"""
import pathlib

import pytest

from pipeline.color.space import ciede2000, hex_to_rgb, srgb_to_lab

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "ciede2000_sharma.tsv"


def _sharma_pairs():
    rows = []
    for line in FIXTURE.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        rows.append([float(x) for x in line.split("\t")])
    return rows


def test_t020_hex_to_rgb():
    assert hex_to_rgb("#F08F90") == (240, 143, 144)
    assert hex_to_rgb("f08f90") == (240, 143, 144)
    with pytest.raises(ValueError):
        hex_to_rgb("#12345")


@pytest.mark.parametrize(
    "rgb,expected",
    [
        ((255, 255, 255), (100.0, 0.0, 0.0)),      # D65 白色点 → L*=100, a*=b*=0
        ((0, 0, 0), (0.0, 0.0, 0.0)),
        ((255, 0, 0), (53.2408, 80.0925, 67.2032)),
        ((0, 255, 0), (87.7347, -86.1827, 83.1793)),
        ((0, 0, 255), (32.2970, 79.1875, -107.8602)),
    ],
)
def test_t020b_srgb_to_lab(rgb, expected):
    got = srgb_to_lab(rgb)
    for g, e in zip(got, expected):
        assert abs(g - e) < 1e-3, f"{got} != {expected}"


def test_t020c_gamma_boundary_is_continuous():
    """sRGB の伝達関数は 0.04045 で線形部と冪部が連続であること。"""
    below = srgb_to_lab((10, 10, 10))[0]   # 10/255 = 0.0392 < 0.04045(線形部)
    above = srgb_to_lab((11, 11, 11))[0]   # 11/255 = 0.0431 > 0.04045(冪部)
    assert below < above
    assert abs(above - below) < 1.0        # 境界で跳ねない


@pytest.mark.parametrize("row", _sharma_pairs())
def test_t021_ciede2000_reference(row):
    l1, a1, b1, l2, a2, b2, expected = row
    got = ciede2000((l1, a1, b1), (l2, a2, b2))
    assert abs(got - expected) < 1e-4, f"{got} != {expected}"


def test_t021b_identity_and_symmetry():
    a, b = (52.1, 12.3, -4.5), (48.0, -3.2, 9.9)
    assert ciede2000(a, a) == pytest.approx(0.0, abs=1e-12)
    assert ciede2000(a, b) == pytest.approx(ciede2000(b, a), abs=1e-12)


def test_t021c_sharma_fixture_is_complete():
    """検証データが 34 対そろっていること(部分適用で緑になるのを防ぐ)。"""
    assert len(_sharma_pairs()) == 34
