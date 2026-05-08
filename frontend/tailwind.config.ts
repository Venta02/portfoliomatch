import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: "#0A0A0F",
          secondary: "#12121A",
          tertiary: "#1A1A24",
        },
        foreground: {
          DEFAULT: "#FAFAFA",
          muted: "#A1A1AA",
        },
        border: "#27272A",
        accent: {
          blue: "#3B82F6",
          violet: "#8B5CF6",
          emerald: "#10B981",
          amber: "#F59E0B",
          rose: "#F43F5E",
        },
      },
      fontFamily: {
        sans: ["ui-sans-serif", "system-ui", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      animation: {
        shimmer: "shimmer 2s infinite linear",
        "fade-in-up": "fade-in-up 0.4s ease-out forwards",
        "spin-slow": "spin-slow 1.5s linear infinite",
        "pulse-glow": "pulse-glow 2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
