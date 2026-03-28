import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  ...(process.env.NEXT_OUTPUT === "standalone" ? { output: "standalone" } : {}),
  turbopack: {
    root: process.cwd(),
  },
};

export default nextConfig;
