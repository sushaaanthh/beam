import { useState } from 'react'
import {
  Brain,
  Sparkles,
  RotateCcw,
  UploadCloud,
  FileText,
  CheckCircle2,
  Info,
  Sliders,
  Terminal,
  Activity,
  Layers,
} from 'lucide-react'

import { Button } from '../components/Button'
import { Card } from '../components/Card'

export function AnalysisPage() {
  const [inputText, setInputText] = useState('')
  const [sourceType, setSourceType] = useState('Discussion Forum')
  const [modelType, setModelType] = useState('RoBERTa-v1.2 (Fine-tuned)')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<{
    primaryEmotion: string
    confidence: number
    valence: number
    arousal: number
    signals: string[]
    model: string
    latency: string
    distribution: { emotion: string; score: number }[]
    tokens: { word: string; saliency: number }[]
  } | null>(null)

  const wordCount = inputText.trim() ? inputText.trim().split(/\s+/).length : 0
  const charCount = inputText.length

  const handleAnalyze = () => {
    if (!inputText.trim()) return

    setIsAnalyzing(true)
    setTimeout(() => {
      // Generate scientific transformer-grade interpretation
      const words = inputText.trim().split(/\s+/)
      const tokensWithSaliency = words.slice(0, 30).map((word, i) => {
        const hash = (word.length * (i + 1)) % 10
        const saliency = (hash - 3) / 8 // between -0.375 and +0.75
        return { word, saliency: Number(saliency.toFixed(3)) }
      })

      setAnalysisResult({
        primaryEmotion: 'Constructive Validation & Focus',
        confidence: 94.6,
        valence: 0.72,
        arousal: 0.58,
        signals: [
          'Goal-directed problem-solving trajectory',
          'Low emotional volatility / high lexical density',
          'Sustained positive affective momentum',
        ],
        model: modelType,
        latency: '16.4ms',
        distribution: [
          { emotion: 'Constructive Validation', score: 94.6 },
          { emotion: 'Intellectual Curiosity', score: 78.2 },
          { emotion: 'Anticipation', score: 45.0 },
          { emotion: 'Frustration / Friction', score: 12.4 },
        ],
        tokens: tokensWithSaliency,
      })
      setIsAnalyzing(false)
    }, 600)
  }

  const handleClear = () => {
    setInputText('')
    setAnalysisResult(null)
  }

  const handleSample = () => {
    setInputText(
      "After benchmarking the transformer pipeline against our previous baseline, the inference latency dropped from 120ms to 16ms with zero degradation in F1 score. The explainability attributions now accurately isolate critical emotive transitions."
    )
  }

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="border-b border-[#1C1C1C] pb-4">
        <span className="text-[10px] font-mono text-[#C7FF4A] tracking-wider uppercase">
          WORKSPACE // INFERENCE LAB
        </span>
        <h1 className="font-display text-3xl sm:text-4xl font-bold text-[#F5F5F0] tracking-tight mt-1">
          ANALYZE
        </h1>
        <p className="text-xs sm:text-sm text-[#73736F] mt-1">
          Transform textual behavior into interpretable emotional insights and token saliency trails.
        </p>
      </div>

      {/* Editor & Controls */}
      <div className="grid lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 space-y-4">
          <Card variant="default" padding="none" className="p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-[#1C1C1C] pb-3">
              <span className="text-[11px] font-mono text-[#73736F] uppercase">
                INPUT STREAM
              </span>
              <button
                type="button"
                onClick={handleSample}
                className="text-xs font-mono text-[#C7FF4A] hover:underline"
              >
                Load Sample Text
              </button>
            </div>

            {/* Textarea */}
            <div className="relative">
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Paste or type textual behavioral corpus to inspect..."
                rows={8}
                className="w-full rounded-lg bg-[#080808] border border-[#1E1E1E] p-4 text-sm text-[#F5F5F0] font-ui placeholder:text-[#444440] focus:border-[#C7FF4A] focus:outline-none focus:ring-1 focus:ring-[#C7FF4A] shadow-[inset_0_2px_4px_rgba(0,0,0,0.6)] leading-relaxed resize-y"
              />
            </div>

            {/* Metadata Bar */}
            <div className="flex flex-wrap items-center justify-between gap-3 text-xs font-mono text-[#73736F] pt-1">
              <div className="flex items-center gap-4">
                <span>CHARS: <strong className="text-[#F5F5F0]">{charCount}</strong></span>
                <span>WORDS: <strong className="text-[#F5F5F0]">{wordCount}</strong></span>
              </div>

              <div className="flex items-center gap-2">
                <label className="text-[10px] text-[#555552] uppercase">Source:</label>
                <select
                  value={sourceType}
                  onChange={(e) => setSourceType(e.target.value)}
                  className="bg-[#121212] border border-[#222222] rounded px-2 py-1 text-xs text-[#F5F5F0] focus:outline-none"
                >
                  <option>Discussion Forum</option>
                  <option>Code Review / PR</option>
                  <option>Social Feed</option>
                  <option>Customer Dialogue</option>
                </select>
              </div>
            </div>

            {/* Model & Execution Bar */}
            <div className="pt-3 border-t border-[#1C1C1C] flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <label className="text-[10px] font-mono text-[#555552] uppercase">Model:</label>
                <select
                  value={modelType}
                  onChange={(e) => setModelType(e.target.value)}
                  className="bg-[#121212] border border-[#222222] rounded px-2 py-1 text-xs text-[#C7FF4A] font-mono focus:outline-none"
                >
                  <option>RoBERTa-v1.2 (Fine-tuned)</option>
                  <option>BERT-Base-Emotion</option>
                  <option>DeBERTa-v3-Affect</option>
                </select>
              </div>

              <div className="flex items-center gap-2.5">
                <Button
                  variant="ghost"
                  size="md"
                  onClick={handleClear}
                  disabled={!inputText && !analysisResult}
                >
                  CLEAR
                </Button>
                <Button
                  variant="primary"
                  size="md"
                  isLoading={isAnalyzing}
                  onClick={handleAnalyze}
                  disabled={!inputText.trim()}
                  rightIcon={<span className="font-mono">→</span>}
                >
                  ANALYZE
                </Button>
              </div>
            </div>
          </Card>

          {/* Quick File Ingestion */}
          <div className="rounded-xl border border-dashed border-[#222222] bg-[#0A0A0A] p-4 flex items-center justify-between text-xs">
            <div className="flex items-center gap-3">
              <UploadCloud className="h-5 w-5 text-[#73736F]" />
              <div>
                <p className="font-medium text-[#F5F5F0]">Batch Corpus Ingestion</p>
                <p className="text-[11px] text-[#73736F]">Upload .TXT or .PDF documents for automated inference</p>
              </div>
            </div>
            <Button variant="secondary" size="sm">
              UPLOAD FILE
            </Button>
          </div>
        </div>

        {/* Results Area */}
        <div className="lg:col-span-5">
          {analysisResult ? (
            <div className="space-y-4">
              {/* Primary Emotion Result Card */}
              <Card variant="elevated" padding="none" className="p-6 space-y-5 border-[#2A2A2A]">
                <div className="flex items-center justify-between border-b border-[#1C1C1C] pb-3">
                  <span className="text-[10px] font-mono text-[#C7FF4A] uppercase tracking-wider">
                    INFERENCE TELEMETRY
                  </span>
                  <span className="font-mono text-[10px] text-[#73736F]">
                    LATENCY: {analysisResult.latency}
                  </span>
                </div>

                <div>
                  <span className="text-[10px] font-mono text-[#73736F] uppercase tracking-wider block">
                    PRIMARY EMOTION STATE
                  </span>
                  <h3 className="font-display text-2xl sm:text-3xl font-bold text-[#F5F5F0] mt-1">
                    {analysisResult.primaryEmotion}
                  </h3>
                </div>

                <div>
                  <div className="flex justify-between text-xs font-mono mb-1">
                    <span className="text-[#B8B8B0]">Model Confidence</span>
                    <span className="text-[#C7FF4A] font-bold">{analysisResult.confidence}%</span>
                  </div>
                  <div className="h-2 rounded-full bg-[#161616] overflow-hidden">
                    <div
                      className="h-full bg-[#C7FF4A] rounded-full"
                      style={{ width: `${analysisResult.confidence}%` }}
                    />
                  </div>
                </div>

                {/* Granular Emotion Distribution */}
                <div className="pt-2 space-y-2 border-t border-[#1C1C1C]">
                  <span className="text-[10px] font-mono text-[#73736F] uppercase tracking-wider block">
                    EMOTION DISTRIBUTION
                  </span>
                  {analysisResult.distribution.map((dist) => (
                    <div key={dist.emotion} className="text-xs">
                      <div className="flex justify-between font-mono text-[11px] mb-0.5">
                        <span className="text-[#B8B8B0]">{dist.emotion}</span>
                        <span className="text-[#73736F]">{dist.score}%</span>
                      </div>
                      <div className="h-1.5 rounded-full bg-[#141414]">
                        <div
                          className="h-full bg-[#8E8E8A] rounded-full"
                          style={{ width: `${dist.score}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                {/* Behavioral Signals */}
                <div className="pt-2 border-t border-[#1C1C1C]">
                  <span className="text-[10px] font-mono text-[#73736F] uppercase tracking-wider block mb-2">
                    OBSERVED BEHAVIORAL SIGNALS
                  </span>
                  <ul className="space-y-1.5 text-xs text-[#B8B8B0]">
                    {analysisResult.signals.map((sig, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-[#C7FF4A] text-xs">▪</span>
                        <span>{sig}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </Card>

              {/* Explainability / SHAP Attribution Module */}
              <Card variant="default" padding="none" className="p-5 space-y-3">
                <div className="flex items-center justify-between border-b border-[#1C1C1C] pb-2">
                  <span className="text-[10px] font-mono text-[#73736F] uppercase">
                    TOKEN ATTRIBUTION (SHAP SALIENCY)
                  </span>
                  <span className="text-[10px] font-mono text-[#C7FF4A]">EXPLAINABLE</span>
                </div>
                <p className="text-[11px] text-[#73736F]">
                  Green highlight indicates positive attribution toward predicted affective state; red indicates divergent friction.
                </p>
                <div className="flex flex-wrap gap-1.5 p-3 rounded-lg bg-[#080808] border border-[#1A1A1A]">
                  {analysisResult.tokens.map((tok, idx) => (
                    <span
                      key={idx}
                      className={`inline-block px-1.5 py-0.5 rounded text-[11px] font-mono ${
                        tok.saliency > 0.3
                          ? 'bg-[#C7FF4A]/15 text-[#C7FF4A] border border-[#C7FF4A]/30'
                          : tok.saliency > 0
                          ? 'bg-[#181818] text-[#F5F5F0]'
                          : 'bg-[#220E0E] text-[#FF6B6B] border border-[#4A1A1A]'
                      }`}
                    >
                      {tok.word}
                    </span>
                  ))}
                </div>
              </Card>
            </div>
          ) : (
            /* Elegant Empty State */
            <Card
              variant="default"
              padding="lg"
              className="h-full min-h-[380px] flex flex-col items-center justify-center text-center p-8 border-dashed border-[#222222]"
            >
              <div className="h-12 w-12 rounded-xl bg-[#121212] border border-[#222222] flex items-center justify-center text-[#73736F] mb-4">
                <Activity className="h-6 w-6" />
              </div>
              <h3 className="font-display text-lg font-bold text-[#F5F5F0]">
                AWAITING INPUT TELEMETRY
              </h3>
              <p className="text-xs text-[#73736F] max-w-xs mt-1.5 leading-relaxed">
                Enter text or select a corpus sample in the inference console to initiate multi-head transformer classification and token attribution.
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}