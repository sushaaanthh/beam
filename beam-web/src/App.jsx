import './App.css'

const pillars = [
  {
    title: 'Behavioral signals',
    copy: 'Models online language, posting patterns, and interaction cues to identify hedonic emotional states.',
  },
  {
    title: 'Transformer analysis',
    copy: 'Uses contextual language representations to support robust classification and interpretation.',
  },
  {
    title: 'Explainable outputs',
    copy: 'Keeps inference readable with clear reasoning, evidence trails, and model-aware summaries.',
  },
]

const pipeline = ['Collect', 'Clean', 'Train', 'Infer', 'Explain']

const roadmap = [
  'Implement independent Reddit ingestion in beam-scraper.',
  'Add training, inference, and evaluation workflows in beam-ai.',
  'Persist datasets, checkpoints, and experiment outputs in the new storage roots.',
]

function App() {
  return (
    <main className="beam-shell">
      <div className="beam-orb beam-orb--one" />
      <div className="beam-orb beam-orb--two" />

      <section className="beam-hero">
        <p className="beam-kicker">Behavioral Emotion Analysis Model</p>
        <h1>B.E.A.M.</h1>
        <p className="beam-lead">
          An explainable AI framework for detecting and analyzing hedonic emotional states from
          online textual behavior.
        </p>

        <div className="beam-actions">
          <a href="#architecture" className="beam-button">
            Explore architecture
          </a>
          <a href="#roadmap" className="beam-button beam-button--ghost">
            View roadmap
          </a>
        </div>
      </section>

      <section id="architecture" className="beam-grid" aria-label="Project pillars">
        {pillars.map((pillar) => (
          <article key={pillar.title} className="beam-card">
            <span className="beam-card__label">Core layer</span>
            <h2>{pillar.title}</h2>
            <p>{pillar.copy}</p>
          </article>
        ))}
      </section>

      <section className="beam-panel">
        <div>
          <p className="beam-panel__label">Processing flow</p>
          <h2>From raw behavior to interpretable insight</h2>
        </div>

        <div className="beam-steps" aria-label="Pipeline stages">
          {pipeline.map((step, index) => (
            <span key={step} className="beam-step">
              <strong>{String(index + 1).padStart(2, '0')}</strong>
              {step}
            </span>
          ))}
        </div>
      </section>

      <section id="roadmap" className="beam-roadmap">
        <div>
          <p className="beam-panel__label">Future roadmap</p>
          <h2>Architecture first, features next</h2>
        </div>

        <ul>
          {roadmap.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <footer className="beam-footer">
        <span>B.E.A.M. build surface</span>
        <span>React + Vite + TailwindCSS</span>
      </footer>
    </main>
  )
}

export default App
