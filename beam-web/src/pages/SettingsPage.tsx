import { useState } from 'react'
import {
  Sliders,
  Bell,
  Lock,
  Database,
  Cpu,
  CheckCircle2,
} from 'lucide-react'

import { Button } from '../components/Button'
import { Card } from '../components/Card'

export function SettingsPage() {
  const [emailAlerts, setEmailAlerts] = useState(true)
  const [autoSaliency, setAutoSaliency] = useState(true)
  const [rawTelemetryLogging, setRawTelemetryLogging] = useState(false)
  const [defaultModel, setDefaultModel] = useState('RoBERTa-v1.2')
  const [confidenceThreshold, setConfidenceThreshold] = useState('0.85')

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="border-b border-[#1C1C1C] pb-4">
        <span className="text-[10px] font-mono text-[#C7FF4A] tracking-wider uppercase">
          WORKSPACE // CONFIGURATION
        </span>
        <h1 className="font-display text-3xl sm:text-4xl font-bold text-[#F5F5F0] tracking-tight mt-1">
          SETTINGS
        </h1>
        <p className="text-xs sm:text-sm text-[#73736F] mt-1">
          Inference parameters, explainability switches, notification filters, and telemetry preferences.
        </p>
      </div>

      <div className="space-y-6">
        {/* Analysis Preferences */}
        <Card variant="default" padding="none" className="p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-[#1C1C1C] pb-3">
            <Sliders className="h-4 w-4 text-[#C7FF4A]" />
            <h3 className="font-display text-lg font-bold text-[#F5F5F0]">
              ANALYSIS & EXPLAINABILITY PREFERENCES
            </h3>
          </div>

          <div className="space-y-4 text-xs">
            <div className="flex items-center justify-between p-3 rounded-lg bg-[#0C0C0C] border border-[#1E1E1E]">
              <div>
                <p className="font-medium text-[#F5F5F0]">Automated SHAP Attribution Computation</p>
                <p className="text-[#73736F] text-[11px]">Generate token saliency highlights automatically for every inference</p>
              </div>
              <input
                type="checkbox"
                checked={autoSaliency}
                onChange={(e) => setAutoSaliency(e.target.checked)}
                className="h-4 w-4 accent-[#C7FF4A] rounded"
              />
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-[#0C0C0C] border border-[#1E1E1E]">
              <div>
                <p className="font-medium text-[#F5F5F0]">Confidence Cutoff Filter</p>
                <p className="text-[#73736F] text-[11px]">Minimum probability threshold required for high-certainty flag</p>
              </div>
              <select
                value={confidenceThreshold}
                onChange={(e) => setConfidenceThreshold(e.target.value)}
                className="bg-[#141414] border border-[#262626] rounded px-3 py-1 text-xs text-[#F5F5F0] focus:outline-none"
              >
                <option value="0.75">0.75 (Permissive)</option>
                <option value="0.85">0.85 (Balanced Standard)</option>
                <option value="0.95">0.95 (High Strictness)</option>
              </select>
            </div>
          </div>
        </Card>

        {/* Model Preferences */}
        <Card variant="default" padding="none" className="p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-[#1C1C1C] pb-3">
            <Cpu className="h-4 w-4 text-[#C7FF4A]" />
            <h3 className="font-display text-lg font-bold text-[#F5F5F0]">
              DEFAULT TRANSFORMER ENGINE
            </h3>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 rounded-lg bg-[#0C0C0C] border border-[#1E1E1E]">
              <div>
                <p className="font-medium text-[#F5F5F0]">Primary Checkpoint</p>
                <p className="text-[#73736F] text-[11px]">Default architecture instantiated for interactive text analysis</p>
              </div>
              <select
                value={defaultModel}
                onChange={(e) => setDefaultModel(e.target.value)}
                className="bg-[#141414] border border-[#262626] rounded px-3 py-1 text-xs text-[#C7FF4A] font-mono focus:outline-none"
              >
                <option value="RoBERTa-v1.2">RoBERTa-Emotion-v1.2</option>
                <option value="BERT-Base">BERT-Base-Affective</option>
                <option value="DeBERTa-v3">DeBERTa-v3-Attention-Attribution</option>
              </select>
            </div>
          </div>
        </Card>

        {/* Notifications & Privacy */}
        <Card variant="default" padding="none" className="p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-[#1C1C1C] pb-3">
            <Bell className="h-4 w-4 text-[#C7FF4A]" />
            <h3 className="font-display text-lg font-bold text-[#F5F5F0]">
              NOTIFICATIONS & TELEMETRY
            </h3>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 rounded-lg bg-[#0C0C0C] border border-[#1E1E1E]">
              <div>
                <p className="font-medium text-[#F5F5F0]">Batch Job Notifications</p>
                <p className="text-[#73736F] text-[11px]">Receive summary reports when batch dataset ingestion completes</p>
              </div>
              <input
                type="checkbox"
                checked={emailAlerts}
                onChange={(e) => setEmailAlerts(e.target.checked)}
                className="h-4 w-4 accent-[#C7FF4A] rounded"
              />
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-[#0C0C0C] border border-[#1E1E1E]">
              <div>
                <p className="font-medium text-[#F5F5F0]">Raw Telemetry Persistent Logging</p>
                <p className="text-[#73736F] text-[11px]">Retain full token tensors in database archive for offline audit</p>
              </div>
              <input
                type="checkbox"
                checked={rawTelemetryLogging}
                onChange={(e) => setRawTelemetryLogging(e.target.checked)}
                className="h-4 w-4 accent-[#C7FF4A] rounded"
              />
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}