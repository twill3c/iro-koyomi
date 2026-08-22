/** フッタの 5 リンク(F-12)。 */
export interface FooterLink {
  label: string;
  href: string;
}

export const FOOTER_LINKS: FooterLink[] = [
  { label: "MIT License", href: "https://github.com/twill3c/iro-koyomi/blob/main/LICENSE" },
  { label: "GitHub", href: "https://github.com/twill3c/iro-koyomi" },
  { label: "操作説明", href: "/about/" },
  { label: "設計図", href: "https://claude.ai/code/artifact/2e1f1d6f-ad7d-4df3-a8d2-0930f103235b" },
  { label: "App Menu", href: "https://app-menu-amber.vercel.app/" },
];
