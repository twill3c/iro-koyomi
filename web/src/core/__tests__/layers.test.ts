// T-103 / T-105 / T-106 — 層フィルタ・色以外の伝達・充填率(F-04 / F-10 / N-03)
import { describe, expect, it } from "vitest";

import { chipLabel, fillSlices, filterByLayers } from "@/core/layers";
import type { ColorEntry, Fill } from "@/core/types";

function color(over: Partial<ColorEntry>): ColorEntry {
  return {
    id: "000", name: "色", readings: {}, hex_by_source: {}, delta_e: null,
    provenance: "記載なし", layer: "C", season: null, phase: null, kigo: null,
    origin: null, certainty: null, a_count: 0, b_count: 0, calendar_order: null,
    ...over,
  };
}

const 白 = color({ id: "1", name: "白", layer: "A", a_count: 161 });
const 山吹 = color({ id: "2", name: "山吹色", layer: "B", b_count: 11, season: "春", phase: "晩" });
const 今様 = color({ id: "3", name: "今様色", layer: "C" });

describe("filterByLayers", () => {
  it("層で絞り込む", () => {
    expect(filterByLayers([白, 山吹, 今様], ["A"]).map((c) => c.id)).toEqual(["1"]);
    expect(filterByLayers([白, 山吹, 今様], ["A", "B"]).map((c) => c.id)).toEqual(["1", "2"]);
  });

  it("C を選ぶと空欄の色が出る(隠さない)", () => {
    expect(filterByLayers([白, 山吹, 今様], ["C"]).map((c) => c.name)).toEqual(["今様色"]);
  });

  it("未選択は全件", () => {
    expect(filterByLayers([白, 山吹, 今様], []).length).toBe(3);
  });
});

describe("fillSlices", () => {
  const fill: Fill = { A: 19, B: 80, C: 270, total: 369 };

  it("A/B/C の三枠を必ず返し、比率の合計は 1", () => {
    const slices = fillSlices(fill);
    expect(slices.map((s) => s.layer)).toEqual(["A", "B", "C"]);
    expect(slices.reduce((a, s) => a + s.ratio, 0)).toBeCloseTo(1, 10);
  });

  it("C の割合を丸めて消さない", () => {
    expect(fillSlices(fill).find((s) => s.layer === "C")?.percentLabel).toBe("73.2%");
  });

  it("total が 0 でも壊れない(非有限値を出さない)", () => {
    const slices = fillSlices({ A: 0, B: 0, C: 0, total: 0 });
    expect(slices.every((s) => Number.isFinite(s.ratio))).toBe(true);
  });
});

describe("chipLabel(N-03: 色だけで伝えない)", () => {
  it("色名・季節・証拠を文字で出す", () => {
    expect(chipLabel(白)).toBe("白／季語なし／直接 161 句");
    expect(chipLabel(山吹)).toBe("山吹色／春晩／語源 11 句");
    expect(chipLabel(今様)).toBe("今様色／季語なし／句なし");
  });
});
