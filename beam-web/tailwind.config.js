/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['SF Pro Display', '-apple-system', 'BlinkMacSystemFont', 'Geist', 'Inter', 'Segoe UI', 'system-ui', 'sans-serif'],
        mono: ['SF Mono', 'Monaco', 'Menlo', 'Consolas', 'monospace'],
      },
      colors: {
        // Apple-inspired color system
        apple: {
          // Base neutrals - deep space black
          bg: '#000000',
          bgElevated: '#0d0d0d',
          bgCard: '#1a1a1a',
          bgCardHover: '#232323',
          border: '#2d2d2d',
          borderHover: '#3a3a3a',

          // Text
          textPrimary: '#ffffff',
          textSecondary: '#8e8e93',
          textTertiary: '#6e6e73',
          textQuaternary: '#48484a',

          // Accent - Apple Blue
          accent: '#007aff',
          accentHover: '#0056cc',
          accentLight: '#4da6ff',
          accentSoft: 'rgba(0, 122, 255, 0.1)',

          // Semantic
          success: '#30d158',
          successSoft: 'rgba(48, 209, 88, 0.1)',
          warning: '#ff9f0a',
          warningSoft: 'rgba(255, 159, 10, 0.1)',
          danger: '#ff453a',
          dangerSoft: 'rgba(255, 69, 58, 0.1)',

          // Glass
          glass: 'rgba(255, 255, 255, 0.04)',
          glassStrong: 'rgba(255, 255, 255, 0.08)',
          glassBorder: 'rgba(255, 255, 255, 0.1)',
          glassBorderStrong: 'rgba(255, 255, 255, 0.15)',
        },
      },
      boxShadow: {
        // Apple-style shadows with depth
        'apple-sm': '0 1px 2px rgba(0, 0, 0, 0.4), 0 1px 0 rgba(255, 255, 255, 0.05) inset',
        'apple-md': '0 4px 16px rgba(0, 0, 0, 0.5), 0 1px 0 rgba(255, 255, 255, 0.05) inset',
        'apple-lg': '0 12px 40px rgba(0, 0, 0, 0.6), 0 1px 0 rgba(255, 255, 255, 0.05) inset',
        'apple-xl': '0 24px 64px rgba(0, 0, 0, 0.7), 0 1px 0 rgba(255, 255, 255, 0.05) inset',
        'apple-inner': 'inset 0 1px 0 rgba(255, 255, 255, 0.1), inset 0 -1px 0 rgba(0, 0, 0, 0.3)',
        'apple-glow': '0 0 0 1px rgba(255, 255, 255, 0.05), 0 8px 32px rgba(0, 0, 0, 0.5)',
        'accent-glow': '0 0 0 1px rgba(0, 122, 255, 0.3), 0 0 24px rgba(0, 122, 255, 0.15)',
      },
      borderRadius: {
        'apple-sm': '8px',
        'apple-md': '12px',
        'apple-lg': '16px',
        'apple-xl': '24px',
        'apple-2xl': '32px',
        'apple-full': '9999px',
      },
      transitionTimingFunction: {
        'apple': 'cubic-bezier(0.4, 0, 0.2, 1)',
        'apple-spring': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
      },
      transitionDuration: {
        'apple-fast': '120ms',
        'apple-normal': '200ms',
        'apple-slow': '300ms',
        'apple-slower': '500ms',
      },
      backdropBlur: {
        'apple': '20px',
        'apple-strong': '40px',
      },
      backgroundImage: {
        'apple-gradient-radial': 'radial-gradient(ellipse at center, rgba(0, 122, 255, 0.08) 0%, transparent 70%)',
        'apple-gradient-mesh': 'linear-gradient(135deg, rgba(0, 122, 255, 0.03) 0%, transparent 50%), radial-gradient(ellipse at 80% 20%, rgba(48, 209, 88, 0.04) 0%, transparent 50%)',
        'apple-noise': "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E\")",
      },
      fontSize: {
        'display-4xl': ['5.5rem', { lineHeight: '1.05', letterSpacing: '-0.03em', fontWeight: '600' }],
        'display-3xl': ['4.5rem', { lineHeight: '1.08', letterSpacing: '-0.02em', fontWeight: '600' }],
        'display-2xl': ['3.5rem', { lineHeight: '1.1', letterSpacing: '-0.02em', fontWeight: '600' }],
        'display-xl': ['2.75rem', { lineHeight: '1.15', letterSpacing: '-0.015em', fontWeight: '600' }],
        'display-lg': ['2.25rem', { lineHeight: '1.2', letterSpacing: '-0.01em', fontWeight: '600' }],
        'display-md': ['1.75rem', { lineHeight: '1.25', letterSpacing: '-0.005em', fontWeight: '600' }],
        'display-sm': ['1.5rem', { lineHeight: '1.3', fontWeight: '600' }],
        'heading-xl': ['1.25rem', { lineHeight: '1.4', fontWeight: '600' }],
        'heading-lg': ['1.125rem', { lineHeight: '1.4', fontWeight: '600' }],
        'heading-md': ['1rem', { lineHeight: '1.45', fontWeight: '600' }],
        'heading-sm': ['0.875rem', { lineHeight: '1.5', fontWeight: '600' }],
        'body-xl': ['1.125rem', { lineHeight: '1.55', fontWeight: '400' }],
        'body-lg': ['1rem', { lineHeight: '1.55', fontWeight: '400' }],
        'body-md': ['0.875rem', { lineHeight: '1.55', fontWeight: '400' }],
        'body-sm': ['0.8125rem', { lineHeight: '1.5', fontWeight: '400' }],
        'caption-lg': ['0.75rem', { lineHeight: '1.5', fontWeight: '400' }],
        'caption-md': ['0.6875rem', { lineHeight: '1.5', fontWeight: '400' }],
        'caption-sm': ['0.625rem', { lineHeight: '1.5', fontWeight: '400' }],
      },
      spacing: {
        'apple-1': '4px',
        'apple-2': '8px',
        'apple-3': '12px',
        'apple-4': '16px',
        'apple-5': '20px',
        'apple-6': '24px',
        'apple-7': '28px',
        'apple-8': '32px',
        'apple-9': '36px',
        'apple-10': '40px',
        'apple-12': '48px',
        'apple-14': '56px',
        'apple-16': '64px',
        'apple-20': '80px',
        'apple-24': '96px',
        'apple-32': '128px',
      },
      animation: {
        'apple-fade-in': 'appleFadeIn 200ms cubic-bezier(0.4, 0, 0.2, 1) forwards',
        'apple-slide-up': 'appleSlideUp 300ms cubic-bezier(0.4, 0, 0.2, 1) forwards',
        'apple-slide-down': 'appleSlideDown 300ms cubic-bezier(0.4, 0, 0.2, 1) forwards',
        'apple-scale-in': 'appleScaleIn 200ms cubic-bezier(0.34, 1.56, 0.64, 1) forwards',
        'apple-shimmer': 'appleShimmer 2s ease-in-out infinite',
        'apple-pulse-soft': 'applePulseSoft 3s ease-in-out infinite',
      },
      keyframes: {
        appleFadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        appleSlideUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        appleSlideDown: {
          '0%': { opacity: '0', transform: 'translateY(-16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        appleScaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        appleShimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        applePulseSoft: {
          '0%, 100%': { opacity: '0.6' },
          '50%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}