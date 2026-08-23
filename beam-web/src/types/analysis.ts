export type AnalysisStatus = 'pending' | 'processing' | 'completed' | 'failed'

export type SourceType = 'text' | 'discussion' | 'social_feed' | 'review'

export type AnalysisCreateRequest = {
  text: string
  source_type: SourceType
  title?: string | null
}

export type AnalysisCreatedResponse = {
  session_id: string
  status: AnalysisStatus
}

export type EmotionDistributionItem = {
  label: string
  score: number
}

/** Model-derived prediction. Fields are null until a real model is deployed. */
export type PredictionPayload = {
  primary_emotion: string | null
  confidence: number | null
  emotion_distribution: EmotionDistributionItem[] | null
  inference_time_ms: number | null
}

export type BehaviorMetricsPayload = {
  positivity_score: number | null
  negativity_score: number | null
  engagement_score: number | null
  linguistic_complexity: number | null
  emotional_variance: number | null
  posting_frequency: number | null
}

export type ExplanationPayload = {
  method: string | null
  summary: string | null
  important_keywords: string[] | null
}

export type ModelInfoPayload = {
  model_name: string | null
  model_version: string | null
  deployed: boolean
  note: string | null
}

export type AnalysisInputMetadata = {
  char_count: number
  word_count: number
  raw_text: string
  created_at: string
}

export type AnalysisSessionSummary = {
  session_id: string
  status: AnalysisStatus
  source_type: string
  title: string | null
  created_at: string
  completed_at: string | null
  primary_emotion: string | null
  confidence: number | null
  model_name: string | null
}

export type AnalysisDetail = AnalysisSessionSummary & {
  input: AnalysisInputMetadata
  prediction: PredictionPayload | null
  behavior_metrics: BehaviorMetricsPayload | null
  explanation: ExplanationPayload | null
  model_info: ModelInfoPayload
}

export type AnalysisSort = 'created_desc' | 'created_asc'

export type AnalysisListParams = {
  page?: number | undefined
  page_size?: number | undefined
  search?: string | undefined
  status?: AnalysisStatus | '' | undefined
  sort?: AnalysisSort | undefined
}

export type AnalysisListResponse = {
  items: AnalysisSessionSummary[]
  total: number
  page: number
  page_size: number
  pages: number
}
