"""T-022 — 出典パーサと出典間差分(F-03 / N-05)。

Wikipedia の表記から色名と HEX を取り出す。両出典とも **HEX の典拠を書いていない**ため、
provenance は "記載なし" として保持する(隠さず表示するのが本アプリの主張)。
"""
from pipeline.color.sources import ColorEntry, build_palette, parse_en_wikitext, parse_ja_wikitext

EN = """
{| class="wikitable"
|-
!Name
!Romanized
!English translation
![[RGB]]
![[Hex triplet]]
|-
|{{lang|ja|一斤染}}
|{{translit|ja|Ikkonzome}}
|One kin dye
|240,143,144
|style="background:#F08F90; color:#ffffff;"|#F08F90
|{{lang|ja|桃色}}
|{{translit|ja|Momo-iro}}
|Peach-colored
|244,121,131
|style="background:#F47983;"|#F47983
|}
"""

JA = """
== あ行 ==
{| class="wikitable"
!色!!色名!!備考
|-
|bgcolor="#165e83" style="color:white"|<br/>#165E83||あいいろ<br/>[[藍色]]||[[染料]]の「[[アイ (植物)|アイ(藍)]]」の色。
|-
|bgcolor="#F47983"|<br/>#F47983||ももいろ<br/>[[桃色]]||[[モモ|桃]]の花の色。
|-
|bgcolor="#f08f91"|<br/>#F08F91||いっこんぞめ<br/>[[一斤染]]||紅花染の淡い色。
|}
"""


def test_t022_parse_en():
    got = parse_en_wikitext(EN)
    assert got == [
        ColorEntry(name="一斤染", reading="Ikkonzome", hex="#F08F90", note="One kin dye"),
        ColorEntry(name="桃色", reading="Momo-iro", hex="#F47983", note="Peach-colored"),
    ]


def test_t022b_parse_ja():
    got = parse_ja_wikitext(JA)
    assert [e.name for e in got] == ["藍色", "桃色", "一斤染"]
    assert got[0].hex == "#165E83"          # 小文字表記も正規化する
    assert got[0].reading == "あいいろ"
    assert "染料" in got[0].note            # 備考は語源の手がかり(B 層の材料)


def test_t022c_build_palette_joins_and_diffs():
    palette = build_palette({"en": parse_en_wikitext(EN), "ja": parse_ja_wikitext(JA)})
    by_name = {p.name: p for p in palette}

    # 両出典にある色: 値が同一なら ΔE = 0、違えば ΔE > 0
    assert by_name["桃色"].hex_by_source == {"en": "#F47983", "ja": "#F47983"}
    assert by_name["桃色"].delta_e == 0.0
    assert by_name["一斤染"].hex_by_source == {"en": "#F08F90", "ja": "#F08F91"}
    assert by_name["一斤染"].delta_e > 0.0

    # 片方だけの色は差分なし(欠落を 0 と混同しない)
    assert by_name["藍色"].hex_by_source == {"ja": "#165E83"}
    assert by_name["藍色"].delta_e is None

    # 全色に「HEX の典拠は記載なし」が付く(N-05)
    assert all(p.provenance == "記載なし" for p in palette)
