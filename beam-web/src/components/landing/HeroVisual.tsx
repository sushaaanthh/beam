import { useEffect, useRef } from 'react'
import { colors, fonts } from '../../design/tokens'

type Particle = {
  x: number
  y: number
  vx: number
  baseY: number
  amplitude: number
  frequency: number
  phase: number
  lime: boolean
  radius: number
}

const PARTICLE_COUNT = 56
const LINK_DISTANCE = 90
const LIME_RATIO = 0.18

function createParticle(width: number, height: number): Particle {
  const y = height * (0.2 + Math.random() * 0.6)
  return {
    x: Math.random() * width,
    y,
    baseY: y,
    vx: 0.12 + Math.random() * 0.3,
    amplitude: height * (0.04 + Math.random() * 0.1),
    frequency: 0.4 + Math.random() * 1.1,
    phase: Math.random() * Math.PI * 2,
    lime: Math.random() < LIME_RATIO,
    radius: 1 + Math.random() * 1.6,
  }
}

/**
 * Abstract signal-matrix visualisation:
 * textual signals (particles), behavioral patterns (drift paths),
 * transformer processing (link mesh), emotional states (lime peaks).
 * Lightweight canvas — no libraries, paused off-screen, static when
 * prefers-reduced-motion is set.
 */
export function HeroVisual() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const frameRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    const frame = frameRef.current
    if (!canvas || !frame) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

    let particles: Particle[] = []
    let width = 0
    let height = 0
    let rafId = 0
    let running = true
    let time = 0

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2)
      const rect = frame.getBoundingClientRect()
      width = rect.width
      height = rect.height
      canvas.width = Math.round(width * dpr)
      canvas.height = Math.round(height * dpr)
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      particles = Array.from({ length: PARTICLE_COUNT }, () => createParticle(width, height))
    }

    const drawGrid = () => {
      const step = 28
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)'
      ctx.lineWidth = 1
      ctx.beginPath()
      for (let x = step; x < width; x += step) {
        ctx.moveTo(x, 0)
        ctx.lineTo(x, height)
      }
      for (let y = step; y < height; y += step) {
        ctx.moveTo(0, y)
        ctx.lineTo(width, y)
      }
      ctx.stroke()
    }

    const drawWaves = () => {
      // Thin baseline signals — one restrained lime carrier wave.
      const waves = [
        { yRatio: 0.32, color: 'rgba(184, 184, 176, 0.16)', amp: height * 0.05, freq: 1.4 },
        { yRatio: 0.52, color: 'rgba(115, 115, 111, 0.22)', amp: height * 0.07, freq: 1.0 },
        { yRatio: 0.72, color: 'rgba(199, 255, 74, 0.30)', amp: height * 0.09, freq: 1.8 },
      ]
      for (const wave of waves) {
        ctx.strokeStyle = wave.color
        ctx.lineWidth = wave.color.includes('199') ? 1.5 : 1
        ctx.beginPath()
        const yBase = height * wave.yRatio
        for (let x = 0; x <= width; x += 4) {
          const y =
            yBase +
            Math.sin((x / width) * Math.PI * 2 * wave.freq + time * 0.5 + wave.yRatio * 6) *
              wave.amp
          if (x === 0) ctx.moveTo(x, y)
          else ctx.lineTo(x, y)
        }
        ctx.stroke()
      }
    }

    const drawParticlesAndLinks = () => {
      // Link mesh — transformer attention metaphor.
      ctx.lineWidth = 1
      for (let i = 0; i < particles.length; i++) {
        const a = particles[i]
        if (!a) continue
        for (let j = i + 1; j < particles.length; j++) {
          const b = particles[j]
          if (!b) continue
          const dx = a.x - b.x
          const dy = a.y - b.y
          const dist = Math.hypot(dx, dy)
          if (dist < LINK_DISTANCE) {
            const alpha = (1 - dist / LINK_DISTANCE) * 0.14
            ctx.strokeStyle =
              a.lime || b.lime
                ? `rgba(199, 255, 74, ${alpha * 1.6})`
                : `rgba(184, 184, 176, ${alpha})`
            ctx.beginPath()
            ctx.moveTo(a.x, a.y)
            ctx.lineTo(b.x, b.y)
            ctx.stroke()
          }
        }
      }

      for (const p of particles) {
        ctx.fillStyle = p.lime ? colors.lime : 'rgba(184, 184, 176, 0.55)'
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2)
        ctx.fill()

        if (p.lime) {
          ctx.strokeStyle = 'rgba(199, 255, 74, 0.35)'
          ctx.beginPath()
          ctx.arc(p.x, p.y, p.radius + 3.5, 0, Math.PI * 2)
          ctx.stroke()
        }
      }
    }

    const step = () => {
      time += 0.016
      ctx.clearRect(0, 0, width, height)

      drawGrid()
      drawWaves()

      for (const p of particles) {
        p.x += p.vx
        p.y = p.baseY + Math.sin(time * p.frequency + p.phase) * p.amplitude
        if (p.x - p.radius > width) {
          p.x = -p.radius
          p.baseY = height * (0.2 + Math.random() * 0.6)
        }
      }
      drawParticlesAndLinks()

      if (running && !reducedMotion) rafId = requestAnimationFrame(step)
    }

    const renderStatic = () => {
      drawGrid()
      drawWaves()
      drawParticlesAndLinks()
    }

    resize()

    const resizeObserver = new ResizeObserver(() => {
      resize()
      if (reducedMotion) renderStatic()
    })
    resizeObserver.observe(frame)

    if (reducedMotion) {
      renderStatic()
    } else {
      const intersectionObserver = new IntersectionObserver((entries) => {
        const visible = entries[0]?.isIntersecting ?? false
        if (visible && !running) {
          running = true
          rafId = requestAnimationFrame(step)
        } else if (!visible && running) {
          running = false
          cancelAnimationFrame(rafId)
        }
      })
      intersectionObserver.observe(frame)
      rafId = requestAnimationFrame(step)

      return () => {
        running = false
        cancelAnimationFrame(rafId)
        resizeObserver.disconnect()
        intersectionObserver.disconnect()
      }
    }

    return () => {
      running = false
      cancelAnimationFrame(rafId)
      resizeObserver.disconnect()
    }
  }, [])

  return (
    <div className="kc-panel overflow-hidden" role="img"
      aria-label="Abstract visualization of textual signal particles flowing through transformer layers with highlighted emotional state peaks"
    >
      {/* Frame header */}
      <div className="flex items-center justify-between border-b border-line-subtle px-5 py-3.5">
        <span className="text-[10px] font-medium uppercase tracking-[0.2em] text-dim">
          SIGNAL MATRIX
        </span>
        <span className="inline-flex items-center gap-1.5 text-[10px] font-medium uppercase tracking-[0.16em] text-lime">
          <span className="h-1 w-1 rounded-full bg-lime beam-pulse" aria-hidden="true" />
          Live Feed
        </span>
      </div>

      {/* Canvas stage */}
      <div ref={frameRef} className="relative h-64 bg-base sm:h-72 lg:h-[300px]">
        <canvas ref={canvasRef} className="absolute inset-0 h-full w-full" aria-hidden="true" />
        <div
          className="pointer-events-none absolute inset-x-0 bottom-0 flex items-center justify-between px-5 pb-3 text-[10px] tracking-[0.12em] text-dim"
          style={{ fontFamily: fonts.ui }}
        >
          <span>CH_01 · VALENCE</span>
          <span className="text-lime">CONF 0.942</span>
        </div>
      </div>

      {/* Channel readouts */}
      <div className="grid grid-cols-3 divide-x divide-line-subtle border-t border-line-subtle text-center">
        {[
          { label: 'Tokens / s', value: '142.8' },
          { label: 'Latency', value: '14.2ms' },
          { label: 'Layers', value: '12' },
        ].map((stat) => (
          <div key={stat.label} className="px-3 py-3">
            <p className="font-display text-sm font-semibold text-chalk">{stat.value}</p>
            <p className="mt-0.5 text-[9px] font-medium uppercase tracking-[0.18em] text-dim">
              {stat.label}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}
