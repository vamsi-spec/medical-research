/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class", // Add this line
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          blue: "#1e40af",
          dark: "#1e293b",
          light: "#f8fafc",
        },
        semantic: {
          success: "#10b981",
          warning: "#f59e0b",
          danger: "#ef4444",
          info: "#3b82f6",
        },
      },
    },
  },
  plugins: [],
};
