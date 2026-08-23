import { Link } from 'react-router-dom'
import { Activity, Brain, Sliders } from 'lucide-react'

import { KeycapBadge, KeycapCard, KeycapPanel } from '../components/keycap'
import {
  Container,
  FeatureModule,
  MetricDisplay,
  SectionHeading,
  StatusIndicator,
  TechnicalLabel,
} from '../components/global'
import { keycapClass } from '../components/keycap'
import { HeroVisual } from '../components/landing/HeroVisual'

const researchStages = [
  {
    step: '01',
    title: 'Collect',
    desc: 'Ingest raw textual streams and behavioral telemetry across online discussions.',
  },
  {
    step: '02',
    title: 'Clean',
    desc: 'Apply rigorous token cleaning, de-identification, and noise filtering.',
  },
  {
    step: '03',
    title: 'Analyze',
    desc: 'Extract deep semantic embeddings and behavioral signal vectors.',
  },
  {
    step: '04',
    title: 'Infer',
    desc: 'Multi-head transformer classification across granular emotional dimensions.',
  },
  {
    step: '05',
    title: 'Explain',
    desc: 'Compute SHAP attribution scores and confidence distributions for full transparency.',
  },
]

const capabilities = [
  {
    index: '01',
    code: 'SIGNAL_EXTRACTION',
    icon: <Activity className="h-4.5 w-4.5" />,
    title: 'Behavioral Signals',
    desc: 'Models language patterns, interaction cues, and behavioral signals to detect subtle affective transitions across large volumes of textual data — the raw sensory layer of the pipeline.',
  },
  {
    index: '02',
    code: 'TRANSFORMER_CORE',
    icon: <Brain className="h-4.5 w-4.5" />,
    title: 'Transformer Analysis',
    desc: 'Fine-tuned RoBERTa representations with contextual attention layers classify emotional states with calibrated precision across granular, human-readable emotion dimensions.',
  },
  {
    index: '03',
    code: 'XAI_FRAMEWORK',
    icon: <Sliders className="h-4.5 w-4.5" />,
    title: 'Explainable Outputs',
    desc: 'Attention attribution and token saliency expose exactly which linguistic evidence drove each prediction — no black-box labels, only traceable reasoning.',
  },
]

const interpretabilityFacets = [
  {
    label: 'Emotion Classification',
    detail: 'Granular multi-label emotion states with ranked alternatives.',
  },
  {
    label: 'Behavioral Metrics',
    detail: 'Valence polarity, arousal intensity, and cognitive saliency scores.',
  },
  {
    label: 'Model Confidence',
    detail: 'Calibrated probability distributions for every inference.',
  },
  {
    label: 'Feature Importance',
    detail: 'Per-token SHAP attributions ranked by contribution weight.',
  },
  {
    label: 'Evidence',
    detail: 'Direct linguistic citations linking outputs back to source text.',
  },
]

const attributionTokens = [
  { word: 'exhausting', weight: '-0.25', positive: false },
  { word: 'latency drop', weight: '+0.42', positive: true },
  { word: 'incredibly', weight: '+0.38', positive: true },
  { word: 'rewarding', weight: '+0.86', positive: true },
]

const techStack = [
  'PyTorch',
  'HuggingFace Transformers',
  'RoBERTa',
  'FastAPI',
  'React',
  'PostgreSQL',
  'scikit-learn',
  'SHAP',
]

export function LandingPage() {
  return (
    <div id="overview">
      {/* ================= HERO ================= */}
      <section className="instrument-grid border-b border-line-subtle">
        <Container className="grid items-center gap-12 py-16 sm:py-20 lg:grid-cols-12 lg:gap-10 lg:py-24">
          <div className="space-y-7 lg:col-span-7">
            <div className="flex items-center gap-4">
              <StatusIndicator label="Operational" />
              <TechnicalLabel tone="lime">Behavioral Emotion Analysis Model</TechnicalLabel>
            </div>

            <div className="space-y-4">
              <h1 className="font-display text-6xl font-semibold leading-[0.95] tracking-[0.04em] text-chalk sm:text-7xl lg:text-8xl">
                B.E.A.M.
              </h1>
              <p className="max-w-xl font-display text-xl font-normal normal-case leading-snug tracking-wide text-mist sm:text-2xl">
                Understand emotional behavior through transformer intelligence.
              </p>
            </div>

            <p className="max-w-xl text-sm leading-relaxed text-mist sm:text-base">
              An explainable deep learning framework for analyzing emotional states
              and behavioral signals in online textual data.
            </p>

            <div className="flex flex-wrap items-center gap-3.5 pt-1">
              <Link to="/analysis" className={keycapClass('primary', 'lg')}>
                Start Analysis →
              </Link>
              <a href="#research" className={keycapClass('graphite', 'lg')}>
                Explore Research
              </a>
            </div>

            <dl className="grid max-w-lg grid-cols-3 gap-6 border-t border-line-subtle pt-7">
              <MetricDisplay value="94.8%" label="F1 Validation" />
              <MetricDisplay value="28" label="Emotion Classes" />
              <MetricDisplay value="SHAP" label="Explainability" tone="lime" />
            </dl>
          </div>

          <div className="lg:col-span-5">
            <HeroVisual />
          </div>
        </Container>
      </section>

      {/* ================= RESEARCH FLOW ================= */}
      <section id="research" className="scroll-mt-24 border-b border-line-subtle bg-deep/40">
        <Container className="space-y-10 py-16 sm:py-20 lg:py-24">
          <SectionHeading
            eyebrow="Research Flow"
            title="From Raw Text to Interpretable Insight"
            description="Five deterministic stages carry every input through the B.E.A.M. pipeline — nothing is skipped, everything is auditable."
          />

          <ol className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5" aria-label="Research flow stages">
            {researchStages.map((stage) => (
              <li key={stage.step}>
                <KeycapCard interactive className="group flex h-full flex-col p-5">
                  <div className="flex items-center justify-between">
                    <span className="font-display text-2xl font-semibold leading-none text-[#3A3A36] transition-colors duration-150 group-hover:text-lime">
                      {stage.step}
                    </span>
                    <span
                      className="h-1.5 w-1.5 rounded-full bg-line transition-colors duration-150 group-hover:bg-lime"
                      aria-hidden="true"
                    />
                  </div>
                  <h3 className="mt-5 font-display text-base font-semibold uppercase tracking-[0.08em] text-chalk">
                    {stage.title}
                  </h3>
                  <p className="mt-2 text-xs leading-relaxed text-dim">{stage.desc}</p>
                </KeycapCard>
              </li>
            ))}
          </ol>
        </Container>
      </section>

      {/* ================= CORE CAPABILITIES ================= */}
      <section id="features" className="scroll-mt-24 border-b border-line-subtle">
        <Container className="space-y-10 py-16 sm:py-20 lg:py-24">
          <SectionHeading
            eyebrow="Core Capabilities"
            title="The B.E.A.M. Engine"
            description="Three cooperating modules form the analysis core — signal extraction, transformer inference, and mechanical explainability."
          />

          <div className="grid gap-5 md:grid-cols-3 md:gap-6">
            {capabilities.map((capability) => (
              <FeatureModule
                key={capability.code}
                index={capability.index}
                code={capability.code}
                title={capability.title}
                description={capability.desc}
                icon={capability.icon}
                footer={
                  <span className="text-[10px] font-medium uppercase tracking-[0.18em] text-dim transition-colors duration-150 group-hover:text-lime">
                    Module Active
                  </span>
                }
              />
            ))}
          </div>
        </Container>
      </section>

      {/* ================= INTERPRETABILITY ================= */}
      <section id="architecture" className="scroll-mt-24 border-b border-line-subtle bg-deep/40">
        <Container className="space-y-10 py-16 sm:py-20 lg:py-24">
          <SectionHeading
            eyebrow="Explainable AI"
            title="Built for Interpretability"
            description="B.E.A.M. is designed to expose reasoning and evidence rather than simply returning a label. Every output ships with the full audit trail that produced it."
          />

          <KeycapPanel
            eyebrow="Output Contract // v1"
            title="Inference Report Structure"
            meta={<TechnicalLabel>5 Facets</TechnicalLabel>}
            bodyClassName="p-5 sm:p-8"
          >
            <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
              {interpretabilityFacets.map((facet, i) => (
                <li key={facet.label} className="flex flex-col">
                  <KeycapCard className="flex h-full flex-col gap-3 bg-raised p-4">
                    <span className="font-display text-xs font-semibold tracking-[0.14em] text-dim">
                      F{String(i + 1).padStart(2, '0')}
                    </span>
                    <h3 className="font-display text-sm font-semibold uppercase leading-snug tracking-[0.06em] text-chalk">
                      {facet.label}
                    </h3>
                    <p className="text-xs leading-relaxed text-dim">{facet.detail}</p>
                  </KeycapCard>
                </li>
              ))}
            </ul>

            {/* Evidence strip — token-level attribution sample */}
            <div className="mt-8 rounded-module border border-line-subtle bg-surface p-5">
              <div className="mb-4 flex items-center justify-between">
                <TechnicalLabel>Token Attribution · SHAP</TechnicalLabel>
                <StatusIndicator label="Sample Trace" tone="idle" pulse={false} />
              </div>
              <div className="flex flex-wrap gap-2">
                {attributionTokens.map((token) => (
                  <KeycapBadge
                    key={token.word}
                    tone={token.positive ? 'lime' : 'graphite'}
                    className="normal-case tracking-normal"
                  >
                    {token.word}
                    <span className={token.positive ? 'opacity-80' : 'opacity-60'}>
                      {token.weight}
                    </span>
                  </KeycapBadge>
                ))}
              </div>
              <p className="mt-4 text-xs leading-relaxed text-dim">
                Each token carries a signed contribution score, so a prediction can always be
                traced back to the exact words that produced it.
              </p>
            </div>
          </KeycapPanel>
        </Container>
      </section>

      {/* ================= TECHNOLOGY ================= */}
      <section id="documentation" className="scroll-mt-24 border-b border-line-subtle">
        <Container className="space-y-10 py-16 sm:py-20 lg:py-24">
          <SectionHeading
            eyebrow="Stack & Documentation"
            title="Technology"
            description="A deliberately boring, production-grade stack. Full pipeline documentation lives in the repository /docs directory."
          />
          <ul className="flex flex-wrap gap-3" aria-label="Technology stack">
            {techStack.map((tech) => (
              <li key={tech}>
                <TechnicalLabel>{tech}</TechnicalLabel>
              </li>
            ))}
          </ul>
        </Container>
      </section>

      {/* ================= FINAL CTA ================= */}
      <section className="bg-deep/40">
        <Container className="py-16 sm:py-20 lg:py-24">
          <KeycapPanel bodyClassName="relative overflow-hidden p-8 text-center sm:p-14">
            <div className="pointer-events-none absolute inset-0 instrument-grid opacity-60" aria-hidden="true" />
            <div className="relative mx-auto max-w-2xl space-y-6">
              <TechnicalLabel tone="lime">Interpretable Deep Learning Pipeline</TechnicalLabel>
              <h2 className="font-display text-4xl font-semibold tracking-tight text-chalk sm:text-5xl">
                Ready to Analyze?
              </h2>
              <p className="mx-auto max-w-md text-sm leading-relaxed text-mist sm:text-base">
                Explore textual behavior through an interpretable deep learning pipeline.
              </p>
              <div className="flex flex-wrap justify-center gap-3.5 pt-2">
                <Link to="/analysis" className={keycapClass('primary', 'lg')}>
                  Start Analysis →
                </Link>
                <a href="#research" className={keycapClass('graphite', 'lg')}>
                  View Research
                </a>
              </div>
            </div>
          </KeycapPanel>
        </Container>
      </section>
    </div>
  )
}
