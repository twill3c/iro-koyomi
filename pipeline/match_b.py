"""B 層照合(F-04 / F-06)。

B 層は「**色名の由来語**が句に現れる」ことを指す。語の一致という事実ではあるが、
色への言及ではない。`is_color_mention` は常に False であり、ここを真にしてはならない。
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ORIGINS_TSV = Path("data/curated/color_origins.tsv")
CERTAINTIES = {"established", "contested", "approximate"}


@dataclass(frozen=True)
class Origin:
    color_name: str
    origin: str          # 色名の由来になった物の名
    kigo: str            # 対応する季語(由来語と異なることがある)
    certainty: str       # established | contested | approximate
    note: str = ""


@dataclass(frozen=True)
class OriginHit:
    color_name: str
    origin: str
    kigo: str
    certainty: str
    start: int
    end: int

    layer: str = "B"

    @property
    def is_color_mention(self) -> bool:
        """B 層は色への言及ではない(F-04)。"""
        return False


def load_origins(path: Path = ORIGINS_TSV) -> list[Origin]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        color_name, origin, kigo, certainty, *rest = line.split("\t")
        if certainty.strip() not in CERTAINTIES:
            raise ValueError(f"certainty 未設定または不正: {color_name}/{certainty!r}")
        out.append(
            Origin(
                color_name=color_name.strip(),
                origin=origin.strip(),
                kigo=kigo.strip(),
                certainty=certainty.strip(),
                note=rest[0].strip() if rest else "",
            )
        )
    return out


def find_origin_words(text: str, origins: list[Origin]) -> list[OriginHit]:
    hits = []
    for o in origins:
        start = text.find(o.origin)
        while start != -1:
            hits.append(
                OriginHit(
                    color_name=o.color_name,
                    origin=o.origin,
                    kigo=o.kigo,
                    certainty=o.certainty,
                    start=start,
                    end=start + len(o.origin),
                )
            )
            start = text.find(o.origin, start + 1)
    return sorted(hits, key=lambda h: (h.start, h.color_name))


def main() -> None:
    """B 層照合を実行し、A/B/C の充填率と歳時記順の並びを報告する。"""
    import json
    from collections import Counter

    from pipeline.corpus import load as load_corpus
    from pipeline.saijiki.kigo import calendar_order, load_kigo

    origins = load_origins()
    corpus = load_corpus()
    per_color: Counter[str] = Counter()
    records = []
    for haiku in corpus:
        hits = find_origin_words(haiku["norm"], origins)
        if not hits:
            continue
        for h in hits:
            per_color[h.color_name] += 1
        records.append(
            {
                "author": haiku["author"],
                "work": haiku["work"],
                "text": haiku["text"],
                "hits": [
                    {"color_name": h.color_name, "origin": h.origin, "kigo": h.kigo,
                     "certainty": h.certainty, "start": h.start, "end": h.end, "layer": "B"}
                    for h in hits
                ],
            }
        )
    out = Path("data/silver/layer_b.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")

    palette = json.loads(Path("data/colors/palette.json").read_text(encoding="utf-8"))["colors"]
    layer_a = {}
    a_path = Path("data/silver/layer_a.jsonl")
    if a_path.exists():
        for line in a_path.read_text(encoding="utf-8").splitlines():
            for hit in json.loads(line)["hits"]:
                layer_a[hit["color_name"]] = layer_a.get(hit["color_name"], 0) + 1

    kigo_by_name = {k.name: k for k in load_kigo()}
    origin_by_color = {o.color_name: o for o in origins}
    a_only = {c["name"] for c in palette if layer_a.get(c["name"])}
    b_only = {c["name"] for c in palette if c["name"] in per_color} - a_only
    empty = {c["name"] for c in palette} - a_only - b_only

    ordered = sorted(
        (c["name"] for c in palette if c["name"] in origin_by_color),
        key=lambda n: calendar_order(kigo_by_name[origin_by_color[n].kigo]) + (n,),
    )
    lines = [
        "# B 層と歳時記の並び(F-04 / F-06)",
        "",
        f"- 由来語を確定した色 **{len(origin_by_color)}** / 色票 {len(palette)}",
        f"- 由来語が句に現れた色 **{len(per_color)}**、B 層の句 **{len(records)}**",
        "",
        "## 三層の充填",
        "",
        "| 層 | 色数 | 割合 |",
        "|---|---:|---:|",
        f"| A 直接(句に色語) | {len(a_only)} | {len(a_only)/len(palette):.1%} |",
        f"| B 語源(由来語が句に) | {len(b_only)} | {len(b_only)/len(palette):.1%} |",
        f"| C 空欄 | {len(empty)} | {len(empty)/len(palette):.1%} |",
        "",
        "**C は埋めない。** 空欄の多さがこのアプリの主張である(G-06)。",
        "",
        "## 汎用語による B 層の薄さ",
        "",
        "由来語が句によく現れる語(月・梅など)ほど B 層の句数は増えるが、",
        "「月を詠んだ句」が「月白という色の句」であるわけではない。",
        "出現の多い由来語は結び付きが薄いものとして certainty に反映し、下表に出す。",
        "",
        "| 由来語 | 句数 | 対応する色 |",
        "|---|---:|---|",
    ] + [
        f"| {o} | {n} | {'・'.join(sorted(c for c in per_color if origin_by_color[c].origin == o))} |"
        for o, n in sorted(
            {origin_by_color[c].origin: per_color[c] for c in per_color}.items(),
            key=lambda x: -x[1],
        )[:5]
    ] + [
        "",
        "## 歳時記順(由来語を持つ色)",
        "",
        "| 季 | 時候 | 季語 | 色 | certainty | B 層の句数 |",
        "|---|---|---|---|---|---:|",
    ]
    for name in ordered:
        o = origin_by_color[name]
        k = kigo_by_name[o.kigo]
        lines.append(
            f"| {k.season} | {k.phase} | {k.name} | {name} | {o.certainty} | {per_color.get(name, 0)} |"
        )
    Path("docs/layer_b_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"B 層 {len(records)} 句 / A {len(a_only)} + B {len(b_only)} + C {len(empty)} = {len(palette)} 色")


if __name__ == "__main__":
    main()
