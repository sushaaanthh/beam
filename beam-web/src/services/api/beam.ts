import { apiClient } from './http'

export interface SHAPToken {
  word: string
  saliency: number
}

export interface EmotionScore {
  emotion: string
  score: number
}

export interface LifestylePrescription {
  title: string
  prescription: string
  recommended_action: string
  wellness_target: string
  urgency: 'LOW' | 'MEDIUM' | 'HIGH'
  behavioral_tags: string[]
}

export interface JournalEntry {
  id: string
  title: string
  content: string
  mood_emoji?: string
  primary_emotion: string
  confidence: number
  valence: number
  arousal: number
  reflection_score: number
  reflection_depth?: number
  emotional_clarity?: number
  vocab_richness?: number
  ai_insight?: string
  lifestyle_prescription?: LifestylePrescription
  tokens: SHAPToken[]
  trigger_words: string[]
  distribution: EmotionScore[]
  signals: string[]
  latency_ms?: number
  created_at: string
}

export interface LiveEmotionResult {
  live_emotion: string
  confidence: number
  valence: number
  word_count: number
}

export interface VoiceTimelineSegment {
  time_range: string
  start_sec: number
  end_sec: number
  segment_text: string
  emotion: string
  valence: number
  badge_color: string
  acoustic_pitch_hz: number
}

export interface VoiceNote {
  id: string
  transcript: string
  duration_seconds: number
  primary_emotion: string
  confidence: number
  valence: number
  arousal: number
  reflection_score?: number
  trigger_words: string[]
  tokens?: SHAPToken[]
  emotion_timeline?: VoiceTimelineSegment[]
  waveform_amplitudes?: number[]
  stt_engine?: string
  created_at: string
}

export interface ChatMessage {
  id: string
  sender: 'user' | 'companion'
  message: string
  detected_emotion?: string
  confidence?: number
  valence?: number
  trigger_words?: string[]
  tokens?: SHAPToken[]
  created_at: string
}

export interface RedditAnalysisResult {
  source: string
  source_type: string
  total_posts_analyzed: number
  dominant_emotion: string
  average_valence: number
  emotion_distribution: { emotion: string; percentage: number; count: number }[]
  top_keywords: string[]
  analyzed_posts: {
    id: string
    text: string
    primary_emotion: string
    confidence: number
    valence: number
    trigger_words: string[]
  }[]
  timeline_vector: { index: number; emotion: string; valence: number }[]
}

export interface DashboardSummary {
  wellness_gauge: number
  dominant_emotion: string
  active_streak: number
  consistency_score: number
  positivity_ratio: number
  reflection_meter: number
  recovery_score: number
  weekly_trend: { day: string; score: number; dominant: string }[]
  word_cloud: { text: string; value: number }[]
  calendar_heatmap: { day_offset: number; intensity: number; mood: string }[]
  total_journals: number
  total_voice_notes: number
  recent_journals: JournalEntry[]
  recent_voice_notes: VoiceNote[]
  ai_insights: string[]
  unread_notifications: number
}

export interface WellnessMetrics {
  wellness_score: number
  consistency_score: number
  positive_ratio: number
  engagement_score: number
  reflection_score: number
  recovery_score: number
  dominant_emotion: string
  active_streak_days: number
  weekly_trend: { day: string; score: number; dominant: string }[]
  recommendations: string[]
}

export const beamApi = {
  // Priority 1: Journal AI
  predictLiveEmotion: async (text: string): Promise<LiveEmotionResult> => {
    const res = await apiClient.post('/journal/live', { text })
    return res.data
  },
  createJournal: async (data: { content: string; title?: string; mood_emoji?: string; model_name?: string }) => {
    const res = await apiClient.post('/journal', data)
    return res.data
  },
  getJournals: async () => {
    const res = await apiClient.get('/journal/history')
    return res.data
  },
  getJournalTrends: async () => {
    const res = await apiClient.get('/journal/trends')
    return res.data
  },
  deleteJournal: async (id: string) => {
    const res = await apiClient.delete(`/journal/${id}`)
    return res.data
  },

  // Priority 2: Voice AI
  transcribeAudio: async (formData: FormData): Promise<{ status: string; transcript: string }> => {
    const res = await apiClient.post('/voice/transcribe', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },
  uploadVoice: async (formData: FormData) => {
    const res = await apiClient.post('/voice', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },
  getVoiceHistory: async () => {
    const res = await apiClient.get('/voice/history')
    return res.data
  },

  // Priority 3: Chat Companion with Memory
  sendChatMessage: async (message: string) => {
    const res = await apiClient.post('/chat', { message })
    return res.data
  },
  getChatHistory: async () => {
    const res = await apiClient.get('/chat/history')
    return res.data
  },
  getChatSummary: async () => {
    const res = await apiClient.get('/chat/summary')
    return res.data
  },
  clearChatHistory: async () => {
    const res = await apiClient.delete('/chat/clear')
    return res.data
  },

  // Priority 4: Social Media & Reddit
  analyzeReddit: async (payload: { identifier: string; source_type?: string; max_items?: number }): Promise<{ status: string; data: RedditAnalysisResult }> => {
    const res = await apiClient.post('/social/reddit', payload)
    return res.data
  },
  getBenchmarks: async () => {
    const res = await apiClient.get('/social/benchmarks')
    return res.data
  },

  // Module 5: Wellness
  submitCheckIn: async (payload: {
    energy_level: number
    stress_level: number
    motivation_level: number
    sleep_quality: number
    free_text_reflection?: string
  }) => {
    const res = await apiClient.post('/wellness/check-in', payload)
    return res.data
  },
  getWellnessScore: async () => {
    const res = await apiClient.get('/wellness/score')
    return res.data
  },

  // Module 8: Dashboard
  getDashboardSummary: async () => {
    const res = await apiClient.get('/dashboard/summary')
    return res.data
  },

  // Module 9: Notifications
  getNotifications: async () => {
    const res = await apiClient.get('/notifications')
    return res.data
  },
  markNotificationRead: async (id: string) => {
    const res = await apiClient.put(`/notifications/${id}/read`)
    return res.data
  },

  // Module 10: Privacy
  exportPrivacyData: async () => {
    const res = await apiClient.post('/privacy/export')
    return res.data
  },

  // Reports
  downloadReportUrl: '/reports/download',
}
