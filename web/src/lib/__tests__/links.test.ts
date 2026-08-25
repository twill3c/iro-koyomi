// T-107 — フッタ 5 リンク(F-12)
import { describe, expect, it } from "vitest";

import { FOOTER_LINKS } from "@/lib/links";

describe("FOOTER_LINKS", () => {
  it("5 件で、ラベルと href が揃っている", () => {
    expect(FOOTER_LINKS.map((l) => l.label)).toEqual([
      "MIT License", "GitHub", "色暦の読み方", "色暦設計図", "App Menu",
    ]);
    expect(FOOTER_LINKS.every((l) => l.href.length > 0)).toBe(true);
  });
});
