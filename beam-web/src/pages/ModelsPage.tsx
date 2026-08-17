import {
  Cpu,
  CheckCircle2,
  Sliders,
  Layers,
  Zap,
  ArrowUpRight,
  ShieldCheck,
} from 'lucide-react'

import { Button } from '../components/Button'
import { Card } from '../components/Card'

const models = [
  {
    name: 'RoBERTa-Emotion-v1.2',
    version: '1.2.0',
    task: 'Granular Affective Classification',
    dataset: 'GoEmotions + Dev Telemetry',
    accuracy: '94.8%',
    f1: '0.942',
    latency: '16.4ms',
    status: 'PRODUCTION_ACTIVE',
    parameters: '125M',
  },
  {
    name: 'BERT-Base-Affective',
    version: '1.0.4',
    task: 'Binary Valence / Polarity',
    dataset: 'Academic Benchmark',
    accuracy: '91.2%',
    f1: '0.908',
    latency: '14.1ms',
    status: 'STANDBY',
    parameters: '110M',
  },
  {
    name: 'DeBERTa-v3-Attention-Attribution',
    version: '2.0.0-rc1',
    task: 'Explainable Behavioral Inference',
    dataset: 'Full Aggregated Corpus',
    accuracy: '95.6%',
    f1: '0.951',
    latency: '24.8ms',
    status: 'EVALUATION',
    parameters: '304M',
  },
]

export function ModelsPage() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#1C1C1C] pb-4">
        <div>
          <span className="text-[10px] font-mono text-[#C7FF4A] tracking-wider uppercase">
            WORKSPACE // TRANSFORMER REGISTRY
          </span>
          <h1 className="font-display text-3xl sm:text-4xl font-bold text-[#F5F5F0] tracking-tight mt-1">
            MODEL REGISTRY
          </h1>
          <p className="text-xs sm:text-sm text-[#73736F] mt-1">
            Active neural network checkpoints, evaluation telemetry, and deployment weights.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="secondary" size="sm">
            Deploy Checkpoint
          </Button>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {models.map((model) => (
          <Card
            key={model.name}
            variant="default"
            padding="none"
            hover
            className="p-6 space-y-5 flex flex-col justify-between"
          >
            <div className="space-y-4">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <span className="font-mono text-[10px] text-[#73736F] bg-[#141414] px-2 py-0.5 rounded border border-[#222222]">
                    v{model.version}
                  </span>
                  <h3 className="font-display text-xl font-bold text-[#F5F5F0] mt-2">
                    {model.name}
                  </h3>
                </div>
                <span
                  className={`inline-flex items-center gap-1 font-mono text-[10px] ${
                    model.status === 'PRODUCTION_ACTIVE'
                      ? 'text-[#C7FF4A]'
                      : 'text-[#B8B8B0]'
                  }`}
                >
                  <span
                    className={`h-1.5 w-1.5 rounded-full ${
                      model.status === 'PRODUCTION_ACTIVE'
                        ? 'bg-[#C7FF4A]'
                        : 'bg-[#555552]'
                    }`}
                  />
                  {model.status === 'PRODUCTION_ACTIVE' ? 'LIVE' : 'STANDBY'}
                </span>
              </div>

              <div className="space-y-2 text-xs border-y border-[#181818] py-3">
                <div className="flex justify-between">
                  <span className="text-[#73736F]">Task</span>
                  <span className="text-[#F5F5F0] font-medium">{model.task}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#73736F]">Dataset</span>
                  <span className="text-[#B8B8B0]">{model.dataset}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#73736F]">Parameters</span>
                  <span className="text-[#B8B8B0] font-mono">{model.parameters}</span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="p-2 rounded bg-[#0A0A0A] border border-[#1C1C1C]">
                  <span className="text-[10px] font-mono text-[#73736F] uppercase block">Accuracy</span>
                  <span className="font-display text-base font-bold text-[#C7FF4A] block mt-0.5">{model.accuracy}</span>
                </div>
                <div className="p-2 rounded bg-[#0A0A0A] border border-[#1C1C1C]">
                  <span className="text-[10px] font-mono text-[#73736F] uppercase block">F1 Score</span>
                  <span className="font-display text-base font-bold text-[#F5F5F0] block mt-0.5">{model.f1}</span>
                </div>
                <div className="p-2 rounded bg-[#0A0A0A] border border-[#1C1C1C]">
                  <span className="text-[10px] font-mono text-[#73736F] uppercase block">Latency</span>
                  <span className="font-display text-base font-bold text-[#B8B8B0] block mt-0.5">{model.latency}</span>
                </div>
              </div>
            </div>

            <div className="pt-2">
              <Button variant="secondary" fullWidth size="sm" rightIcon={<ArrowUpRight className="h-3.5 w-3.5" />}>
                Inspect Architecture
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
