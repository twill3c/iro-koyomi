// T-100 / T-101 — 色覚シミュレーションとコントラスト比(F-11 / G-02)
//
// 二色型色覚のシミュレーションには、公開されていて出所を辿れる検証データセットが
// 見つからなかった。実装から期待値を転記するのは禁止(TEST_SPEC 実行規約)なので、
// 変換が数学的に満たすべき**不変量**をオラクルにする:
//   1. 無彩色は動かない(灰色軸は混同平面上にある)
//   2. 冪等である(平面への射影を 2 回かけても同じ)
//   3. 混同線上の色は同じ色に潰れる(赤と緑が近づく)
// コントラスト比は WCAG 2.x の定義から期待値が一意に決まるため既知値で固定する。
import { describe, expect, it } from "vitest";

import { CVD_TYPES, contrastRatio, simulate } from "@/core/vision";

const GRAYS = ["#000000", "#3C3C3C", "#808080", "#CFCFCF", "#FFFFFF"];

describe("simulate(不変量オラクル)", () => {
  it.each(CVD_TYPES)("%s: 無彩色は変化しない", (type) => {
    for (const gray of GRAYS) {
      expect(simulate(gray, type)).toBe(gray.toUpperCase());
    }
  });

  it.each(CVD_TYPES)("%s: 冪等(2 回かけても変わらない)", (type) => {
    for (const hex of ["#F08F90", "#165E83", "#F8B500", "#7D2431"]) {
      const once = simulate(hex, type);
      expect(simulate(once, type)).toBe(once);
    }
  });

  it.each(["protan", "deutan"] as const)("%s: 赤と緑が互いに近づく", (type) => {
    const red = simulate("#FF0000", type);
    const green = simulate("#00FF00", type);
    const dist = (a: string, b: string) =>
      Math.abs(parseInt(a.slice(1, 3), 16) - parseInt(b.slice(1, 3), 16)) +
      Math.abs(parseInt(a.slice(3, 5), 16) - parseInt(b.slice(3, 5), 16)) +
      Math.abs(parseInt(a.slice(5, 7), 16) - parseInt(b.slice(5, 7), 16));
    expect(dist(red, green)).toBeLessThan(dist("#FF0000", "#00FF00"));
  });

  it.each(["protan", "deutan"] as const)("%s: 軸に取った青は動かない(拘束条件)", (type) => {
    expect(simulate("#0000FF", type)).toBe("#0000FF");
  });

  it("tritan: 軸に取った赤は動かない(拘束条件)", () => {
    expect(simulate("#FF0000", "tritan")).toBe("#FF0000");
  });

  it("出力は常に 6 桁の 16 進表記", () => {
    for (const type of CVD_TYPES) {
      expect(simulate("#F08F90", type)).toMatch(/^#[0-9A-F]{6}$/);
    }
  });
});

describe("contrastRatio(WCAG 既知値)", () => {
  it("白と黒は 21:1", () => {
    expect(contrastRatio("#FFFFFF", "#000000")).toBeCloseTo(21, 6);
  });

  it("同じ色どうしは 1:1", () => {
    expect(contrastRatio("#7D2431", "#7D2431")).toBeCloseTo(1, 10);
  });

  it("対称である", () => {
    expect(contrastRatio("#FFFFFF", "#767676")).toBeCloseTo(
      contrastRatio("#767676", "#FFFFFF"), 10,
    );
  });

  it("#777777 と白は約 4.48:1(WCAG AA の境界近傍として周知の値)", () => {
    expect(contrastRatio("#777777", "#FFFFFF")).toBeCloseTo(4.48, 2);
  });
});
