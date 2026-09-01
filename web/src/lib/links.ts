/** フッタの 5 リンク(F-12)。 */
export interface FooterLink {
  label: string;
  href: string;
}

// 著作権表示はリンクの文言に含めず、MIT License の直後の地の文にする(規約の一部)。
export const FOOTER_NOTICE = "© 2026 坂田哲朗";

export const FOOTER_LINKS: FooterLink[] = [
  { label: "MIT License", href: "https://github.com/twill3c/iro-koyomi/blob/main/LICENSE" },
  { label: "GitHub", href: "https://github.com/twill3c/iro-koyomi" },
  {
    label: "色暦の読み方",
    href: "https://claude.ai/code/artifact/23ce7348-34b7-4398-a489-555bdae27055",
  },
  { label: "色暦設計図", href: "https://claude.ai/code/artifact/2e1f1d6f-ad7d-4df3-a8d2-0930f103235b" },
  { label: "App Menu", href: "https://app-menu-amber.vercel.app/" },
];
