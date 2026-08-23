import { useState } from 'react'
import {
  MessageSquare,
  Sparkles,
  ArrowRight,
  TrendingUp,
  BarChart2,
  Users,
  Activity,
  Layers,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react'

import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { beamApi, type RedditAnalysisResult } from '../services/api/beam'

const presetSources = [
  { label: 'r/pondicherry (Local Community Feed)', value: 'r/pondicherry', type: 'subreddit' as const },
  { label: 'u/student_dev (Demo Student Profile)', value: 'u/student_dev', type: 'username' as const },
  { label: 'r/learnmachinelearning (AI Community)', value: 'r/learnmachinelearning', type: 'subreddit' as const },
  { label: 'r/datascience (Professional Discourse)', value: 'r/datascience', type: 'subreddit' as const },
  { label: 'r/mentalhealth (Supportive Discourse)', value: 'r/mentalhealth', type: 'subreddit' as const },
]

export function RedditAnalysisPage() {
  const [redditInput, setRedditInput] = useState('u/student_dev')
  const [sourceType, setSourceType] = useState<'username' | 'subreddit'>('username')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [redditResult, setRedditResult] = useState<RedditAnalysisResult | null>(null)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  const handleAnalyzeReddit = async () => {
    if (!redditInput.trim() || isAnalyzing) return
    setIsAnalyzing(true)
    setErrorMsg(null)

    try {
      const res = await beamApi.analyzeReddit({
        identifier: redditInput.trim(),
        source_type: sourceType,
        max_items: 5,
      })
      if (res.data) {
        setRedditResult(res.data)
      }
    } catch (err: any) {
      setErrorMsg(`Failed to load posts for ${redditInput.trim()}. Please ensure the Reddit account/subreddit is public.`)
      setRedditResult(null)
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      {/* Header Banner */}
      <div className="border-b border-[#1C1C1C] pb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-mono font-medium bg-[#FF4500]/10 text-[#FF5722] border border-[#FF4500]/25">
              <MessageSquare className="h-3 w-3" />
              SOCIAL INTELLIGENCE PIPELINE
            </span>
            <span className="text-xs font-mono text-[#555550]">|</span>
            <span className="text-xs font-mono text-[#8E8E88]">RoBERTa + GoEmotions 27-Class Engine</span>
          </div>
          <h1 className="font-display text-3xl font-bold tracking-tight text-[#F5F5F0]">
            Reddit Social Post Analysis
          </h1>
          <p className="text-sm text-[#8E8E88] mt-1 max-w-2xl">
            Injest live Reddit submissions, comments, and community threads to compute longitudinal affective trajectories, sentiment valence, and keyword emotion attributions.
          </p>
        </div>
      </div>

      {/* Query Bar */}
      <Card variant="elevated" padding="none" className="p-6 border-[#222222] bg-[#0A0A0A]">
        <div className="flex flex-col gap-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="text-xs font-mono text-[#8E8E88] uppercase tracking-wider">
              Target Profile or Subreddit Corpus
            </span>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[11px] text-[#555550]">Quick Presets:</span>
              {presetSources.map((preset) => (
                <button
                  key={preset.value}
                  type="button"
                  onClick={() => {
                    setSourceType(preset.type)
                    setRedditInput(preset.value)
                  }}
                  className={`text-xs font-mono px-2 py-0.5 rounded border transition-colors ${
                    redditInput === preset.value
                      ? 'border-[#FF4500] text-[#FF5722] bg-[#FF4500]/10'
                      : 'border-[#222222] text-[#73736F] hover:text-[#F5F5F0] hover:border-[#333333]'
                  }`}
                >
                  {preset.value}
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-3">
            {/* Type selector */}
            <div className="flex items-center gap-1 bg-[#121212] border border-[#222222] rounded-lg p-1">
              <button
                type="button"
                onClick={() => setSourceType('username')}
                className={`px-3 py-1.5 rounded text-xs font-mono transition-all ${
                  sourceType === 'username' ? 'bg-[#222222] text-[#FF5722] font-bold' : 'text-[#73736F]'
                }`}
              >
                u/ Username
              </button>
              <button
                type="button"
                onClick={() => setSourceType('subreddit')}
                className={`px-3 py-1.5 rounded text-xs font-mono transition-all ${
                  sourceType === 'subreddit' ? 'bg-[#222222] text-[#FF5722] font-bold' : 'text-[#73736F]'
                }`}
              >
                r/ Subreddit
              </button>
            </div>

            {/* Input field */}
            <div className="relative flex-1 w-full">
              <input
                type="text"
                value={redditInput}
                onChange={(e) => setRedditInput(e.target.value)}
                placeholder={
                  sourceType === 'username'
                    ? 'Enter username (e.g. u/student_dev)'
                    : 'Enter subreddit (e.g. r/learnmachinelearning)'
                }
                className="w-full rounded-lg bg-[#080808] border border-[#1E1E1E] px-4 py-2.5 text-sm text-[#F5F5F0] focus:border-[#FF4500] focus:outline-none font-mono"
              />
            </div>

            <Button
              variant="primary"
              size="md"
              isLoading={isAnalyzing}
              onClick={handleAnalyzeReddit}
              className="bg-[#FF4500] hover:bg-[#FF5722] text-white whitespace-nowrap"
              rightIcon={<ArrowRight className="h-4 w-4" />}
            >
              Analyze Posts
            </Button>
          </div>

          {errorMsg && (
            <div className="flex items-center gap-2 text-xs text-[#FF6B6B] bg-[#FF4500]/10 border border-[#FF4500]/30 px-3 py-2 rounded">
              <AlertCircle className="h-3.5 w-3.5" />
              <span>{errorMsg}</span>
            </div>
          )}
        </div>
      </Card>

      {/* Initial state placeholder */}
      {!redditResult && !isAnalyzing && (
        <Card variant="outline" padding="lg" className="border-dashed border-[#222222] text-center py-12">
          <div className="max-w-md mx-auto space-y-3">
            <div className="h-12 w-12 rounded-full bg-[#FF4500]/10 border border-[#FF4500]/20 flex items-center justify-center mx-auto text-[#FF5722]">
              <MessageSquare className="h-6 w-6" />
            </div>
            <h3 className="font-display text-lg font-semibold text-[#F5F5F0]">Ready for Social Emotion Mining</h3>
            <p className="text-xs text-[#73736F] leading-relaxed">
              Select a demo preset above or enter any public Reddit user / community to parse multi-class affective distributions, emotion trajectories, and keyword attributions.
            </p>
            <div className="pt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleAnalyzeReddit}
                className="border-[#333333] hover:border-[#FF4500] text-xs font-mono"
              >
                Run Default Analysis (u/student_dev)
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Results Grid */}
      {redditResult && redditResult.total_posts_analyzed === 0 && (
        <Card variant="outline" padding="lg" className="border-[#222222] text-center py-10">
          <div className="max-w-md mx-auto space-y-2">
            <div className="h-10 w-10 rounded-full bg-[#222222] flex items-center justify-center mx-auto text-[#73736F]">
              <MessageSquare className="h-5 w-5" />
            </div>
            <h3 className="font-display text-base font-semibold text-[#F5F5F0]">No Posts Found for {redditResult.source}</h3>
            <p className="text-xs text-[#73736F]">
              This username or subreddit has no recent public submissions or does not exist. Try searching for another active subreddit or username.
            </p>
          </div>
        </Card>
      )}

      {redditResult && redditResult.total_posts_analyzed > 0 && (
        <div className="grid lg:grid-cols-12 gap-6 animate-in fade-in duration-200">
          {/* Distribution & Key Stats (5 cols) */}
          <div className="lg:col-span-5 space-y-6">
            <Card variant="elevated" padding="none" className="p-6 space-y-5 border-[#2A2A2A]">
              <div className="border-b border-[#1C1C1C] pb-3">
                <span className="text-[10px] font-mono text-[#FF5722] uppercase tracking-wider block">
                  SOURCE: {redditResult.source}
                </span>
                <h3 className="font-display text-xl font-bold text-[#F5F5F0] mt-0.5">
                  DOMINANT: {redditResult.dominant_emotion}
                </h3>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-[#080808] border border-[#1C1C1C] rounded-lg">
                  <span className="text-[10px] font-mono text-[#73736F] block">POSTS ANALYZED</span>
                  <span className="font-mono text-xl font-bold text-[#F5F5F0]">
                    {redditResult.total_posts_analyzed}
                  </span>
                </div>
                <div className="p-3 bg-[#080808] border border-[#1C1C1C] rounded-lg">
                  <span className="text-[10px] font-mono text-[#73736F] block">AVERAGE VALENCE</span>
                  <span
                    className={`font-mono text-xl font-bold ${
                      redditResult.average_valence >= 0 ? 'text-[#C7FF4A]' : 'text-[#FF6B6B]'
                    }`}
                  >
                    {redditResult.average_valence > 0 ? `+${redditResult.average_valence}` : redditResult.average_valence}
                  </span>
                </div>
              </div>

              {/* Emotion distribution bars */}
              <div className="space-y-3 pt-2">
                <span className="text-xs font-mono text-[#73736F] uppercase tracking-wider block">
                  Affective Distribution (%)
                </span>
                <div className="space-y-2.5">
                  {redditResult.emotion_distribution.map((item, idx) => (
                    <div key={item.emotion} className="space-y-1">
                      <div className="flex justify-between text-xs font-mono">
                        <span className="text-[#F5F5F0] flex items-center gap-1.5">
                          <span className="text-[10px] text-[#73736F]">#{idx + 1}</span>
                          {item.emotion}
                        </span>
                        <span className="text-[#FF5722] font-bold">{item.percentage}%</span>
                      </div>
                      <div className="h-1.5 w-full bg-[#1A1A1A] rounded-full overflow-hidden">
                        <div
                          className="h-full bg-[#FF4500] rounded-full transition-all duration-500"
                          style={{ width: `${item.percentage}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Top Trigger Keywords */}
              {redditResult.top_keywords && redditResult.top_keywords.length > 0 && (
                <div className="pt-2 border-t border-[#1C1C1C]">
                  <span className="text-xs font-mono text-[#73736F] uppercase tracking-wider block mb-2">
                    Key Attribution Terms
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {redditResult.top_keywords.map((kw) => (
                      <span
                        key={kw}
                        className="px-2 py-0.5 bg-[#141414] border border-[#222222] rounded text-[11px] font-mono text-[#D4D4D0]"
                      >
                        #{kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </Card>

            {/* Longitudinal timeline trajectory */}
            <Card variant="elevated" padding="none" className="p-6 border-[#2A2A2A] space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-[#73736F] uppercase tracking-wider">
                  Longitudinal Valence Vector
                </span>
                <span className="text-[10px] font-mono text-[#C7FF4A]">Sequential Post Flow</span>
              </div>
              <div className="flex items-center gap-2 pt-2">
                {redditResult.timeline_vector.map((point) => (
                  <div key={point.index} className="flex-1 flex flex-col items-center gap-1">
                    <div className="h-20 w-full bg-[#0E0E0E] border border-[#1E1E1E] rounded flex items-end justify-center p-1 relative group">
                      <div
                        className={`w-full rounded-sm transition-all ${
                          point.valence >= 0 ? 'bg-[#C7FF4A]' : 'bg-[#FF6B6B]'
                        }`}
                        style={{ height: `${Math.max(15, Math.abs(point.valence) * 100)}%` }}
                      />
                      <div className="absolute -top-7 hidden group-hover:block bg-[#1A1A1A] text-[9px] font-mono px-1.5 py-0.5 rounded border border-[#333333] whitespace-nowrap z-10 text-[#F5F5F0]">
                        {point.emotion} ({point.valence > 0 ? `+${point.valence}` : point.valence})
                      </div>
                    </div>
                    <span className="text-[9px] font-mono text-[#73736F]">P{point.index}</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Granular Posts Stream (7 cols) */}
          <div className="lg:col-span-7 space-y-4">
            <div className="flex items-center justify-between px-1">
              <span className="text-xs font-mono text-[#73736F] uppercase tracking-wider">
                Post-by-Post Inference Feed ({redditResult.analyzed_posts.length})
              </span>
              <span className="text-[10px] font-mono text-[#FF5722]">RoBERTa Classifier Active</span>
            </div>

            <div className="space-y-3">
              {redditResult.analyzed_posts.map((post) => (
                <div
                  key={post.id}
                  className="p-4 bg-[#0A0A0A] border border-[#1E1E1E] rounded-xl hover:border-[#333333] transition-all space-y-3"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-[10px] font-mono text-[#555550]">{post.id}</span>
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 bg-[#FF4500]/15 text-[#FF5722] border border-[#FF4500]/30 rounded text-[11px] font-mono font-medium">
                        {post.primary_emotion}
                      </span>
                      <span className="text-[11px] font-mono text-[#C7FF4A]">{post.confidence}% conf</span>
                    </div>
                  </div>

                  <p className="text-sm text-[#D4D4D0] leading-relaxed font-sans italic">
                    "{post.text}"
                  </p>

                  <div className="flex items-center justify-between pt-2 border-t border-[#141414] text-[10px] font-mono text-[#73736F]">
                    <div className="flex items-center gap-2">
                      <span>Valence:</span>
                      <span className={post.valence >= 0 ? 'text-[#C7FF4A]' : 'text-[#FF6B6B]'}>
                        {post.valence > 0 ? `+${post.valence}` : post.valence}
                      </span>
                    </div>
                    {post.trigger_words && post.trigger_words.length > 0 && (
                      <div className="flex items-center gap-1">
                        <span className="text-[#555550]">Triggers:</span>
                        <span className="text-[#A3A39E]">{post.trigger_words.join(', ')}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
