"""句コーパスの構築(F-02 の出力を集約)。

silver は派生物なのでコミットしない(bronze と同じ扱い)。web 向けの gold は別途生成する。
"""
from __future__ import annotations

import json
from pathlib import Path

from pipeline.aozora_index import load_rows
from pipeline.aozora_text import fetch_text
from pipeline.census import _load_tsv
from pipeline.extract_haiku import extract

SILVER = Path("data/silver/haiku.jsonl")


def build() -> list[dict]:
    index = {(r["姓"] + r["名"], r["作品名"]): r for r in load_rows() if r["役割フラグ"] == "著者"}
    out = []
    for author, title, tier, status, *_ in _load_tsv("data/curated/census_candidates.tsv"):
        if status != "confirmed":
            continue
        row = index[(author, title)]
        text = fetch_text(row["テキストファイルURL"], row["作品ID"])
        for h in extract(text):
            out.append(
                {
                    "author": author,
                    "work": title,
                    "work_id": row["作品ID"],
                    "card_url": row["図書カードURL"],
                    "text": h.text,
                    "norm": h.norm,
                    "start": h.start,
                    "end": h.end,
                }
            )
    SILVER.parent.mkdir(parents=True, exist_ok=True)
    SILVER.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in out) + "\n", encoding="utf-8")
    return out


def load() -> list[dict]:
    if not SILVER.exists():
        return build()
    return [json.loads(l) for l in SILVER.read_text(encoding="utf-8").splitlines() if l.strip()]


if __name__ == "__main__":
    print(f"句 {len(build())} 件 → {SILVER}")
