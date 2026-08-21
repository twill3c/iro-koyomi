"""色票基盤の生成(F-03)。

出典は人間承認済みの CC BY-SA 2 系統のみ。JIS Z 8102 は参照リンクとして扱い、
数値・名称表を取り込まない(N-05)。
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

from pipeline.color.sources import build_palette, parse_en_wikitext, parse_ja_wikitext

BRONZE = Path("data/bronze")
OUT = Path("data/colors")

SOURCES = {
    "en": {
        "file": "wp_en_colors.wiki",
        "title": 'en.wikipedia "Traditional colors of Japan"',
        "url": "https://en.wikipedia.org/wiki/Traditional_colors_of_Japan",
        "license": "CC BY-SA 4.0",
        "parser": parse_en_wikitext,
    },
    "ja": {
        "file": "wp_ja_colors.wiki",
        "title": "ja.wikipedia「日本の色の一覧」",
        "url": "https://ja.wikipedia.org/wiki/日本の色の一覧",
        "license": "CC BY-SA 4.0",
        "parser": parse_ja_wikitext,
    },
}

JIS_REFERENCE = {
    "name": "JIS Z 8102 慣用色名",
    "url": "https://www.jisc.go.jp/",
    "note": "唯一の公的基準だが規格票のため数値・名称表を転載しない(参照のみ)",
}


def main() -> None:
    by_source = {
        key: meta["parser"]((BRONZE / meta["file"]).read_text(encoding="utf-8"))
        for key, meta in SOURCES.items()
    }
    palette = sorted(build_palette(by_source), key=lambda p: p.name)
    both = [p for p in palette if p.delta_e is not None]

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "palette.json").write_text(
        json.dumps(
            {
                "sources": {k: {x: v[x] for x in ("title", "url", "license")} for k, v in SOURCES.items()},
                "jis_reference": JIS_REFERENCE,
                "colors": [
                    {
                        "name": p.name,
                        "readings": p.readings,
                        "hex_by_source": p.hex_by_source,
                        "delta_e": round(p.delta_e, 4) if p.delta_e is not None else None,
                        "provenance": p.provenance,
                        "notes": p.notes,
                    }
                    for p in palette
                ],
            },
            ensure_ascii=False,
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )

    des = sorted((p.delta_e for p in both), reverse=True)
    top = sorted(both, key=lambda p: -p.delta_e)[:12]
    lines = [
        "# 色票と出典差(F-03)",
        "",
        f"- 色名 **{len(palette)}** 件(en {len(by_source['en'])} / ja {len(by_source['ja'])})",
        f"- 両出典に値がある色 **{len(both)}** 件。うち **完全一致(ΔE=0)は {sum(1 for d in des if d == 0)} 件**",
        f"- ΔE2000 中央値 **{statistics.median(des):.2f}** / 最大 **{des[0]:.2f}**",
        "- **両出典とも HEX の典拠を書いていない**(provenance: 記載なし)",
        "",
        "ΔE2000 は 1 以下が「訓練された目でようやく判別」、5 を超えれば誰にでも別の色に見える。",
        "中央値が 10 を超えるということは、同じ色名が出典によって**別の色**を指しているということである。",
        "",
        "## 差の大きい色",
        "",
        "| 色名 | en | ja | ΔE2000 |",
        "|---|---|---|---:|",
    ]
    for p in top:
        lines.append(f"| {p.name} | `{p.hex_by_source['en']}` | `{p.hex_by_source['ja']}` | {p.delta_e:.1f} |")
    lines += ["", "## ライセンス", ""]
    for meta in SOURCES.values():
        lines.append(f"- [{meta['title']}]({meta['url']}) — {meta['license']}")
    lines += [
        f"- {JIS_REFERENCE['name']}: {JIS_REFERENCE['note']}",
        "",
        "両出典が CC BY-SA 4.0 のため、`data/colors/palette.json` も **CC BY-SA 4.0** で再配布する",
        "(コードは MIT)。2026-08-22 人間承認済み。",
        "",
    ]
    Path("docs/palette_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"色名 {len(palette)} / 両出典 {len(both)} / ΔE 中央値 {statistics.median(des):.2f} → data/colors/palette.json")


if __name__ == "__main__":
    main()
