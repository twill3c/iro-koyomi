"""色空間変換と色差(F-03 / G-01)。

sRGB は IEC 61966-2-1、白色点は D65。ΔE2000 は CIE 15:2004 / Sharma, Wu, Dalal (2005)。
期待値はテスト側が公開参照値を持つ(実装から転記しない)。
"""
from __future__ import annotations

import math

# D65 白色点(CIE 1931 2°観測者)
WHITE_D65 = (95.047, 100.000, 108.883)

# sRGB(D65)→ XYZ 行列(IEC 61966-2-1)
_M = (
    (0.4124564, 0.3575761, 0.1804375),
    (0.2126729, 0.7151522, 0.0721750),
    (0.0193339, 0.1191920, 0.9503041),
)

_EPS = 216 / 24389   # (6/29)^3
_KAPPA = 24389 / 27  # (29/3)^3


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    s = value.strip().lstrip("#")
    if len(s) != 6 or any(c not in "0123456789abcdefABCDEF" for c in s):
        raise ValueError(f"6 桁の 16 進表記ではない: {value!r}")
    return tuple(int(s[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _linearize(channel: float) -> float:
    """sRGB の伝達関数の逆(ガンマ展開)。"""
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def _f(t: float) -> float:
    return t ** (1 / 3) if t > _EPS else (_KAPPA * t + 16) / 116


def srgb_to_lab(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    r, g, b = (_linearize(c / 255) for c in rgb)
    xyz = [sum(m * v for m, v in zip(row, (r, g, b))) * 100 for row in _M]
    fx, fy, fz = (_f(c / w) for c, w in zip(xyz, WHITE_D65))
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def hex_to_lab(value: str) -> tuple[float, float, float]:
    return srgb_to_lab(hex_to_rgb(value))


def ciede2000(
    lab1: tuple[float, float, float],
    lab2: tuple[float, float, float],
    *,
    k_l: float = 1.0,
    k_c: float = 1.0,
    k_h: float = 1.0,
) -> float:
    l1, a1, b1 = lab1
    l2, a2, b2 = lab2

    c1 = math.hypot(a1, b1)
    c2 = math.hypot(a2, b2)
    c_bar = (c1 + c2) / 2
    g = 0.5 * (1 - math.sqrt(c_bar**7 / (c_bar**7 + 25**7)))

    a1p, a2p = (1 + g) * a1, (1 + g) * a2
    c1p, c2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360 if (b1 or a1p) else 0.0
    h2p = math.degrees(math.atan2(b2, a2p)) % 360 if (b2 or a2p) else 0.0

    dlp = l2 - l1
    dcp = c2p - c1p
    if c1p * c2p == 0:
        dhp = 0.0
    elif abs(h2p - h1p) <= 180:
        dhp = h2p - h1p
    else:
        dhp = h2p - h1p - 360 if h2p > h1p else h2p - h1p + 360
    dhp_term = 2 * math.sqrt(c1p * c2p) * math.sin(math.radians(dhp) / 2)

    lp_bar = (l1 + l2) / 2
    cp_bar = (c1p + c2p) / 2
    if c1p * c2p == 0:
        hp_bar = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hp_bar = (h1p + h2p) / 2
    elif h1p + h2p < 360:
        hp_bar = (h1p + h2p + 360) / 2
    else:
        hp_bar = (h1p + h2p - 360) / 2

    t = (
        1
        - 0.17 * math.cos(math.radians(hp_bar - 30))
        + 0.24 * math.cos(math.radians(2 * hp_bar))
        + 0.32 * math.cos(math.radians(3 * hp_bar + 6))
        - 0.20 * math.cos(math.radians(4 * hp_bar - 63))
    )
    s_l = 1 + (0.015 * (lp_bar - 50) ** 2) / math.sqrt(20 + (lp_bar - 50) ** 2)
    s_c = 1 + 0.045 * cp_bar
    s_h = 1 + 0.015 * cp_bar * t
    r_t = (
        -2
        * math.sqrt(cp_bar**7 / (cp_bar**7 + 25**7))
        * math.sin(math.radians(60 * math.exp(-(((hp_bar - 275) / 25) ** 2))))
    )

    term_l = dlp / (k_l * s_l)
    term_c = dcp / (k_c * s_c)
    term_h = dhp_term / (k_h * s_h)
    return math.sqrt(term_l**2 + term_c**2 + term_h**2 + r_t * term_c * term_h)
