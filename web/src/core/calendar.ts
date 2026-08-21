/** 歳時記順の並びと季節ごとの束ね(F-08)。DOM に依存しない。 */
import type { ColorEntry, Phase, Season } from "./types";

export const SEASON_ORDER: Season[] = ["新年", "春", "夏", "秋", "冬"];
export const PHASE_LABEL: Record<Phase, string> = {
  三: "通季",
  初: "初",
  仲: "仲",
  晩: "晩",
};

/** 季語を持つ色を歳時記順に、持たない色をその後ろに置く。並びは決定論。 */
export function sortByCalendar(colors: ColorEntry[]): ColorEntry[] {
  const keyed = colors.map((c, i) => ({ c, i }));
  keyed.sort((x, y) => {
    const a = x.c.calendar_order;
    const b = y.c.calendar_order;
    if (a && !b) return -1;
    if (!a && b) return 1;
    if (a && b) {
      if (a[0] !== b[0]) return a[0] - b[0];
      if (a[1] !== b[1]) return a[1] - b[1];
    }
    return x.c.name.localeCompare(y.c.name, "ja") || x.i - y.i;
  });
  return keyed.map((k) => k.c);
}

export interface SeasonGroup {
  season: Season | "季語なし";
  colors: ColorEntry[];
}

/** 季節ごとに束ねる。空の季節も枠として残す(欠落を隠さない)。 */
export function groupBySeason(colors: ColorEntry[]): SeasonGroup[] {
  const sorted = sortByCalendar(colors);
  const groups: SeasonGroup[] = SEASON_ORDER.map((season) => ({ season, colors: [] }));
  const none: SeasonGroup = { season: "季語なし", colors: [] };
  for (const color of sorted) {
    const group = groups.find((g) => g.season === color.season);
    (group ?? none).colors.push(color);
  }
  return [...groups, none];
}
