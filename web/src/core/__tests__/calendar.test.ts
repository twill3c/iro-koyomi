// T-102 — 色暦の並び(F-08)
import { describe, expect, it } from "vitest";

import { groupBySeason, sortByCalendar } from "@/core/calendar";
import type { ColorEntry } from "@/core/types";

function color(over: Partial<ColorEntry>): ColorEntry {
  return {
    id: "000", name: "色", readings: {}, hex_by_source: {}, delta_e: null,
    provenance: "記載なし", layer: "C", season: null, phase: null, kigo: null,
    origin: null, certainty: null, a_count: 0, b_count: 0, calendar_order: null,
    ...over,
  };
}

const 若菜 = color({ id: "1", name: "若菜色", season: "新年", phase: "三", calendar_order: [0, 0] });
const 桜 = color({ id: "2", name: "桜色", season: "春", phase: "晩", calendar_order: [1, 3] });
const 鶯 = color({ id: "3", name: "鶯色", season: "春", phase: "三", calendar_order: [1, 0] });
const 朽葉 = color({ id: "4", name: "朽葉色", season: "冬", phase: "三", calendar_order: [4, 0] });
const 今様 = color({ id: "5", name: "今様色" });

describe("sortByCalendar", () => {
  it("新年→春→夏→秋→冬、季内は通季が先", () => {
    const got = sortByCalendar([桜, 朽葉, 若菜, 鶯]);
    expect(got.map((c) => c.name)).toEqual(["若菜色", "鶯色", "桜色", "朽葉色"]);
  });

  it("季語のない色は末尾に置く(捨てない)", () => {
    const got = sortByCalendar([今様, 桜]);
    expect(got.map((c) => c.name)).toEqual(["桜色", "今様色"]);
  });

  it("入力順に関わらず同じ並びになる(決定論)", () => {
    const a = sortByCalendar([桜, 鶯, 今様, 若菜]).map((c) => c.id);
    const b = sortByCalendar([今様, 若菜, 桜, 鶯]).map((c) => c.id);
    expect(a).toEqual(b);
  });
});

describe("groupBySeason", () => {
  it("五季 + 季語なしの枠を必ず返す。空の季節も残す", () => {
    const groups = groupBySeason([若菜, 桜, 今様]);
    expect(groups.map((g) => g.season)).toEqual(["新年", "春", "夏", "秋", "冬", "季語なし"]);
    expect(groups.find((g) => g.season === "夏")?.colors).toEqual([]);
    expect(groups.find((g) => g.season === "季語なし")?.colors.map((c) => c.name)).toEqual(["今様色"]);
  });
});
