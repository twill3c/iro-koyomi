"""gold 生成(F-07)。

web は静的ビューアであり、分析はここで終える。層の決定は**証拠の有無**だけで行う:
A 層の句があれば A、無く B 層があれば B、どちらも無ければ C(空欄)。
C を埋めるための緩和は行わない(G-06)。
"""
from __future__ import annotations

import json
from pathlib import Path

from pipeline.lexicon import Term, find_color_words
from pipeline.match_b import Origin, find_origin_words
from pipeline.saijiki.kigo import Kigo, calendar_order

OUT = Path("web/public/data")


def _attribution(haiku: dict) -> dict:
    return {
        "author": haiku["author"],
        "work": haiku["work"],
        "text": haiku["text"],
        "card_url": haiku["card_url"],
        "base_text": haiku["base_text"],
        "publisher": haiku["publisher"],
        "typist": haiku["typist"],
        "proofreader": haiku["proofreader"],
    }


def assemble(
    palette: list[dict],
    corpus: list[dict],
    lexicon: list[Term],
    exclusions: list[str],
    origins: list[Origin],
    kigo: list[Kigo],
) -> tuple[dict, dict]:
    kigo_by_name = {k.name: k for k in kigo}
    origin_by_color = {o.color_name: o for o in origins}

    layer_a: dict[str, list[dict]] = {}
    layer_b: dict[str, list[dict]] = {}
    for haiku in corpus:
        for hit in find_color_words(haiku["norm"], lexicon, exclusions):
            layer_a.setdefault(hit.color_name, []).append(
                {
                    **_attribution(haiku),
                    "norm": haiku["norm"],
                    "term": hit.term,
                    "start": hit.start,
                    "end": hit.end,
                    "sense_width": hit.sense_width,
                    "connectable": hit.connectable,
                    "is_color_mention": True,
                }
            )
        for hit in find_origin_words(haiku["norm"], origins):
            layer_b.setdefault(hit.color_name, []).append(
                {
                    **_attribution(haiku),
                    "norm": haiku["norm"],
                    "origin": hit.origin,
                    "kigo": hit.kigo,
                    "certainty": hit.certainty,
                    "start": hit.start,
                    "end": hit.end,
                    "is_color_mention": False,
                }
            )

    by_name = sorted(palette, key=lambda c: c["name"])
    index_colors, details, fill = [], {}, {"A": 0, "B": 0, "C": 0, "total": len(palette)}
    for n, color in enumerate(by_name, start=1):
        name = color["name"]
        a, b = layer_a.get(name, []), layer_b.get(name, [])
        layer = "A" if a else ("B" if b else "C")
        fill[layer] += 1
        origin = origin_by_color.get(name)
        k = kigo_by_name.get(origin.kigo) if origin else None
        cid = f"{n:03d}"
        entry = {
            "id": cid,
            "name": name,
            "readings": color["readings"],
            "hex_by_source": color["hex_by_source"],
            "delta_e": color["delta_e"],
            "provenance": color["provenance"],
            "layer": layer,
            "season": k.season if k else None,
            "phase": k.phase if k else None,
            "kigo": k.name if k else None,
            "origin": origin.origin if origin else None,
            "certainty": origin.certainty if origin else None,
            "a_count": len(a),
            "b_count": len(b),
            "calendar_order": list(calendar_order(k))[:2] if k else None,
        }
        index_colors.append(entry)
        details[cid] = {**entry, "notes": color.get("notes", {}), "layer_a": a, "layer_b": b}

    index = {"fill": fill, "colors": index_colors}
    return index, details


def main() -> None:
    from pipeline.corpus import load as load_corpus
    from pipeline.lexicon import build_lexicon, load_exclusions
    from pipeline.match_b import load_origins
    from pipeline.saijiki.kigo import load_kigo

    palette_doc = json.loads(Path("data/colors/palette.json").read_text(encoding="utf-8"))
    index, details = assemble(
        palette_doc["colors"],
        load_corpus(),
        build_lexicon(),
        load_exclusions(),
        load_origins(),
        load_kigo(),
    )
    index["sources"] = palette_doc["sources"]
    index["jis_reference"] = palette_doc["jis_reference"]

    (OUT / "colors").mkdir(parents=True, exist_ok=True)
    (OUT / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    for cid, detail in details.items():
        (OUT / "colors" / f"{cid}.json").write_text(
            json.dumps(detail, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
    print(
        f"gold: {len(index['colors'])} 色 "
        f"(A {index['fill']['A']} / B {index['fill']['B']} / C {index['fill']['C']}) → {OUT}"
    )


if __name__ == "__main__":
    main()
