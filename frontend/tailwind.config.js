/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: "#f8fafc",
          panel: "#ffffff",
          muted: "#f1f5f9",
        },
        line: {
          DEFAULT: "#e2e8f0",
          strong: "#cbd5e1",
        },
        ink: {
          DEFAULT: "#0f172a",
          muted: "#64748b",
          faint: "#94a3b8",
        },
        accent: {
          DEFAULT: "#1e40af",
          hover: "#1d4ed8",
        },
      },
      fontFamily: {
        sans: ['"Inter"', "system-ui", "Segoe UI", "sans-serif"],
      },
    },
  },
  plugins: [],
};
