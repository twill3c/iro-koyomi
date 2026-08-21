import type { NextConfig } from "next";

// 静的エクスポート(N-01)— サーバ API を持たず、out/ のみで動作する
const nextConfig: NextConfig = {
  output: "export",
  // Vercel の素の静的配信(framework: null)は .html クリーン URL を解決しないため
  // work/000773/index.html のディレクトリ形式で出力する(TOOL-ENV 対応・loop_005)
  trailingSlash: true,
};

export default nextConfig;
