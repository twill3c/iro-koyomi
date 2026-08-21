"""T-040/T-041 — 色語辞書と A 層照合(F-05 / F-04 / G-03)。

A 層は「句に色語そのものが現れる」ことだけを事実として扱う。
語源語(山吹・桃・柿)は A ではなく B 層であり、ここでは検出しない。
"""
import pytest

from pipeline.lexicon import Term, find_color_words

LEX = [
    Term(term="白", kind="basic", color_name="白", sense_width=False),
    Term(term="紅", kind="basic", color_name="紅", sense_width=False),
    Term(term="青", kind="basic", color_name="青", sense_width=True),   # 古語の青は緑を含む
    Term(term="浅葱色", kind="name", color_name="浅葱色", sense_width=False),
    Term(term="山吹色", kind="name", color_name="山吹色", sense_width=False),
]
EXCL = ["紅葉", "白粉", "紫陽花"]


def test_t040_direct_color_words_with_offsets():
    """虚子の一句から白と紅を拾い、位置が正しいこと。"""
    text = "白牡丹といふといへども紅ほのか"
    hits = find_color_words(text, LEX, EXCL)
    assert [(h.term, h.start, h.end) for h in hits] == [("白", 0, 1), ("紅", 11, 12)]


def test_t040b_stem_alone_is_not_a_layer():
    """語源語(山吹)だけでは A 層にしない。B 層で扱う。"""
    assert find_color_words("山吹や葉に花に葉に花に葉に", LEX, EXCL) == []
    hits = find_color_words("山吹色の扇ひらけり", LEX, EXCL)
    assert [h.term for h in hits] == ["山吹色"]


def test_t040c_excluded_compounds_are_masked():
    """紅葉(もみじ)は植物の名であって色の言及ではない。"""
    assert find_color_words("紅葉して山静かなり", LEX, EXCL) == []
    # 同じ句に生きた色語があればそちらは残る
    hits = find_color_words("紅葉ちる白き庭かな", LEX, EXCL)
    assert [h.term for h in hits] == ["白"]


def test_t040d_longest_match_wins():
    """浅葱色は「浅葱」+「色」ではなく 1 語として拾う。"""
    lex = LEX + [Term(term="浅葱", kind="name", color_name="浅葱色", sense_width=False)]
    hits = find_color_words("浅葱色の空", lex, EXCL)
    assert [(h.term, h.start, h.end) for h in hits] == [("浅葱色", 0, 3)]


def test_t041_sense_width_flag():
    """青は緑を含むため、色票 HEX と接続しない。"""
    hits = find_color_words("青葉して御目の雫拭はばや", LEX, EXCL)
    assert len(hits) == 1
    assert hits[0].term == "青"
    assert hits[0].sense_width is True
    assert hits[0].connectable is False       # HEX と結ばない
    white = find_color_words("白露や", LEX, EXCL)[0]
    assert white.sense_width is False and white.connectable is True


def test_t041b_repeated_word_yields_multiple_hits():
    hits = find_color_words("白妙の白き衣", LEX, EXCL)
    # 白(0)妙(1)の(2)白(3)き(4)衣(5)
    assert [h.start for h in hits] == [0, 3]


@pytest.mark.parametrize("bad", ["", "　", "・"])
def test_t040e_empty_input_is_normal(bad):
    assert find_color_words(bad, LEX, EXCL) == []
