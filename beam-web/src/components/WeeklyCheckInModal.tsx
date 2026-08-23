import { useState } from 'react'
import { X, Sparkles, CheckCircle2, HeartPulse, Sliders } from 'lucide-react'
import { Button } from './Button'
import { Card } from './Card'
import { beamApi, WellnessMetrics } from '../services/api/beam'

interface WeeklyCheckInModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: (metrics: WellnessMetrics) => void
}

export function WeeklyCheckInModal({ isOpen, onClose, onSuccess }: WeeklyCheckInModalProps) {
  const [energy, setEnergy] = useState(8)
  const [stress, setStress] = useState(3)
  const [motivation, setMotivation] = useState(8)
  const [sleep, setSleep] = useState(7)
  const [reflection, setReflection] = useState('')
  const [loading, setLoading] = useState(false)

  if (!isOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await beamApi.submitCheckIn({
        energy_level: energy,
        stress_level: stress,
        motivation_level: motivation,
        sleep_quality: sleep,
        free_text_reflection: reflection,
      })
      if (res.metrics) {
        onSuccess(res.metrics)
      }
      onClose()
    } catch {
      onClose()
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-lg rounded-2xl bg-[#0A0A0A] border border-[#222222] shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-[#1C1C1C] flex items-center justify-between bg-[#0E0E0E]">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-[#C7FF4A]/10 border border-[#C7FF4A]/30 flex items-center justify-center text-[#C7FF4A]">
              <HeartPulse className="h-5 w-5" />
            </div>
            <div>
              <h2 className="font-display text-lg font-bold text-[#F5F5F0]">
                Weekly Wellness Check-in
              </h2>
              <p className="text-xs text-[#73736F]">
                Calibrate your longitudinal affective wellness score
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#73736F] hover:text-white hover:bg-[#181818] transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {/* Sliders */}
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs font-mono mb-1.5">
                <span className="text-[#B8B8B0]">Energy & Vitality</span>
                <span className="text-[#C7FF4A] font-bold">{energy} / 10</span>
              </div>
              <input
                type="range"
                min={1}
                max={10}
                value={energy}
                onChange={(e) => setEnergy(Number(e.target.value))}
                className="w-full accent-[#C7FF4A] cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono mb-1.5">
                <span className="text-[#B8B8B0]">Stress & Autonomic Load</span>
                <span className="text-[#FF6B6B] font-bold">{stress} / 10</span>
              </div>
              <input
                type="range"
                min={1}
                max={10}
                value={stress}
                onChange={(e) => setStress(Number(e.target.value))}
                className="w-full accent-[#FF6B6B] cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono mb-1.5">
                <span className="text-[#B8B8B0]">Motivation & Drive</span>
                <span className="text-[#C7FF4A] font-bold">{motivation} / 10</span>
              </div>
              <input
                type="range"
                min={1}
                max={10}
                value={motivation}
                onChange={(e) => setMotivation(Number(e.target.value))}
                className="w-full accent-[#C7FF4A] cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono mb-1.5">
                <span className="text-[#B8B8B0]">Sleep Quality</span>
                <span className="text-[#C7FF4A] font-bold">{sleep} / 10</span>
              </div>
              <input
                type="range"
                min={1}
                max={10}
                value={sleep}
                onChange={(e) => setSleep(Number(e.target.value))}
                className="w-full accent-[#C7FF4A] cursor-pointer"
              />
            </div>
          </div>

          {/* Free-text Reflection */}
          <div>
            <label className="text-xs font-mono text-[#73736F] uppercase block mb-1.5">
              Free-form Reflection (Optional NLP Analysis)
            </label>
            <textarea
              rows={3}
              value={reflection}
              onChange={(e) => setReflection(e.target.value)}
              placeholder="How would you summarize your overall cognitive and emotional trajectory this week?"
              className="w-full rounded-lg bg-[#080808] border border-[#1E1E1E] p-3 text-xs text-[#F5F5F0] placeholder:text-[#444440] focus:border-[#C7FF4A] focus:outline-none"
            />
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#1C1C1C]">
            <Button variant="ghost" size="sm" type="button" onClick={onClose}>
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              type="submit"
              isLoading={loading}
              leftIcon={<Sparkles className="h-3.5 w-3.5" />}
            >
              Compute Wellness Score
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
