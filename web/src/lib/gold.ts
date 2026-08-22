/** ビルド時に gold を読む(静的 export のため実行時 API は持たない — N-01)。 */
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

import type { ColorEntry } from "@/core/types";

const DIR = join(process.cwd(), "public", "data");

export interface ColorDetail extends ColorEntry {
  notes: Record<string, string>;
  layer_a: HaikuHit[];
  layer_b: HaikuHit[];
}

export interface HaikuHit {
  author: string;
  work: string;
  text: string;
  norm: string;
  card_url: string;
  base_text: string;
  publisher: string;
  typist: string;
  proofreader: string;
  start: number;
  end: number;
  is_color_mention: boolean;
  term?: string;
  sense_width?: boolean;
  connectable?: boolean;
  origin?: string;
  kigo?: string;
  certainty?: string;
}

export function colorIds(): string[] {
  return readdirSync(join(DIR, "colors"))
    .filter((f) => f.endsWith(".json"))
    .map((f) => f.replace(/\.json$/, ""))
    .sort();
}

export function readColor(id: string): ColorDetail {
  return JSON.parse(readFileSync(join(DIR, "colors", `${id}.json`), "utf8"));
}
