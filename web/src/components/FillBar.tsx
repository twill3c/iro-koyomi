import { fillSlices, LAYER_LABEL } from "@/core/layers";
import type { Fill } from "@/core/types";

/** 充填率(F-10)。C の割合こそが主題なので、必ず描く。 */
export default function FillBar({ fill }: { fill: Fill }) {
  const slices = fillSlices(fill);
  return (
    <section className="fill">
      <h2>{fill.total} 色のうち、句に結びついたのは</h2>
      <div className="fill-bar" role="img" aria-label={slices.map((s) => `${LAYER_LABEL[s.layer]} ${s.count}色 ${s.percentLabel}`).join("、")}>
        {slices.map((s) => (
          <div key={s.layer} className={`fill-seg ${s.layer}`} style={{ width: `${s.ratio * 100}%` }}>
            {s.ratio > 0.08 ? s.percentLabel : ""}
          </div>
        ))}
      </div>
      <ul className="fill-legend">
        {slices.map((s) => (
          <li key={s.layer}>
            <span className={`swatch ${s.layer}`} aria-hidden="true" />
            <b>{s.layer}</b> {LAYER_LABEL[s.layer]} — {s.count} 色（{s.percentLabel}）
          </li>
        ))}
      </ul>
    </section>
  );
}
