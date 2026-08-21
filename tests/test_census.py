"""T-002 — census 集計(F-01)。ミニ索引フィクスチャで手計算と一致すること。"""
from pipeline.census import (
    count_distinct_color_words,
    select_candidate_works,
    summarize,
)

WORKS = [
    # (work_id, title, person_id, author, death_year, flag)
    ("001", "俳句稿", "p1", "正岡子規", 1902, "なし"),
    ("002", "墨汁一滴", "p1", "正岡子規", 1902, "なし"),
    ("003", "五百句", "p2", "高浜虚子", 1959, "なし"),
    ("004", "草木塔", "p3", "種田山頭火", 1940, "なし"),
    ("005", "現代俳句評釈", "p4", "架空 存命", 1980, "なし"),  # 没年で落ちる
    ("006", "吾輩は猫である", "p5", "夏目漱石", 1916, "なし"),  # 句集ではない
]
KEYWORDS = ["俳句", "句", "俳諧", "発句"]


def test_select_candidate_works_filters_by_keyword_and_copyright():
    got = select_candidate_works(WORKS, KEYWORDS)
    # 001(俳句稿)・003(五百句)・005 は句を含むが没年 1980 で落ちる
    assert [w[0] for w in got] == ["001", "003"]


def test_count_distinct_color_words():
    lines = [
        "白牡丹といふといへども紅ほのか",
        "赤い椿白い椿と落ちにけり",
        "をりとりてはらりとおもきすすきかな",  # 色語なし
    ]
    words = ["白", "紅", "赤", "青", "黄"]
    assert count_distinct_color_words(lines, words) == {"白", "紅", "赤"}


def test_summarize_counts():
    lines = ["白牡丹といふといへども紅ほのか", "赤い椿白い椿と落ちにけり"]
    got = summarize(WORKS, KEYWORDS, lines, ["白", "紅", "赤", "青"])
    assert got["candidate_works"] == 2      # 001, 003
    assert got["candidate_authors"] == 2    # p1, p2
    assert got["rejected_works"] == 4       # 002,004,006(語)+ 005(没年)
    assert got["lines"] == 2
    assert got["distinct_color_words"] == 3
    assert got["color_word_coverage"] == {"白": 2, "紅": 1, "赤": 1}
