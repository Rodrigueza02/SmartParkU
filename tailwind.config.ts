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
        mint: {
          pastel: "#C1EBDD", // Suave verde menta pastel
          solid: "#70C1B3",  // Verde menta más sólido para el botón
          premium: "#A3E4D7", // Verde menta premium para App Móvil
        },
        coral: {
          soft: "#FADBD8",   // Rojo coral suave para ocupado
        },
        softWhite: "#FDFDFD",
        lightGray: "#F3F4F6",
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
    },
  },
  plugins: [],
};
export default config;
