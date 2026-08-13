import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // ── Paleta oficial UCC ─────────────────────────────────────────────
        ucc: {
          green:     "#6AB023", // Verde vibrante (U del logo)
          blue:      "#00AEEF", // Azul cielo (C del logo)
          lime:      "#B5D334", // Verde lima (arco exterior)
          navy:      "#1E3A5F", // Azul oscuro (texto UCC)
          cyan:      "#00BCD4", // Cyan (punto del arco)
        },
        // ── Mint (mantener para compatibilidad con componentes existentes) ──
        mint: {
          pastel:  "#C1EBDD",
          solid:   "#00AEEF", // Reemplazado por azul UCC
          premium: "#6AB023", // Reemplazado por verde UCC
        },
        coral: {
          soft: "#FADBD8",
        },
        softWhite: "#FDFDFD",
        lightGray: "#F3F4F6",
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
        // Gradiente UCC para fondos
        "ucc-gradient": "linear-gradient(135deg, #00AEEF 0%, #6AB023 100%)",
      },
    },
  },
  plugins: [],
};
export default config;
