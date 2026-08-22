import Link from "next/link";

import { chipLabel, LAYER_LABEL } from "@/core/layers";
import type { ColorEntry } from "@/core/types";

/** 代表色は出典の最初の値。値が食い違うことは詳細で示すため、ここでは 1 つに決め打たない。 */
function firstHex(color: ColorEntry): string | null {
  const values = Object.values(color.hex_by_source);
  return values.length > 0 ? values[0] : null;
}

export default function ColorChip({ color }: { color: ColorEntry }) {
  const hex = firstHex(color);
  const sources = Object.keys(color.hex_by_source).length;
  return (
    <li>
      <Link className="chip" href={`/color/${color.id}/`} title={chipLabel(color)}>
        <span className="swatch" style={hex ? { background: hex } : undefined} aria-hidden="true">
          {hex ? null : <span className="none">値なし</span>}
        </span>
        <span className="body">
          <span className="name">{color.name}</span>
          <span className="meta">
            <span className={`layer ${color.layer}`}>{color.layer}</span>
            {LAYER_LABEL[color.layer]}
          </span>
          <span className="meta">
            {color.season ? `${color.season}${color.phase === "三" ? "" : (color.phase ?? "")}` : "季語なし"}
            {color.kigo ? `・${color.kigo}` : ""}
            {color.certainty && color.certainty !== "established" ? "（諸説あり）" : ""}
          </span>
          <span className="meta">
            {sources >= 2
              ? `出典 ${sources} 件・ΔE ${color.delta_e?.toFixed(1) ?? "—"}`
              : "出典 1 件（比較なし）"}
          </span>
        </span>
      </Link>
    </li>
  );
}
