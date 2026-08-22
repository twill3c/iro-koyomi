"use client";

// 色覚シミュレーションとコントラスト比(F-11)。
import { useState } from "react";

import { contrastRatio, CVD_LABEL, CVD_TYPES, simulate, wcagLevel } from "@/core/vision";

const PAPER = "#FAF7F0";
const INK = "#1B1A17";

export default function VisionPanel({ hex }: { hex: string }) {
  const [normal, setNormal] = useState(true);
  const onPaper = contrastRatio(hex, PAPER);
  const withInk = contrastRatio(hex, INK);

  return (
    <section className="vision">
      <h3>見え方とコントラスト</h3>
      <div className="filters">
        <button aria-pressed={normal} onClick={() => setNormal(true)}>
          そのまま
        </button>
        <button aria-pressed={!normal} onClick={() => setNormal(false)}>
          三型を並べる
        </button>
      </div>
      <ul className="sims">
        <li>
          <span className="swatch" style={{ background: hex }} aria-hidden="true" />
          <span>一般色覚</span>
          <code>{hex}</code>
        </li>
        {!normal &&
          CVD_TYPES.map((t) => {
            const sim = simulate(hex, t);
            return (
              <li key={t}>
                <span className="swatch" style={{ background: sim }} aria-hidden="true" />
                <span>{CVD_LABEL[t]}</span>
                <code>{sim}</code>
              </li>
            );
          })}
      </ul>
      <table className="contrast">
        <tbody>
          <tr>
            <th>紙の色（{PAPER}）に対して</th>
            <td>
              {onPaper.toFixed(2)}:1（{wcagLevel(onPaper)}）
            </td>
          </tr>
          <tr>
            <th>墨の色（{INK}）に対して</th>
            <td>
              {withInk.toFixed(2)}:1（{wcagLevel(withInk)}）
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  );
}
