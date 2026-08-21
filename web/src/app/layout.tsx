import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "色暦 — 日本の伝統色と俳句",
  description:
    "日本の伝統色 369 色を、出典ごとに食い違うカラーコードと、その色に結びつく俳句とともに歳時記順に並べる。",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
