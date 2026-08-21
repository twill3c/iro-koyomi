"""青空文庫の全作品拡張索引(list_person_all_extended_utf8.csv)の読み込み。

取得は手動コマンドのみ(N-02)。本モジュールは取得済み zip を読むだけで、
ネットワークにはアクセスしない(テストがネットワーク非依存であるため)。
"""
from __future__ import annotations

import csv
import io
import zipfile
from pathlib import Path

from pipeline.copyright import parse_death_year

INDEX_ZIP = Path("data/bronze/aozora_index.zip")


def load_rows(zip_path: Path = INDEX_ZIP) -> list[dict]:
    with zipfile.ZipFile(zip_path) as z:
        name = z.namelist()[0]
        with z.open(name) as f:
            return list(csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig")))


def to_work_row(row: dict) -> tuple:
    """census の WorkRow 形式へ写す。"""
    return (
        row["作品ID"],
        row["作品名"] + (("(" + row["副題"] + ")") if row["副題"] else ""),
        row["人物ID"],
        f'{row["姓"]}{row["名"]}',
        parse_death_year(row["没年月日"]),
        row["人物著作権フラグ"],
    )
