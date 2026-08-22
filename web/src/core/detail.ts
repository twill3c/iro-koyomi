/** 詳細画面の描画データ(F-09)。DOM に依存しない。 */

export interface SourceRow {
  source: string;
  hex: string;
  provenance: string;
}

export interface SourceTable {
  rows: SourceRow[];
  deltaLabel: string;
}

/** 出典別 HEX の表。**1 件のときに ΔE を 0 と書かない**(欠落と一致を混同しない)。 */
export function sourceRows(
  hexBySource: Record<string, string>,
  deltaE: number | null,
  provenance: string,
): SourceTable {
  const rows = Object.entries(hexBySource).map(([source, hex]) => ({ source, hex, provenance }));
  const deltaLabel =
    rows.length < 2
      ? "出典 1 件のため比較なし"
      : deltaE === null
        ? "ΔE2000 = —"
        : `ΔE2000 = ${deltaE.toFixed(2)}`;
  return { rows, deltaLabel };
}

export interface Highlighted {
  before: string;
  match: string;
  after: string;
}

/** 句を色語の位置で 3 分割する。範囲外は素通しし、例外にしない(N-04)。 */
export function highlight(text: string, start: number, end: number): Highlighted {
  if (!(start >= 0 && end <= text.length && start < end)) {
    return { before: text, match: "", after: "" };
  }
  return {
    before: text.slice(0, start),
    match: text.slice(start, end),
    after: text.slice(end),
  };
}
