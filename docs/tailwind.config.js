/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./data/**/*.{js,ts,jsx,tsx,json}"
  ],
  theme: {
    extend: {
      colors: {
        surface: "#0d1117",
        panel: "#111827",
        border: "#1f2937",
        accent: "#60a5fa",
        accent2: "#a78bfa"
      }
    },
  },
  plugins: [],
};

