import Link from "next/link";

import Footer from "@/components/Footer";
import HaikuList from "@/components/HaikuList";
import VisionPanel from "@/components/VisionPanel";
import { sourceRows } from "@/core/detail";
import { LAYER_LABEL } from "@/core/layers";
import { colorIds, readColor } from "@/lib/gold";

export function generateStaticParams() {
  return colorIds().map((id) => ({ id }));
}

const CERTAINTY_LABEL: Record<string, string> = {
  established: "定説",
  contested: "諸説あり",
  approximate: "近似・推定",
};

export default async function ColorPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const color = readColor(id);
  const table = sourceRows(color.hex_by_source, color.delta_e, color.provenance);
  const primary = table.rows[0]?.hex ?? null;

  return (
    <main className="hall">
      <header className="masthead">
        <p className="eyebrow">
          <Link href="/">色暦</Link> ／ {LAYER_LABEL[color.layer]}
        </p>
        <h1>
          {color.name}
          {color.readings.ja ? <small>（{color.readings.ja}）</small> : null}
        </h1>
        <p className="lede">
          {color.kigo
            ? `由来「${color.origin}」— ${color.season}${color.phase === "三" ? "（通季）" : color.phase}の季語「${color.kigo}」／${CERTAINTY_LABEL[color.certainty ?? "established"]}`
            : "由来語を確定していない色（歳時記に載せていない）"}
        </p>
      </header>

      <section className="sources">
        <h3>出典ごとのカラーコード</h3>
        <table className="hexes">
          <thead>
            <tr>
              <th>出典</th>
              <th>HEX</th>
              <th>HEX の典拠</th>
            </tr>
          </thead>
          <tbody>
            {table.rows.map((r) => (
              <tr key={r.source}>
                <th>{r.source}</th>
                <td>
                  <span className="swatch" style={{ background: r.hex }} aria-hidden="true" />
                  <code>{r.hex}</code>
                </td>
                <td>{r.provenance}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="delta">{table.deltaLabel}</p>
      </section>

      {primary ? <VisionPanel hex={primary} /> : null}

      <section className="layer">
        <h3>A 直接 — 句に色語が現れる（{color.a_count} 句）</h3>
        <HaikuList haiku={color.layer_a} layer="A" />
      </section>

      <section className="layer">
        <h3>B 語源 — 由来語が現れる（{color.b_count} 句）</h3>
        <p className="caveat">
          由来語が詠まれているというだけで、<b>この色について詠まれた句ではない</b>。
        </p>
        <HaikuList haiku={color.layer_b} layer="B" />
      </section>

      <Footer />
    </main>
  );
}
