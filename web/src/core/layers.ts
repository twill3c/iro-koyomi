/** 三層の絞り込みと充填率(F-04 / F-10)。C を隠さないことが要件。 */
import type { ColorEntry, Fill, Layer } from "./types";

export const LAYER_LABEL: Record<Layer, string> = {
  A: "直接（句に色語）",
  B: "語源（由来語が句に）",
  C: "空欄",
};

export function filterByLayers(colors: ColorEntry[], layers: Layer[]): ColorEntry[] {
  if (layers.length === 0) return colors;
  return colors.filter((c) => layers.includes(c.layer));
}

export interface FillSlice {
  layer: Layer;
  count: number;
  ratio: number;
  percentLabel: string;
}

/** 充填率の内訳。合計は必ず 1 になり、C が 0 でない限り必ず含まれる。 */
export function fillSlices(fill: Fill): FillSlice[] {
  const total = fill.total || 1;
  return (["A", "B", "C"] as Layer[]).map((layer) => {
    const count = fill[layer];
    return {
      layer,
      count,
      ratio: count / total,
      percentLabel: `${((count / total) * 100).toFixed(1)}%`,
    };
  });
}

/**
 * 色チップに添えるテキスト。色だけで情報を伝えない(N-03)ため、
 * 色名・層・季節・句数を必ず文字でも出す。
 */
export function chipLabel(color: ColorEntry): string {
  const season = color.season ? `${color.season}${color.phase === "三" ? "" : color.phase}` : "季語なし";
  const evidence =
    color.layer === "A"
      ? `直接 ${color.a_count} 句`
      : color.layer === "B"
        ? `語源 ${color.b_count} 句`
        : "句なし";
  return `${color.name}／${season}／${evidence}`;
}
