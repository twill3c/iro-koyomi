"""句コーパス棚卸し(F-01)。

Loop 0 の目的は「青空文庫から実際に何句取れるか」を実測することであり、
ここで色語辞書(F-05)や抽出規則(F-02)を確定させない。色語は census 用の
種辞書を外から渡し、異なり数の**下限**を測るだけに留める。
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

from pipeline.copyright import is_public_domain, parse_death_year

WorkRow = Sequence  # (work_id, title, person_id, author, death_year, copyright_flag)


def select_candidate_works(works: Iterable[WorkRow], keywords: Sequence[str]) -> list[WorkRow]:
    """題名に句集を示す語を含み、かつ著作権ゲートを通る作品のみ残す。"""
    out = []
    for w in works:
        title, death_year, flag = w[1], w[4], w[5]
        if not any(k in title for k in keywords):
            continue
        if not is_public_domain(death_year, flag):
            continue
        out.append(w)
    return out


def count_distinct_color_words(lines: Iterable[str], color_words: Sequence[str]) -> set[str]:
    return {w for line in lines for w in color_words if w in line}


def color_word_coverage(lines: Iterable[str], color_words: Sequence[str]) -> dict[str, int]:
    """色語ごとの出現句数(1 句内の複数回は 1 と数える)。"""
    c: Counter[str] = Counter()
    for line in lines:
        for w in color_words:
            if w in line:
                c[w] += 1
    return dict(c)


def summarize(
    works: Sequence[WorkRow],
    keywords: Sequence[str],
    lines: Sequence[str],
    color_words: Sequence[str],
) -> dict:
    cand = select_candidate_works(works, keywords)
    return {
        "candidate_works": len(cand),
        "candidate_authors": len({w[2] for w in cand}),
        "rejected_works": len(works) - len(cand),
        "lines": len(lines),
        "distinct_color_words": len(count_distinct_color_words(lines, color_words)),
        "color_word_coverage": color_word_coverage(lines, color_words),
    }


def _load_tsv(path: str) -> list[list[str]]:
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        rows.append(line.split("\t"))
    return rows


def main() -> None:
    """Loop 0: 候補作品を取得し、句数・作者数・色語異なり数を実測して報告する。"""
    from pipeline.aozora_index import load_rows
    from pipeline.aozora_text import fetch_text, haiku_candidates

    index = [r for r in load_rows() if r["役割フラグ"] == "著者"]
    by_key = {(r["姓"] + r["名"], r["作品名"]): r for r in index}
    color_words = [r[0] for r in _load_tsv("data/curated/color_words_seed.tsv")]

    results, all_lines, missing = [], [], []
    for author, title, tier in _load_tsv("data/curated/census_candidates.tsv"):
        row = by_key.get((author, title))
        if row is None:
            missing.append(f"{author}／{title}")
            continue
        if not is_public_domain(parse_death_year(row["没年月日"]), row["人物著作権フラグ"]):
            missing.append(f"{author}／{title}(著作権ゲート)")
            continue
        text = fetch_text(row["テキストファイルURL"], row["作品ID"])
        lines = haiku_candidates(text)
        all_lines += lines
        hits = count_distinct_color_words(lines, color_words)
        results.append((author, title, tier, row["作品ID"], len(lines), len(hits)))

    cov = color_word_coverage(all_lines, color_words)
    out = ["# census — 句コーパス棚卸し(F-01)", "",
           "抽出は census 用の保守的規則による**見積り**であり、F-02 の正式抽出とは別物である。", "",
           "| 作者 | 作品 | tier | 作品ID | 句候補 | 色語(異なり) |", "|---|---|---|---|---:|---:|"]
    for a, t, tier, wid, n, h in results:
        out.append(f"| {a} | {t} | {tier} | {wid} | {n} | {h} |")
    out += ["", f"- 作品 {len(results)} 件 / 作者 {len({r[0] for r in results})} 名 / 句候補 **{len(all_lines)}** 句",
            f"- 色語の異なり数 **{len(cov)}** / 種辞書 {len(color_words)} 語(充填率 {len(cov)/len(color_words):.0%})", ""]
    if missing:
        out += ["## 索引に無い・ゲート落ち", ""] + [f"- {m}" for m in missing] + [""]
    out += ["## 色語の出現句数(降順)", "", "| 色語 | 句数 |", "|---|---:|"]
    for w, n in sorted(cov.items(), key=lambda x: -x[1]):
        out.append(f"| {w} | {n} |")
    Path("docs/census.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"作品 {len(results)} / 句候補 {len(all_lines)} / 色語異なり {len(cov)} → docs/census.md")


if __name__ == "__main__":
    main()
