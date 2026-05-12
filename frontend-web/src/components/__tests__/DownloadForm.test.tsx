// src/components/__tests__/DownloadForm.test.tsx
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { DownloadForm } from '../DownloadForm'

// Mock the API module
vi.mock('../../lib/api', () => ({
  startDownload: vi.fn().mockResolvedValue({ job_id: 'test-default', status: 'pending' }),
  getJobStatus: vi.fn(),
  listDownloads: vi.fn(),
  getVideoInfo: vi.fn(),
}))

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

describe('DownloadForm', () => {
  it('renders the form with title and URL input', () => {
    render(<DownloadForm />)
    expect(screen.getByRole('heading', { name: /ดาวน์โหลดวิดีโอ youtube/i })).toBeInTheDocument()
    expect(screen.getByRole('textbox', { name: /วางลิงก์ที่นี่/i })).toBeInTheDocument()
  })

  it('renders format selector with all options', () => {
    render(<DownloadForm />)
    const formats = ['1080p', '720p', '480p', 'mp3', 'm4a']
    formats.forEach((fmt) => {
      expect(screen.getByRole('radio', { name: fmt })).toBeInTheDocument()
    })
  })

  it('has a submit button disabled when URL is empty', () => {
    render(<DownloadForm />)
    const submitButton = screen.getByRole('button', { name: /ดาวน์โหลด/i })
    expect(submitButton).toBeDisabled()
  })

  it('fetches and shows video preview when URL is entered', async () => {
    const apiModule = await import('../../lib/api')
    vi.mocked(apiModule.getVideoInfo).mockResolvedValue({
      title: 'Test Video Title',
      duration: 120,
      thumbnail: 'https://img.youtube.com/vi/test/maxresdefault.jpg',
    })

    render(<DownloadForm />)
    const urlInput = screen.getByRole('textbox', { name: /วางลิงก์ที่นี่/i })
    fireEvent.change(urlInput, { target: { value: 'https://youtube.com/watch?v=abc' } })
    // Trigger blur to start fetch
    fireEvent.blur(urlInput)

    await waitFor(() => {
      expect(screen.getByText('Test Video Title')).toBeInTheDocument()
    })
  })

  it('shows error when video info fetch fails', async () => {
    const apiModule = await import('../../lib/api')
    vi.mocked(apiModule.getVideoInfo).mockResolvedValue({
      error: 'Video unavailable',
    })

    render(<DownloadForm />)
    const urlInput = screen.getByRole('textbox', { name: /วางลิงก์ที่นี่/i })
    fireEvent.change(urlInput, { target: { value: 'https://youtube.com/watch?v=bad' } })
    fireEvent.blur(urlInput)

    await waitFor(() => {
      expect(screen.getByText(/ไม่สามารถดึงข้อมูลวิดีโอ/i)).toBeInTheDocument()
    })
  })

  it('shows preview before enabling download', async () => {
    const apiModule = await import('../../lib/api')
    vi.mocked(apiModule.getVideoInfo).mockResolvedValue({
      title: 'My Video',
      duration: 180,
      thumbnail: 'https://img.youtube.com/vi/test/maxresdefault.jpg',
    })

    render(<DownloadForm />)
    const urlInput = screen.getByRole('textbox', { name: /วางลิงก์ที่นี่/i })
    fireEvent.change(urlInput, { target: { value: 'https://youtube.com/watch?v=abc' } })
    fireEvent.blur(urlInput)

    // Wait for preview to appear
    await waitFor(() => {
      expect(screen.getByText('My Video')).toBeInTheDocument()
    })

    // Now select format — download button should still work
    fireEvent.click(screen.getByRole('radio', { name: '720p' }))
    const submitButton = screen.getByRole('button', { name: /ดาวน์โหลด/i })
    expect(submitButton).not.toBeDisabled()
  })

  it('shows duration in human-readable format', async () => {
    const apiModule = await import('../../lib/api')
    vi.mocked(apiModule.getVideoInfo).mockResolvedValue({
      title: 'Test Video',
      duration: 125,
      thumbnail: 'https://img.youtube.com/vi/test/maxresdefault.jpg',
    })

    render(<DownloadForm />)
    const urlInput = screen.getByRole('textbox', { name: /วางลิงก์ที่นี่/i })
    fireEvent.change(urlInput, { target: { value: 'https://youtube.com/watch?v=abc' } })
    fireEvent.blur(urlInput)

    // 125 seconds = 2:05
    await waitFor(() => {
      expect(screen.getByText(/2:05/i)).toBeInTheDocument()
    })
  })

  it('calls startDownload with correct values when form is submitted', async () => {
    const apiModule = await import('../../lib/api')
    vi.mocked(apiModule.getVideoInfo).mockResolvedValue({
      title: 'Test Video',
      duration: 60,
      thumbnail: '',
    })
    vi.mocked(apiModule.startDownload).mockResolvedValue({ job_id: 'test-123', status: 'pending' })

    render(<DownloadForm />)

    // Fill URL and trigger preview
    fireEvent.change(screen.getByRole('textbox', { name: /วางลิงก์ที่นี่/i }), {
      target: { value: 'https://www.youtube.com/watch?v=abc' },
    })
    fireEvent.blur(screen.getByRole('textbox', { name: /วางลิงก์ที่นี่/i }))

    await waitFor(() => {
      expect(screen.getByText('Test Video')).toBeInTheDocument()
    })

    // Select mp3 format
    fireEvent.click(screen.getByRole('radio', { name: 'mp3' }))

    // Submit
    fireEvent.click(screen.getByRole('button', { name: /ดาวน์โหลด/i }))

    expect(apiModule.startDownload).toHaveBeenCalledWith(
      'https://www.youtube.com/watch?v=abc',
      'mp3'
    )
  })

  it('shows loading state on button text when submitting', async () => {
    const apiModule = await import('../../lib/api')
    vi.mocked(apiModule.getVideoInfo).mockResolvedValue({
      title: 'Test Video',
      duration: 60,
      thumbnail: '',
    })

    let resolveFn: (value: any) => void
    const slowPromise = new Promise<any>((resolve) => {
      resolveFn = resolve
    })
    vi.mocked(apiModule.startDownload).mockReturnValue(slowPromise)

    render(<DownloadForm />)

    // Fill form
    fireEvent.change(screen.getByRole('textbox', { name: /วางลิงก์ที่นี่/i }), {
      target: { value: 'https://youtube.com/watch?v=xyz' },
    })
    fireEvent.blur(screen.getByRole('textbox', { name: /วางลิงก์ที่นี่/i }))

    await waitFor(() => {
      expect(screen.getByText('Test Video')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole('radio', { name: 'm4a' }))
    fireEvent.click(screen.getByRole('button', { name: /ดาวน์โหลด/i }))

    // Button text should change to loading state
    await waitFor(() => {
      const button = screen.getByRole('button', { name: /กำลังดาวน์โหลด/i })
      expect(button).toBeDisabled()
    })

    // Resolve and wait for form to disappear
    resolveFn!({ job_id: 'job1', status: 'pending' })
    await waitFor(() => {
      expect(screen.queryByRole('button')).not.toBeInTheDocument()
    })
  })

  it('shows error message when startDownload API call fails', async () => {
    const apiModule = await import('../../lib/api')
    vi.mocked(apiModule.getVideoInfo).mockResolvedValue({
      title: 'Test Video',
      duration: 60,
      thumbnail: '',
    })
    vi.mocked(apiModule.startDownload).mockRejectedValue(new Error('Download failed'))

    render(<DownloadForm />)

    fireEvent.change(screen.getByRole('textbox', { name: /วางลิงก์ที่นี่/i }), {
      target: { value: 'https://youtube.com/watch?v=xyz' },
    })
    fireEvent.blur(screen.getByRole('textbox', { name: /วางลิงก์ที่นี่/i }))

    await waitFor(() => {
      expect(screen.getByText('Test Video')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole('radio', { name: '1080p' }))
    fireEvent.click(screen.getByRole('button', { name: /ดาวน์โหลด/i }))

    expect(await screen.findByText(/เกิดข้อผิดพลาด/i)).toBeInTheDocument()
  })

  it('transitions to DownloadStatus after successful download', async () => {
    const apiModule = await import('../../lib/api')
    vi.mocked(apiModule.getVideoInfo).mockResolvedValue({
      title: 'Test Video',
      duration: 60,
      thumbnail: '',
    })
    vi.mocked(apiModule.startDownload).mockResolvedValue({ job_id: 'job-reset', status: 'pending' })

    render(<DownloadForm />)

    fireEvent.change(screen.getByRole('textbox', { name: /วางลิงก์ที่นี่/i }), {
      target: { value: 'https://youtube.com/watch?v=xyz' },
    })
    fireEvent.blur(screen.getByRole('textbox', { name: /วางลิงก์ที่นี่/i }))

    await waitFor(() => {
      expect(screen.getByText('Test Video')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole('radio', { name: '480p' }))
    fireEvent.click(screen.getByRole('button', { name: /ดาวน์โหลด/i }))

    // After successful start, form transitions to status view (no more submit button)
    await waitFor(() => {
      expect(screen.queryByRole('button', { name: /ดาวน์โหลด/i })).not.toBeInTheDocument()
    })
  })
})
