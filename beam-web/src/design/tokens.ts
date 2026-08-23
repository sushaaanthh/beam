/**
 * B.E.A.M. design tokens — programmatic mirror of the CSS token layer
 * (src/index.css @theme). Components should prefer the generated Tailwind
 * utilities / .kc classes; use these values when JS/Canvas needs raw tokens.
 */

export const colors = {
  base: '#050505',
  deep: '#080808',
  surface: '#0D0D0D',
  raised: '#121212',
  keycap: '#161616',
  line: '#262626',
  lineSubtle: '#1C1C1C',
  chalk: '#F5F5F0',
  mist: '#B8B8B0',
  dim: '#73736F',
  lime: '#C7FF4A',
} as const

export const fonts = {
  display: '"Oswald", "Arial Narrow", "Segoe UI", sans-serif',
  ui: '"Product Sans", "Google Sans", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
} as const

export const radii = {
  keycap: '7px',
  module: '12px',
  panel: '18px',
} as const

export const spacing = {
  unit: 4,
  sectionY: 96,
  sectionYLg: 128,
} as const

export const transitions = {
  durationTactile: 160,
  easeTactile: 'cubic-bezier(0.2, 0.8, 0.2, 1)',
} as const

/** Keycap travel in px */
export const keycapDepth = {
  lift: -1,
  press: 1,
} as const
