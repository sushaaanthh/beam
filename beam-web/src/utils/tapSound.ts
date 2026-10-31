let audioContext: AudioContext | null = null

type WindowWithWebkitAudioContext = Window & {
  webkitAudioContext?: typeof AudioContext
}

function getAudioContext(): AudioContext | null {
  if (typeof window === 'undefined') return null
  if (audioContext) return audioContext

  const AudioContextConstructor =
    window.AudioContext ?? (window as WindowWithWebkitAudioContext).webkitAudioContext
  if (!AudioContextConstructor) return null

  audioContext = new AudioContextConstructor()
  return audioContext
}

function scheduleTap(context: AudioContext) {
  const now = context.currentTime
  const oscillator = context.createOscillator()
  const gain = context.createGain()

  oscillator.type = 'sine'
  oscillator.frequency.setValueAtTime(520, now)
  oscillator.frequency.exponentialRampToValueAtTime(260, now + 0.045)
  gain.gain.setValueAtTime(0.0001, now)
  gain.gain.exponentialRampToValueAtTime(0.045, now + 0.004)
  gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.06)

  oscillator.connect(gain)
  gain.connect(context.destination)
  oscillator.start(now)
  oscillator.stop(now + 0.065)
}

export function playTapSound() {
  const context = getAudioContext()
  if (!context) return

  if (context.state === 'suspended') {
    void context.resume().then(() => scheduleTap(context)).catch(() => {
      // Audio is optional; navigation should continue if the browser blocks it.
    })
    return
  }

  scheduleTap(context)
}
