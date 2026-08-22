/**
 * 色覚シミュレーションとコントラスト比(F-11)。
 *
 * 二色型色覚の見えは、LMS 空間で欠損した錐体の応答を残る 2 錐体から線形に
 * 復元して得る(Viénot, Brettel & Mollon 1999 の方式)。復元係数は**定数として
 * 書き写さず、拘束条件から解く**: 「白が変わらないこと」と「軸となる原色が
 * 変わらないこと」の 2 条件で 2 未知数が一意に決まる。
 *
 * この定め方から、テストのオラクルになる不変量が従う:
 *   - 無彩色(白のスカラー倍)は動かない
 *   - 平面への射影なので冪等
 *   - 混同軸上の色は互いに潰れる(赤と緑が近づく)
 */

export const CVD_TYPES = ["protan", "deutan", "tritan"] as const;
export type CvdType = (typeof CVD_TYPES)[number];

export const CVD_LABEL: Record<CvdType, string> = {
  protan: "1 型（P・赤錐体が働かない）",
  deutan: "2 型（D・緑錐体が働かない）",
  tritan: "3 型（T・青錐体が働かない）",
};

// 線形 RGB → LMS(Hunt-Pointer-Estevez を sRGB 原色に合わせたもの)と、その逆
const RGB_TO_LMS = [
  [0.31399022, 0.63951294, 0.04649755],
  [0.15537241, 0.75789446, 0.08670142],
  [0.01775239, 0.10944209, 0.87256922],
];
const LMS_TO_RGB = [
  [5.47221206, -4.6419601, 0.16963708],
  [-1.1252419, 2.29317094, -0.1678952],
  [0.02980165, -0.19318073, 1.16364789],
];

function apply(matrix: number[][], v: number[]): number[] {
  return matrix.map((row) => row[0] * v[0] + row[1] * v[1] + row[2] * v[2]);
}

/** 2 元 1 次連立方程式を解く(拘束条件から復元係数を求めるため)。 */
function solve2(
  [a1, b1, c1]: [number, number, number],
  [a2, b2, c2]: [number, number, number],
): [number, number] {
  const det = a1 * b2 - a2 * b1;
  return [(c1 * b2 - c2 * b1) / det, (a1 * c2 - a2 * c1) / det];
}

/**
 * 復元係数。欠損錐体 i を残る 2 錐体 (j, k) から x*j + y*k で復元する。
 * 拘束は「白」と「軸の原色」の 2 点が動かないこと。
 * P/D 型は青、T 型は赤を軸に取る(Viénot らが 475nm / 660nm を用いるのに対応する近似)。
 */
const ANCHORS: Record<CvdType, number[]> = {
  protan: [0, 0, 1],
  deutan: [0, 0, 1],
  tritan: [1, 0, 0],
};
const MISSING: Record<CvdType, [number, number, number]> = {
  protan: [0, 1, 2], // L ← M, S
  deutan: [1, 0, 2], // M ← L, S
  tritan: [2, 0, 1], // S ← L, M
};

const RECOVER: Record<CvdType, [number, number]> = Object.fromEntries(
  CVD_TYPES.map((type) => {
    const [i, j, k] = MISSING[type];
    const white = apply(RGB_TO_LMS, [1, 1, 1]);
    const anchor = apply(RGB_TO_LMS, ANCHORS[type]);
    return [type, solve2([white[j], white[k], white[i]], [anchor[j], anchor[k], anchor[i]])];
  }),
) as Record<CvdType, [number, number]>;

function srgbToLinear(c: number): number {
  return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

function linearToSrgb(c: number): number {
  const v = c <= 0.0031308 ? c * 12.92 : 1.055 * Math.pow(c, 1 / 2.4) - 0.055;
  return Math.min(1, Math.max(0, v));
}

function parse(hex: string): number[] {
  const s = hex.replace("#", "");
  return [0, 2, 4].map((i) => parseInt(s.slice(i, i + 2), 16) / 255);
}

function format(rgb: number[]): string {
  return (
    "#" +
    rgb
      .map((c) => Math.round(c * 255).toString(16).padStart(2, "0").toUpperCase())
      .join("")
  );
}

export function simulate(hex: string, type: CvdType): string {
  const lms = apply(RGB_TO_LMS, parse(hex).map(srgbToLinear));
  const [i, j, k] = MISSING[type];
  const [x, y] = RECOVER[type];
  const out = [...lms];
  out[i] = x * lms[j] + y * lms[k];
  return format(apply(LMS_TO_RGB, out).map(linearToSrgb));
}

/** WCAG 2.x の相対輝度。 */
export function relativeLuminance(hex: string): number {
  const [r, g, b] = parse(hex).map(srgbToLinear);
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/** WCAG 2.x のコントラスト比(1〜21)。 */
export function contrastRatio(a: string, b: string): number {
  const la = relativeLuminance(a);
  const lb = relativeLuminance(b);
  const [hi, lo] = la >= lb ? [la, lb] : [lb, la];
  return (hi + 0.05) / (lo + 0.05);
}

export function wcagLevel(ratio: number): string {
  if (ratio >= 7) return "AAA";
  if (ratio >= 4.5) return "AA";
  if (ratio >= 3) return "AA（大きい文字のみ）";
  return "不足";
}
