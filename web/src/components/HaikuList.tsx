import { highlight } from "@/core/detail";
import type { HaikuHit } from "@/lib/gold";

/**
 * 句の一覧。A 層は色語を、B 層は由来語を強調するが、
 * **B 層に「この色を詠んだ句」と書いてはならない**(F-04)。
 */
export default function HaikuList({ haiku, layer }: { haiku: HaikuHit[]; layer: "A" | "B" }) {
  if (haiku.length === 0) {
    return <p className="empty">該当する句はない。</p>;
  }
  return (
    <ul className="haiku">
      {haiku.map((h, i) => {
        const parts = highlight(h.norm, h.start, h.end);
        return (
          <li key={`${h.work}-${h.start}-${i}`}>
            <p className="verse">
              {parts.before}
              <mark className={layer === "A" ? "direct" : "origin"}>{parts.match}</mark>
              {parts.after}
            </p>
            <p className="source">
              {h.author}『{h.work}』
              {layer === "B" && h.origin ? `／由来語「${h.origin}」` : ""}
              {layer === "A" && h.sense_width ? "／語義に幅のある語（色票の値とは結ばない）" : ""}
            </p>
            <p className="base">
              底本: {h.base_text}（{h.publisher}）／入力 {h.typist}・校正 {h.proofreader}／
              <a href={h.card_url}>図書カード</a>
            </p>
          </li>
        );
      })}
    </ul>
  );
}
