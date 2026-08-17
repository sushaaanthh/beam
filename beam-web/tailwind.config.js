/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['Oswald', 'sans-serif'],
        ui: ['"Product Sans"', '"Google Sans"', 'Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        // Monochrome palette
        primaryBg: '#050505',
        secondaryBg: '#080808',
        surface: '#0D0D0D',
        elevatedSurface: '#121212',
        keycapSurface: '#161616',
        border: '#262626',
        subtleBorder: '#1C1C1C',
        // Text colors
        textPrimary: '#F5F5F0',
        textSecondary: '#B8B8B0',
        textMuted: '#73736F',
        // Accent (lime)
        accent: '#C7FF4A',
        accentSubtle: '#A8D83A',
      },
      // Keycap interaction utilities
      translate: {
        'keycap-up': '-1px',
        'keycap-down': '1px',
      },
      transitionDuration: {
        keycap: '150ms',
        'keycap-slow': '180ms',
      },
      boxShadow: {
        keycap: 'inset 0 1px 2px rgba(0,0,0,0.3)',
      },
      borderRadius: {
        keycap: '6px',
      },
    },
  },
  plugins: [],
};