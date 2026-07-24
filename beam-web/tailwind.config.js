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
        glow: '0 0 0 1px rgba(148, 163, 184, 0.14), 0 24px 80px rgba(15, 23, 42, 0.28)',
      },
      fontFamily: {
        sans: ['Inter', 'Segoe UI', 'system-ui', 'sans-serif'],
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
