import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        fiscal: {
          50: "#eff6ff",
          500: "#1d4ed8",
          700: "#1e3a8a"
        }
      }
    }
  },
  plugins: []
};

export default config;

