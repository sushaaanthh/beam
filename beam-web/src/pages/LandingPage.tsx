import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Brain,
  Activity,
  Layers,
  ArrowRight,
  ShieldCheck,
  Zap,
  Sliders,
  CheckCircle2,
  Database,
  Terminal,
} from 'lucide-react'

import { Button } from '../components/Button'
import { Card } from '../components/Card'

const pipelineSteps = [
  { step: '01', title: 'COLLECT', desc: 'Ingests raw textual streams and behavioral telemetry across online discussions.' },
  { step: '02', title: 'CLEAN', desc: 'Applies rigorous token cleaning, de-identification, and noise filtering.' },
  { step: '03', title: 'ANALYZE', desc: 'Extracts deep semantic embeddings and behavioral signal vectors.' },
  { step: '04', title: 'INFER', desc: 'Multi-head transformer classification across granular emotional dimensions.' },
  { step: '05', title: 'EXPLAIN', desc: 'Computes SHAP attribution scores and confidence distributions for full transparency.' },
]

const engineCapabilities = [
  {
    icon: <Activity className="h-5 w-5 text-[#C7FF4A]" />,
    title: 'Behavioral Signals',
    desc: 'Models language patterns, interaction cues, and behavioral signals to detect subtle affective transitions in textual data.',
    badge: 'SIGNAL_EXTRACTION',
  },
  {
    icon: <Brain className="h-5 w-5 text-[#C7FF4A]" />,
    title: 'Transformer Analysis',
    desc: 'Uses fine-tuned RoBERTa representations with contextual attention layers for precision emotion classification.',
    badge: 'TRANSFORMER_CORE',
  },
  {
    icon: <Sliders className="h-5 w-5 text-[#C7FF4A]" />,
    title: 'Explainable Outputs',
    desc: 'Uses explainability techniques including attention attribution and token saliency to make model predictions interpretable.',
    badge: 'XAI_FRAMEWORK',
  },
]

const techStack = [
  'PyTorch',
  'Transformers',
  'RoBERTa',
  'PostgreSQL',
  'FastAPI',
  'React',
  'SHAP',
  'scikit-learn',
]

export function LandingPage() {
  const [activeSample, setActiveSample] = useState(0)

  const sampleInterpretations = [
    {
      text: "I spent the entire weekend rebuilding our backend architecture. While it was exhausting, seeing latency drop by 80% felt incredibly rewarding.",
      primaryEmotion: "Joy / Accomplishment",
      confidence: "94.2%",
      behavioralSignal: "Goal-directed validation",
      tokens: [
        { word: "exhausting", weight: -0.25 },
        { word: "rebuilding", weight: 0.12 },
        { word: "latency drop", weight: 0.42 },
        { word: "incredibly", weight: 0.38 },
        { word: "rewarding", weight: 0.86 },
      ]
    },
    {
      text: "Every update seems to introduce new regressions. I'm struggling to understand why basic regressions keep slipping through QA reviews.",
      primaryEmotion: "Frustration / Disappointment",
      confidence: "91.8%",
      behavioralSignal: "Repetitive friction",
      tokens: [
        { word: "regressions", weight: 0.65 },
        { word: "struggling", weight: 0.78 },
        { word: "basic", weight: 0.31 },
        { word: "slipping", weight: 0.52 },
      ]
    }
  ]

  return (
    <div className="space-y-24 sm:space-y-32 py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      {/* Hero Section */}
      <section className="grid lg:grid-cols-12 gap-12 items-center pt-6 sm:pt-12">
        <div className="lg:col-span-7 space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-[#101010] border border-[#262626] text-[11px] font-mono text-[#C7FF4A]">
            <span className="h-1.5 w-1.5 rounded-full bg-[#C7FF4A] animate-pulse"></span>
            BEHAVIORAL EMOTION ANALYSIS MODEL
          </div>

          <div className="space-y-2">
            <h1 className="font-display text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-[#F5F5F0] leading-[1.05]">
              B.E.A.M.
            </h1>
            <p className="font-display text-2xl sm:text-3xl text-[#B8B8B0] uppercase tracking-wide leading-snug">
              Understand emotional behavior through transformer intelligence.
            </p>
          </div>

          <p className="text-sm sm:text-base text-[#B8B8B0] max-w-xl leading-relaxed">
            An explainable deep learning framework for analyzing emotional states and behavioral signals in online textual data with precision confidence metrics and attribution trails.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-4">
            <Link to="/analysis">
              <Button variant="primary" size="lg" rightIcon={<ArrowRight className="h-4 w-4" />}>
                START ANALYSIS
              </Button>
            </Link>
            <a href="#research">
              <Button variant="secondary" size="lg">
                EXPLORE RESEARCH
              </Button>
            </a>
          </div>

          <div className="pt-6 grid grid-cols-3 gap-4 border-t border-[#1C1C1C] max-w-lg">
            <div>
              <p className="font-display text-xl font-bold text-[#F5F5F0]">94.8%</p>
              <p className="text-[10px] text-[#73736F] uppercase tracking-wider font-mono">F1-Validation</p>
            </div>
            <div>
              <p className="font-display text-xl font-bold text-[#F5F5F0]">28</p>
              <p className="text-[10px] text-[#73736F] uppercase tracking-wider font-mono">Emotion Classes</p>
            </div>
            <div>
              <p className="font-display text-xl font-bold text-[#C7FF4A]">SHAP</p>
              <p className="text-[10px] text-[#73736F] uppercase tracking-wider font-mono">Explainability</p>
            </div>
          </div>
        </div>

        {/* Custom Abstract Scientific Visualization */}
        <div className="lg:col-span-5">
          <div className="relative rounded-2xl bg-[#0B0B0B] border border-[#222222] p-6 shadow-[inset_0_1px_0_rgba(255,255,255,0.06),0_12px_32px_rgba(0,0,0,0.8)] overflow-hidden">
            {/* Background grid */}
            <div className="absolute inset-0 instrument-grid opacity-40 pointer-events-none" />

            <div className="relative z-10 space-y-5">
              <div className="flex items-center justify-between border-b border-[#1C1C1C] pb-3 text-xs">
                <span className="font-mono text-[11px] text-[#73736F]">SIGNAL_MATRIX // v1.2</span>
                <span className="inline-flex items-center gap-1.5 font-mono text-[10px] text-[#C7FF4A]">
                  <span className="h-1.5 w-1.5 rounded-full bg-[#C7FF4A]" /> LIVE_FEED
                </span>
              </div>

              {/* Data Signal Waveform Canvas / SVG */}
              <div className="h-44 rounded-lg bg-[#070707] border border-[#1C1C1C] p-4 flex flex-col justify-between relative overflow-hidden">
                <svg className="absolute inset-0 w-full h-full" viewBox="0 0 400 160" preserveAspectRatio="none">
                  {/* Grid lines */}
                  <line x1="0" y1="40" x2="400" y2="40" stroke="#1A1A1A" strokeDasharray="3 3" />
                  <line x1="0" y1="80" x2="400" y2="80" stroke="#222222" />
                  <line x1="0" y1="120" x2="400" y2="120" stroke="#1A1A1A" strokeDasharray="3 3" />
                  
                  {/* Signal 1 - Background */}
                  <path
                    d="M 0 90 Q 50 60, 100 85 T 200 70 T 300 100 T 400 65"
                    fill="none"
                    stroke="#333333"
                    strokeWidth="1.5"
                  />
                  {/* Signal 2 - Foreground Lime Accent */}
                  <path
                    d="M 0 80 Q 40 30, 90 75 T 180 120 T 270 30 T 360 80 T 400 50"
                    fill="none"
                    stroke="#C7FF4A"
                    strokeWidth="2"
                    className="opacity-90"
                  />
                  {/* Data points */}
                  <circle cx="90" cy="75" r="3.5" fill="#C7FF4A" />
                  <circle cx="270" cy="30" r="3.5" fill="#C7FF4A" />
                  <circle cx="360" cy="80" r="3.5" fill="#FFFFFF" />
                </svg>

                <div className="relative z-10 flex justify-between text-[10px] font-mono text-[#73736F]">
                  <span>FREQ: 142.8 Hz</span>
                  <span>CONF: 0.942</span>
                </div>
                <div className="relative z-10 flex justify-between text-[10px] font-mono text-[#73736F]">
                  <span>LATENCY: 14.2ms</span>
                  <span className="text-[#C7FF4A]">STATUS: STABLE</span>
                </div>
              </div>

              {/* Multi-channel telemetry breakdown */}
              <div className="space-y-2 text-xs">
                <div>
                  <div className="flex justify-between text-[11px] mb-1 font-mono">
                    <span className="text-[#B8B8B0]">Valence Polarity</span>
                    <span className="text-[#C7FF4A]">+0.78</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-[#161616] overflow-hidden">
                    <div className="h-full bg-[#C7FF4A] rounded-full" style={{ width: '78%' }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-[11px] mb-1 font-mono">
                    <span className="text-[#B8B8B0]">Arousal Intensity</span>
                    <span className="text-[#F5F5F0]">0.64</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-[#161616] overflow-hidden">
                    <div className="h-full bg-[#8E8E8A] rounded-full" style={{ width: '64%' }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-[11px] mb-1 font-mono">
                    <span className="text-[#B8B8B0]">Cognitive Saliency</span>
                    <span className="text-[#F5F5F0]">0.89</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-[#161616] overflow-hidden">
                    <div className="h-full bg-[#555552] rounded-full" style={{ width: '89%' }} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Section 2: Research Credibility Process */}
      <section id="research" className="space-y-8">
        <div className="border-b border-[#1C1C1C] pb-4">
          <p className="text-[11px] font-mono tracking-[0.16em] uppercase text-[#C7FF4A]">
            METHODOLOGY & WORKFLOW
          </p>
          <h2 className="font-display text-3xl sm:text-4xl font-bold tracking-tight text-[#F5F5F0] mt-1">
            FROM TEXT TO INSIGHT
          </h2>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {pipelineSteps.map((item) => (
            <div
              key={item.step}
              className="group rounded-xl bg-[#0E0E0E] border border-[#222222] p-5 shadow-[inset_0_1px_0_rgba(255,255,255,0.05),0_4px_12px_rgba(0,0,0,0.6)] transition-all duration-150 hover:-translate-y-1 hover:border-[#383838]"
            >
              <div className="flex items-center justify-between">
                <span className="font-display text-2xl font-bold text-[#555552] group-hover:text-[#C7FF4A] transition-colors">
                  {item.step}
                </span>
                <span className="h-1.5 w-1.5 rounded-full bg-[#262626] group-hover:bg-[#C7FF4A]" />
              </div>
              <h3 className="font-display text-lg font-bold text-[#F5F5F0] mt-3">
                {item.title}
              </h3>
              <p className="text-xs text-[#73736F] mt-2 leading-relaxed">
                {item.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Section 3: The BEAM Engine */}
      <section id="features" className="space-y-8">
        <div className="border-b border-[#1C1C1C] pb-4">
          <p className="text-[11px] font-mono tracking-[0.16em] uppercase text-[#C7FF4A]">
            CORE ARCHITECTURE
          </p>
          <h2 className="font-display text-3xl sm:text-4xl font-bold tracking-tight text-[#F5F5F0] mt-1">
            THE BEAM ENGINE
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {engineCapabilities.map((cap) => (
            <Card
              key={cap.title}
              variant="default"
              padding="lg"
              hover
              className="flex flex-col justify-between space-y-6 group"
            >
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="h-10 w-10 rounded-lg bg-[#161616] border border-[#2A2A2A] flex items-center justify-center shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]">
                    {cap.icon}
                  </div>
                  <span className="font-mono text-[10px] text-[#73736F] bg-[#141414] px-2 py-1 rounded border border-[#222222]">
                    {cap.badge}
                  </span>
                </div>
                <h3 className="font-display text-2xl font-bold text-[#F5F5F0] group-hover:text-white">
                  {cap.title}
                </h3>
                <p className="text-xs sm:text-sm text-[#B8B8B0] leading-relaxed">
                  {cap.desc}
                </p>
              </div>

              <div className="pt-4 border-t border-[#1C1C1C] flex items-center text-xs font-mono text-[#C7FF4A]">
                <span>VIEW SPECIFICATION</span>
                <ArrowRight className="h-3 w-3 ml-1.5 transition-transform group-hover:translate-x-1" />
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* Section 4: Built for Interpretability */}
      <section id="architecture" className="space-y-8">
        <div className="border-b border-[#1C1C1C] pb-4">
          <p className="text-[11px] font-mono tracking-[0.16em] uppercase text-[#C7FF4A]">
            EXPLAINABLE AI
          </p>
          <h2 className="font-display text-3xl sm:text-4xl font-bold tracking-tight text-[#F5F5F0] mt-1">
            BUILT FOR INTERPRETABILITY
          </h2>
          <p className="text-sm text-[#B8B8B0] mt-1 max-w-2xl">
            BEAM does not simply output a prediction. It reveals the exact linguistic cues and token saliencies that guided the transformer reasoning.
          </p>
        </div>

        <div className="rounded-2xl bg-[#0E0E0E] border border-[#222222] p-6 sm:p-8 shadow-[inset_0_1px_0_rgba(255,255,255,0.05),0_8px_28px_rgba(0,0,0,0.8)]">
          <div className="flex flex-wrap items-center gap-3 mb-6">
            <span className="text-xs font-mono text-[#73736F]">SELECT SAMPLE:</span>
            {sampleInterpretations.map((sample, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setActiveSample(idx)}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono border transition-all ${
                  activeSample === idx
                    ? 'bg-[#181818] border-[#C7FF4A] text-[#C7FF4A] shadow-[0_0_8px_rgba(199,255,74,0.15)]'
                    : 'bg-[#121212] border-[#262626] text-[#B8B8B0] hover:border-[#383838]'
                }`}
              >
                Sample 0{idx + 1}
              </button>
            ))}
          </div>

          <div className="grid lg:grid-cols-12 gap-8">
            <div className="lg:col-span-7 space-y-6">
              <div>
                <label className="text-[10px] font-mono text-[#73736F] uppercase tracking-wider block mb-2">
                  RAW INPUT TEXT
                </label>
                <div className="p-4 rounded-xl bg-[#080808] border border-[#1E1E1E] text-sm text-[#F5F5F0] font-ui leading-relaxed">
                  "{sampleInterpretations[activeSample].text}"
                </div>
              </div>

              <div>
                <label className="text-[10px] font-mono text-[#73736F] uppercase tracking-wider block mb-2">
                  TOKEN ATTRIBUTION & SALIENCY (SHAP)
                </label>
                <div className="flex flex-wrap gap-2 p-4 rounded-xl bg-[#080808] border border-[#1E1E1E]">
                  {sampleInterpretations[activeSample].tokens.map((tok, i) => (
                    <span
                      key={i}
                      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded border text-xs font-mono ${
                        tok.weight > 0.5
                          ? 'bg-[#C7FF4A]/10 border-[#C7FF4A]/40 text-[#C7FF4A]'
                          : tok.weight > 0
                          ? 'bg-[#181818] border-[#333333] text-[#F5F5F0]'
                          : 'bg-[#1A0E0E] border-[#4A1A1A] text-[#FF6B6B]'
                      }`}
                    >
                      <span>{tok.word}</span>
                      <span className="text-[10px] opacity-70">
                        {tok.weight > 0 ? `+${tok.weight}` : tok.weight}
                      </span>
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="lg:col-span-5 space-y-4">
              <div className="p-5 rounded-xl bg-[#121212] border border-[#262626] space-y-4">
                <div className="flex items-center justify-between border-b border-[#1E1E1E] pb-3">
                  <span className="text-[11px] font-mono text-[#73736F] uppercase">Inference Results</span>
                  <span className="text-[11px] font-mono text-[#C7FF4A]">CALCULATED</span>
                </div>

                <div className="space-y-3 text-xs">
                  <div>
                    <span className="text-[#73736F] text-[10px] uppercase font-mono block">Primary Emotion</span>
                    <span className="font-display text-xl font-bold text-[#F5F5F0]">
                      {sampleInterpretations[activeSample].primaryEmotion}
                    </span>
                  </div>

                  <div>
                    <span className="text-[#73736F] text-[10px] uppercase font-mono block">Model Confidence</span>
                    <div className="flex items-center gap-3 mt-1">
                      <div className="flex-1 h-2 rounded-full bg-[#1C1C1C] overflow-hidden">
                        <div
                          className="h-full bg-[#C7FF4A]"
                          style={{ width: sampleInterpretations[activeSample].confidence }}
                        />
                      </div>
                      <span className="font-mono font-bold text-[#C7FF4A]">
                        {sampleInterpretations[activeSample].confidence}
                      </span>
                    </div>
                  </div>

                  <div>
                    <span className="text-[#73736F] text-[10px] uppercase font-mono block">Observed Behavioral Signal</span>
                    <span className="font-mono text-xs text-[#B8B8B0]">
                      {sampleInterpretations[activeSample].behavioralSignal}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Section 5: Technology & Research Stack */}
      <section id="models" className="space-y-6">
        <div className="border-b border-[#1C1C1C] pb-4">
          <p className="text-[11px] font-mono tracking-[0.16em] uppercase text-[#C7FF4A]">
            RESEARCH STACK
          </p>
          <h2 className="font-display text-2xl sm:text-3xl font-bold tracking-tight text-[#F5F5F0] mt-1">
            TECHNOLOGY & PIPELINE
          </h2>
        </div>

        <div className="flex flex-wrap gap-3">
          {techStack.map((tech) => (
            <div
              key={tech}
              className="px-4 py-2 rounded-lg bg-[#0E0E0E] border border-[#222222] font-mono text-xs text-[#B8B8B0] shadow-[inset_0_1px_0_rgba(255,255,255,0.04)] hover:border-[#383838] hover:text-[#F5F5F0] hover:bg-[#141414] transition-all"
            >
              {tech}
            </div>
          ))}
        </div>
      </section>

      {/* Section 6: Final CTA */}
      <section className="rounded-2xl bg-[#0E0E0E] border border-[#222222] p-8 sm:p-12 text-center relative overflow-hidden shadow-[inset_0_1px_0_rgba(255,255,255,0.08),0_12px_36px_rgba(0,0,0,0.9)]">
        <div className="absolute inset-0 instrument-grid opacity-20 pointer-events-none" />
        <div className="relative z-10 max-w-2xl mx-auto space-y-6">
          <span className="text-[11px] font-mono uppercase tracking-[0.2em] text-[#C7FF4A]">
            INTERPRETABLE DEEP LEARNING PIPELINE
          </span>
          <h2 className="font-display text-4xl sm:text-5xl font-bold text-[#F5F5F0] tracking-tight">
            READY TO ANALYZE?
          </h2>
          <p className="text-sm sm:text-base text-[#B8B8B0]">
            Explore textual behavior through an interpretable deep learning pipeline with explainable confidence models.
          </p>
          <div className="pt-2 flex flex-wrap justify-center gap-4">
            <Link to="/analysis">
              <Button variant="primary" size="lg" rightIcon={<ArrowRight className="h-4 w-4" />}>
                START ANALYSIS →
              </Button>
            </Link>
            <a href="#research">
              <Button variant="secondary" size="lg">
                VIEW RESEARCH
              </Button>
            </a>
          </div>
        </div>
      </section>
    </div>
  )
}
