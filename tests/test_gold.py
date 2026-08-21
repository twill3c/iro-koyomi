"""T-060 — gold 整合(F-07 / G-04 / G-06 / N-07)。

assemble は純関数。ファイル入出力なしで層の決定・件数・決定論を検査する。
"""
from pipeline.build_gold import assemble
from pipeline.lexicon import Term
from pipeline.match_b import Origin
from pipeline.saijiki.kigo import Kigo

PALETTE = [
    {"name": "白", "hex_by_source": {"en": "#FFFFFF", "ja": "#FFFFFE"}, "delta_e": 0.3,
     "readings": {"ja": "しろ"}, "provenance": "記載なし", "notes": {}},
    {"name": "山吹色", "hex_by_source": {"ja": "#F8B500"}, "delta_e": None,
     "readings": {"ja": "やまぶきいろ"}, "provenance": "記載なし", "notes": {}},
    {"name": "今様色", "hex_by_source": {"ja": "#D0576B"}, "delta_e": None,
     "readings": {"ja": "いまよういろ"}, "provenance": "記載なし", "notes": {}},
]
CORPUS = [
    {"author": "高浜虚子", "work": "五百句", "work_id": "051837", "card_url": "https://example/card",
     "text": "白牡丹《はくぼたん》といふといへども紅ほのか", "norm": "白牡丹といふといへども紅ほのか",
     "start": 0, "end": 22, "base_text": "虚子五句集（上）", "publisher": "岩波文庫",
     "typist": "入力者", "proofreader": "校正者"},
    {"author": "正岡子規", "work": "寒山落木　巻一", "work_id": "001896", "card_url": "https://example/card2",
     "text": "山吹や葉に花に葉に花に葉に", "norm": "山吹や葉に花に葉に花に葉に",
     "start": 0, "end": 13, "base_text": "子規全集", "publisher": "講談社",
     "typist": "入力者", "proofreader": "校正者"},
]
LEXICON = [Term(term="白", kind="basic", color_name="白", sense_width=False)]
ORIGINS = [Origin(color_name="山吹色", origin="山吹", kigo="山吹", certainty="established")]
KIGO = [Kigo(name="山吹", reading="やまぶき", season="春", phase="晩")]


def _build():
    return assemble(PALETTE, CORPUS, LEXICON, [], ORIGINS, KIGO)


def test_t060_layers_are_assigned_by_evidence():
    index, details = _build()
    layers = {c["name"]: c["layer"] for c in index["colors"]}
    assert layers == {"白": "A", "山吹色": "B", "今様色": "C"}


def test_t060b_counts_match_details():
    index, details = _build()
    for color in index["colors"]:
        detail = details[color["id"]]
        assert color["a_count"] == len(detail["layer_a"])
        assert color["b_count"] == len(detail["layer_b"])


def test_t060c_empty_color_is_normal():
    """C の色も必ず出力され、句 0 件で正常に扱える(埋めない)。"""
    index, details = _build()
    empty = next(c for c in index["colors"] if c["name"] == "今様色")
    assert (empty["a_count"], empty["b_count"]) == (0, 0)
    assert details[empty["id"]]["layer_a"] == [] and details[empty["id"]]["layer_b"] == []


def test_t060d_source_attribution_on_every_haiku():
    """N-07: 句には底本と図書カードが必ず付く。"""
    _, details = _build()
    for detail in details.values():
        for h in detail["layer_a"] + detail["layer_b"]:
            assert h["base_text"] and h["card_url"] and h["author"] and h["work"]


def test_t060e_b_layer_is_not_a_color_mention():
    _, details = _build()
    yamabuki = next(d for d in details.values() if d["name"] == "山吹色")
    assert yamabuki["layer_b"][0]["is_color_mention"] is False
    assert yamabuki["layer_b"][0]["kigo"] == "山吹"
    assert yamabuki["season"] == "春" and yamabuki["phase"] == "晩"


def test_t060f_deterministic():
    assert _build() == _build()


def test_t060g_fill_rate_is_reported():
    index, _ = _build()
    assert index["fill"] == {"A": 1, "B": 1, "C": 1, "total": 3}


def test_t060h_ids_are_unique_and_stable():
    index, _ = _build()
    ids = [c["id"] for c in index["colors"]]
    assert len(ids) == len(set(ids))
    assert ids == sorted(ids)          # 名前順の連番 — 再生成で並びが揺れない
