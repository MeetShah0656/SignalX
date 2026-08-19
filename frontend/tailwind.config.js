/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0B0E14',
        surface: '#151921',
        card: '#1C2330',
        border: '#2A3447',
        primary: '#3B82F6',
        success: '#10B981',
        danger: '#EF4444',
        warning: '#F59E0B',
        accent: '#8B5CF6',
        textMuted: '#94A3B8'
      },
    },
  },
  plugins: [],
};
