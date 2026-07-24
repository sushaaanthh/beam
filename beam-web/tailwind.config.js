/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      boxShadow: {
        glow: '0 1px 0 rgba(255, 255, 255, 0.06) inset, 0 24px 48px rgba(0, 0, 0, 0.38)',
      },
      fontFamily: {
        sans: ['Geist', 'Inter', 'Segoe UI', 'system-ui', 'sans-serif'],
      },
      colors: {
        beam: {
          950: '#060b16',
          900: '#0b1220',
          800: '#111a2e',
          700: '#1b2943',
          600: '#27375b',
          500: '#3a5588',
          400: '#5f7db1',
          300: '#8ea9d2',
          200: '#c5d5ec',
          100: '#e7eefb',
          50: '#f7f9fe',
        },
      },
    },
  },
  plugins: [],
}
