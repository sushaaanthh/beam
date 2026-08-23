import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { AnalysisPage } from '../AnalysisPage'
import * as analysisApi from '../../services/api/analysis'
import type { AnalysisCreatedResponse, AnalysisDetail } from '../../types/analysis'

vi.mock('../../services/api/analysis', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../services/api/analysis')>()
  return {
    ...actual,
    createAnalysis: vi.fn(),
    fetchAnalysis: vi.fn(),
    deleteAnalysis: vi.fn(),
    fetchAnalysisHistory: vi.fn(),
  }
})

const mockedCreate = vi.mocked(analysisApi.createAnalysis)
const mockedFetch = vi.mocked(analysisApi.fetchAnalysis)

const SESSION_ID = '11111111-1111-1111-1111-111111111111'

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/analysis']}>
      <AnalysisPage />
    </MemoryRouter>,
  )
}

function makeDetail(overrides: Partial<AnalysisDetail> = {}): AnalysisDetail {
  return {
    session_id: SESSION_ID,
    status: 'completed',
    source_type: 'text',
    title: null,
    created_at: '2026-08-23T12:00:00Z',
    completed_at: '2026-08-23T12:00:01Z',
    primary_emotion: null,
    confidence: null,
    model_name: null,
    input: {
      char_count: 24,
      word_count: 4,
      raw_text: 'sample text for testing.',
      created_at: '2026-08-23T12:00:00Z',
    },
    prediction: null,
    behavior_metrics: null,
    explanation: null,
    model_info: {
      model_name: 'beam-mock',
      model_version: null,
      deployed: false,
      note: 'The B.E.A.M. transformer is not deployed yet.',
    },
    ...overrides,
  }
}

async function submitSampleText(text: string) {
  const user = userEvent.setup()
  await user.type(screen.getByPlaceholderText(/paste text to analyze/i), text)
  await user.click(screen.getByRole('button', { name: /^analyze$/i }))
  return user
}

describe('AnalysisPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the editor, counters and controls', () => {
    renderPage()

    expect(screen.getByRole('heading', { level: 1, name: /analyze/i })).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/paste text to analyze/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /clear/i })).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /upload text file/i }),
    ).toBeInTheDocument()
  })

  it('shows a validation error on empty submit and never calls the API', async () => {
    renderPage()
    await submitSampleText('   ')

    expect(await screen.findByRole('alert')).toHaveTextContent(/enter or paste some text/i)
    expect(mockedCreate).not.toHaveBeenCalled()
  })

  it('creates a session and renders the result workspace with unavailability markers', async () => {
    mockedCreate.mockResolvedValueOnce({
      session_id: SESSION_ID,
      status: 'completed',
    } satisfies AnalysisCreatedResponse)
    mockedFetch.mockResolvedValueOnce(makeDetail())

    renderPage()
    await submitSampleText('sample text for testing.')

    await waitFor(() => expect(mockedCreate).toHaveBeenCalledTimes(1))
    expect(mockedCreate).toHaveBeenCalledWith({
      text: 'sample text for testing.',
      source_type: 'text',
    })

    // Result workspace renders with explicit unavailability markers.
    expect(await screen.findByText(/primary emotion/i)).toBeInTheDocument()
    expect(screen.getAllByText(/pending model/i).length).toBeGreaterThan(0)
    expect(screen.getAllByText(/not deployed/i).length).toBeGreaterThan(0)

    // No fabricated predictions are ever displayed.
    expect(screen.queryByText(/joy|frustration|excitement/i)).not.toBeInTheDocument()
  })

  it('keeps a restrained processing state visible while the session is pending', async () => {
    let polls = 0
    mockedCreate.mockResolvedValueOnce({
      session_id: SESSION_ID,
      status: 'processing',
    } satisfies AnalysisCreatedResponse)
    mockedFetch.mockImplementation(async () => {
      polls += 1
      return makeDetail(polls >= 2 ? {} : { status: 'processing' })
    })

    renderPage()
    await submitSampleText('sample text for testing.')

    expect(await screen.findByRole('status')).toBeInTheDocument()
    expect(screen.getByText(/analyzing text/i)).toBeInTheDocument()

    await waitFor(() => expect(polls).toBeGreaterThanOrEqual(2), { timeout: 4000 })
    expect(await screen.findByText(/inference report/i)).toBeInTheDocument()
  })

  it('surfaces a server error message without exposing internals', async () => {
    mockedCreate.mockRejectedValueOnce(
      Object.assign(new Error('boom'), {
        isAxiosError: true,
        response: { status: 500, data: { detail: 'Internal server error' } },
      }),
    )

    renderPage()
    await submitSampleText('sample text for testing.')

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/could not complete the analysis/i)
    expect(screen.queryByText(/stack|traceback|boom/i)).not.toBeInTheDocument()
  })
})
