// T-104 — 詳細画面の描画データ(F-09)
import { describe, expect, it } from "vitest";

import { highlight, sourceRows } from "@/core/detail";

describe("sourceRows", () => {
  it("出典 2 件なら 2 行と ΔE の表示を返す", () => {
    const rows = sourceRows({ en: "#F08F90", ja: "#F08F91" }, 0.34, "記載なし");
    expect(rows.rows.map((r) => r.source)).toEqual(["en", "ja"]);
    expect(rows.deltaLabel).toBe("ΔE2000 = 0.34");
    expect(rows.rows.every((r) => r.provenance === "記載なし")).toBe(true);
  });

  it("出典 1 件なら比較しない(0 と書かない)", () => {
    const rows = sourceRows({ ja: "#165E83" }, null, "記載なし");
    expect(rows.rows).toHaveLength(1);
    expect(rows.deltaLabel).toBe("出典 1 件のため比較なし");
  });

  it("出典 3 件でも全行返す", () => {
    expect(sourceRows({ a: "#000000", b: "#111111", c: "#222222" }, 1.5, "記載なし").rows).toHaveLength(3);
  });
});

describe("highlight", () => {
  it("色語の位置で 3 分割する", () => {
    expect(highlight("白牡丹といふといへども紅ほのか", 11, 12)).toEqual({
      before: "白牡丹といふといへども",
      match: "紅",
      after: "ほのか",
    });
  });

  it("先頭一致でも壊れない", () => {
    expect(highlight("白牡丹や", 0, 1)).toEqual({ before: "", match: "白", after: "牡丹や" });
  });

  it("範囲外は素通しする(非正常値でも落とさない)", () => {
    expect(highlight("あをあらし", 9, 12)).toEqual({ before: "あをあらし", match: "", after: "" });
  });
});
