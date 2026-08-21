"""T-010〜T-013 — 句抽出(F-02 / Q-01 / G-04 / G-08)。

期待値は青空文庫の記法仕様と SPEC の規則から取る。
"""
import pathlib

import pytest

from pipeline.extract_haiku import extract, region_stack
from pipeline.aozora_text import strip_notation

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "mini_aozora.txt"
RAW = FIXTURE.read_text(encoding="utf-8")


def test_t010_strip_notation():
    """ルビ・ルビ開始記号・注記が分析層から落ちること。"""
    assert strip_notation("白牡丹《はくぼたん》といふ") == "白牡丹といふ"
    assert strip_notation("｜牡丹《ぼたん》の花") == "牡丹の花"
    assert strip_notation("［＃５字下げ］序") == "序"


def test_t010b_region_stack_tracks_ranges():
    """［＃ここから…］/［＃ここで…］の範囲注記が状態として追えること。"""
    lines = [
        "句一",
        "［＃ここから１段階小さな文字］",
        "詞書",
        "［＃ここで小さな文字終わり］",
        "句二",
    ]
    stacks = region_stack(lines)
    assert stacks[0] == frozenset()
    assert "小さな文字" in next(iter(stacks[2]))
    assert stacks[4] == frozenset()


def test_t011_conservative_extraction():
    """地の文・見出し・詞書(小さな文字領域)が落ち、字余り句は残ること。"""
    got = [h.text for h in extract(RAW)]
    assert got == [
        "白牡丹《はくぼたん》といふといへども紅《べに》ほのか",
        "飛騨の生れ名はとうといふほととぎす",   # 17 音を超える字余り — 音数では落とさない
        "をりとりてはらりとおもきすすきかな",
    ]
    assert "友の訃に接して悼む" not in got      # 小さな文字領域の詞書
    assert "これは序文である。地の文であるから句として採ってはならない。" not in got


def test_t011b_normalized_layer():
    """分析層はルビを落とした逐語テキストであること。"""
    assert extract(RAW)[0].norm == "白牡丹といふといへども紅ほのか"


def test_t012_offsets_round_trip():
    """表示層は原文の [start,end) と文字単位で一致すること(G-04)。"""
    for h in extract(RAW):
        assert RAW[h.start : h.end] == h.text


# --- G-08 題名オラクル(bronze 取得済みのときのみ) -------------------------
KYOSHI = {
    "051837": ("五百句", 500, True),    # 序に「五百句を選んだ」— 厳密一致
    "051838": ("五百五十句", 550, False),
    "051840": ("六百句", 600, False),   # 序:「厳格に六百句と限ったわけではなく多少超過」
    "051841": ("六百五十句", 650, False),
    "051839": ("七百五十句", 750, False),
}


@pytest.mark.parametrize("wid,spec", KYOSHI.items())
def test_t013_title_oracle(wid, spec):
    title, expected, strict = spec
    path = pathlib.Path("data/bronze") / f"{wid}.txt"
    if not path.exists():
        pytest.skip(f"bronze 未取得: {title}")
    n = len(extract(path.read_text(encoding="utf-8")))
    if strict:
        assert n == expected, f"{title}: {n} 句(題名は {expected} 句)"
    else:
        # 著者自身が「多少超過」と記す。下限は題名値、上限は +10%
        assert expected <= n <= int(expected * 1.10), f"{title}: {n} 句"
