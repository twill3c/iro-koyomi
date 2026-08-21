"""T-052 — B 層照合(F-04 / F-06)。

B 層は「色名の由来語が句に現れる」ことであって、**色への言及ではない**。
ラベルを崩さないことをテストで固定する。
"""
from pipeline.match_b import Origin, find_origin_words

ORIGINS = [
    Origin(color_name="山吹色", origin="山吹", kigo="山吹", certainty="established"),
    Origin(color_name="鴇色", origin="鴇", kigo="鴇", certainty="established"),
    Origin(color_name="桜色", origin="桜", kigo="桜", certainty="established"),
]


def test_t052_origin_hit_is_not_a_color_mention():
    hits = find_origin_words("山吹や葉に花に葉に花に葉に", ORIGINS)
    assert len(hits) == 1
    assert hits[0].color_name == "山吹色"
    assert hits[0].layer == "B"
    assert hits[0].is_color_mention is False   # ここを true にしてはならない


def test_t052b_no_origin_yields_nothing():
    assert find_origin_words("をりとりてはらりとおもきすすきかな", ORIGINS) == []


def test_t052c_offsets():
    hits = find_origin_words("しづかさや桜散りけり", ORIGINS)
    assert (hits[0].start, hits[0].end) == (5, 6)
