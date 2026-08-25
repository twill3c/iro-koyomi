"use client";

// 一覧(F-08 色暦の帯 + F-10 充填率)。分析は gold で終わっており、ここは並べ替えと表示のみ。
import { useEffect, useMemo, useState } from "react";

import { groupBySeason } from "@/core/calendar";
import { filterByLayers, LAYER_LABEL } from "@/core/layers";
import type { ColorIndex, Layer } from "@/core/types";
import { dataUrl } from "@/lib/basePath";

import ColorChip from "./ColorChip";
import FillBar from "./FillBar";
import Footer from "./Footer";

const LAYERS: Layer[] = ["A", "B", "C"];

export default function KoyomiPage() {
  const [index, setIndex] = useState<ColorIndex | null>(null);
  const [layers, setLayers] = useState<Layer[]>([]);

  useEffect(() => {
    fetch(dataUrl("index.json"))
      .then((r) => r.json())
      .then(setIndex)
      .catch(() => setIndex(null));
  }, []);

  const groups = useMemo(
    () => (index ? groupBySeason(filterByLayers(index.colors, layers)) : []),
    [index, layers],
  );

  const toggle = (l: Layer) =>
    setLayers((cur) => (cur.includes(l) ? cur.filter((x) => x !== l) : [...cur, l]));

  return (
    <main className="hall">
      <header className="masthead">
        <p className="eyebrow">日本の伝統色 × 青空文庫の俳句</p>
        <h1>色暦</h1>
        <p className="lede">
          伝統色を、その名の由来になった物（＝季語）を鍵に俳句と結び、歳時記の順に並べる。
          同じ色名でも出典によって値は食い違い、俳人が使った色語は驚くほど狭い。
          そのどちらも隠さずに出す。 <a href="/about/">この地図の読み方</a>
        </p>
        <p className="kanban">
          白牡丹といふといへども紅ほのか
          <cite>高浜虚子『五百句』</cite>
        </p>
      </header>

      {index ? <FillBar fill={index.fill} /> : <p>読み込み中…</p>}

      <div className="filters">
        {LAYERS.map((l) => (
          <button key={l} aria-pressed={layers.includes(l)} onClick={() => toggle(l)}>
            {l}：{LAYER_LABEL[l]}
          </button>
        ))}
        {layers.length > 0 ? <button onClick={() => setLayers([])}>絞り込みを解除</button> : null}
      </div>

      {groups.map((g) => (
        <section className="season" key={g.season}>
          <h3>
            {g.season}（{g.colors.length} 色）
          </h3>
          {g.colors.length === 0 ? (
            <p className="empty">この季に該当する色はない。</p>
          ) : (
            <ul className="strip">
              {g.colors.map((c) => (
                <ColorChip key={c.id} color={c} />
              ))}
            </ul>
          )}
        </section>
      ))}

      <Footer sources={index?.sources} jis={index?.jis_reference} />
    </main>
  );
}
