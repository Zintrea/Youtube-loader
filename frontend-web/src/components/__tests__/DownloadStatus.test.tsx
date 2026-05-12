// src/components/__tests__/DownloadStatus.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { SWRConfig } from 'swr'
import { DownloadStatus } from '../DownloadStatus'
import * as apiModule from '../../lib/api'

// Mock the API module
vi.mock('../../lib/api', () => ({
  getJobStatus: vi.fn(),
  startDownload: vi.fn(),
  listDownloads: vi.fn(),
  getFileUrl: vi.fn((filename) => `http://localhost:8000/api/files/${filename}`),
}))

describe('DownloadStatus', () => {
  afterEach(() => {
    vi.clearAllMocks()
  })

  function renderStatus(jobId: string) {
    return render(
      <SWRConfig
        value={{
          dedupingInterval: 0,
          isOnline: () => true,
        }}
      >
        <DownloadStatus jobId={jobId} />
      </SWRConfig>
    )
  }

  it('shows loading indicator initially', async () => {
    vi.mocked(apiModule.getJobStatus).mockImplementation(
      () => new Promise(() => {}) // never resolves
    )

    renderStatus('job-123')
    expect(screen.getByText(/กำลังดาวน์โหลด/i)).toBeInTheDocument()
  })

  it('shows completed state with filename', async () => {
    vi.mocked(apiModule.getJobStatus).mockResolvedValue({
      id: 'job-123',
      url: 'https://youtube.com/watch?v=abc',
      status: 'completed',
      title: 'My Favorite Song',
      filepath: '/videos/song.mp4',
    })

    renderStatus('job-123')
    expect(await screen.findByText(/เสร็จสิ้น/i)).toBeInTheDocument()
    expect(screen.getByText(/my favorite song/i)).toBeInTheDocument()
  })

  it('shows error state when status is error', async () => {
    vi.mocked(apiModule.getJobStatus).mockResolvedValue({
      id: 'job-456',
      url: 'https://youtube.com/watch?v=broken',
      status: 'error',
      error: 'Video is private or unavailable',
    })

    renderStatus('job-456')
    expect(await screen.findByText(/เกิดข้อผิดพลาด/i)).toBeInTheDocument()
    expect(screen.getByText(/video is private or unavailable/i)).toBeInTheDocument()
  })

  it('shows error state when API call fails', async () => {
    vi.mocked(apiModule.getJobStatus).mockRejectedValue(new Error('Network error'))

    renderStatus('job-fail')
    expect(await screen.findByText(/เกิดข้อผิดพลาด/i)).toBeInTheDocument()
  })

  it('shows downloading/processing status', async () => {
    vi.mocked(apiModule.getJobStatus).mockResolvedValue({
      id: 'job-progress',
      url: 'https://youtube.com/watch?v=d0h1',
      status: 'downloading',
    })

    renderStatus('job-progress')
    expect(await screen.findByText(/กำลังดาวน์โหลด/i)).toBeInTheDocument()
  })

  it('shows title when downloading', async () => {
    vi.mocked(apiModule.getJobStatus).mockResolvedValue({
      id: 'job-with-title',
      url: 'https://youtube.com/watch?v=abc',
      status: 'downloading',
      title: 'Cool Video',
    })

    renderStatus('job-with-title')
    expect(await screen.findByText(/cool video/i)).toBeInTheDocument()
  })
})
