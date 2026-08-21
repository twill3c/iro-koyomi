/** gold(web/public/data/index.json)の型。分析は済んでおり、web は並べ替えと表示だけを行う。 */

export type Layer = "A" | "B" | "C";
export type Season = "新年" | "春" | "夏" | "秋" | "冬";
export type Phase = "三" | "初" | "仲" | "晩";
export type Certainty = "established" | "contested" | "approximate";

export interface ColorEntry {
  id: string;
  name: string;
  readings: Record<string, string>;
  hex_by_source: Record<string, string>;
  delta_e: number | null;
  provenance: string;
  layer: Layer;
  season: Season | null;
  phase: Phase | null;
  kigo: string | null;
  origin: string | null;
  certainty: Certainty | null;
  a_count: number;
  b_count: number;
  calendar_order: [number, number] | null;
}

export interface Fill {
  A: number;
  B: number;
  C: number;
  total: number;
}

export interface ColorIndex {
  fill: Fill;
  colors: ColorEntry[];
  sources: Record<string, { title: string; url: string; license: string }>;
  jis_reference: { name: string; url: string; note: string };
}
