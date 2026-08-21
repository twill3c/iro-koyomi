"""A 層照合の実行(F-04 / F-05)。

出力は色ごとの A 層句と充填率。**C(空欄)を埋めるための規則緩和は行わない**(G-06)。
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from pipeline.corpus import load as load_corpus
from pipeline.lexicon import build_lexicon, find_color_words, load_exclusions

OUT = Path("data/silver/layer_a.jsonl")


def main() -> None:
    lexicon = build_lexicon()
    exclusions = load_exclusions()
    corpus = load_corpus()

    records, per_color, flagged = [], Counter(), 0
    for haiku in corpus:
        hits = find_color_words(haiku["norm"], lexicon, exclusions)
        if not hits:
            continue
        for hit in hits:
            per_color[hit.color_name] += 1
            flagged += int(hit.sense_width)
        records.append(
            {
                "author": haiku["author"],
                "work": haiku["work"],
                "text": haiku["text"],
                "norm": haiku["norm"],
                "hits": [
                    {
                        "term": h.term,
                        "color_name": h.color_name,
                        "start": h.start,
                        "end": h.end,
                        "sense_width": h.sense_width,
                        "connectable": h.connectable,
                    }
                    for h in hits
                ],
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")

    palette = json.loads(Path("data/colors/palette.json").read_text(encoding="utf-8"))["colors"]
    total_colors = len(palette)
    filled = sum(1 for c in palette if per_color.get(c["name"]))
    lines = [
        "# A 層照合の結果(F-04 / F-05)",
        "",
        f"- 句 **{len(corpus)}** 中、色語を含む句は **{len(records)}**({len(records)/len(corpus):.1%})",
        f"- 色語の延べ出現 **{sum(per_color.values())}** / 異なり **{len(per_color)}** 語",
        f"- 色票 **{total_colors}** 色のうち A 層で埋まるのは **{filled}** 色"
        f"(**充填率 {filled/total_colors:.1%}**)。残る **{total_colors - filled}** 色は空欄のまま出す",
        f"- 語義幅フラグ付きのヒット **{flagged}** 件(青・蒼・碧。色票 HEX とは接続しない)",
        "",
        "俳句が使う色語彙は、伝統色の名づけの豊かさとは比べものにならないほど狭い。",
        "これは欠測ではなく、本アプリが示したい事実そのものである。",
        "",
        "| 色 | A 層の句数 |",
        "|---|---:|",
    ]
    lines += [f"| {name} | {n} |" for name, n in per_color.most_common()]
    names = {c["name"] for c in palette}
    orphans = [n for n in per_color if n not in names]
    if orphans:
        lines += [
            "",
            "## 色票に無い色語",
            "",
            "俳人が使っているのに、採用した 2 出典の色名一覧には載っていない語。",
            "色名の一覧が言葉の使われ方を写したものではないことの、もう一つの証拠である。",
            "",
            "| 色語 | 句数 |",
            "|---|---:|",
        ] + [f"| {n} | {per_color[n]} |" for n in sorted(orphans, key=lambda x: -per_color[x])]
    Path("docs/layer_a_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"A 層 {len(records)} 句 / 充填 {filled}/{total_colors} 色 → {OUT}")


if __name__ == "__main__":
    main()
