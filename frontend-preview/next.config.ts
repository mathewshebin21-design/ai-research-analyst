import type { NextConfig } from "next";

// The preview is a static, client-rendered prototype: no server, no API keys.
// PREVIEW_RELATIVE_ASSETS=1 emits ./_next/... paths so the exported folder can be
// opened from any sub-path (a static host or the hosted design preview).
const relativeAssets = process.env.PREVIEW_RELATIVE_ASSETS === "1";

const nextConfig: NextConfig = {
  output: "export",
  assetPrefix: relativeAssets ? "." : undefined,
  images: { unoptimized: true },
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
