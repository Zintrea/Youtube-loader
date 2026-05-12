// src/components/__tests__/DownloadForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { DownloadForm } from '../DownloadForm'

// Mock the API module
vi.mock('../../lib/api', () => ({
  startDownload: vi.fn().mockResolvedValue({ job_id: 'test-default', status: 'pending' }),
  getJobStatus: vi.fn(),
  listDownloads: vi.fn(),
}))

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

  it('has a submit button with disabled state when URL is empty', () => {
    render(<DownloadForm />)
    const submitButton = screen.getByRole('button', { name: /ดาวน์โหลด/i })
    expect(submitButton).toBeDisabled()
  })

  it('enables submit button when URL and format are valid', () => {
    render(<DownloadForm />)
    const urlInput = screen.getByRole('textbox', { name: /วางลิงก์ที่นี่/i })
    fireEvent.change(urlInput, { target: { value: 'https://youtube.com/watch?v=xyz123' } })

    // Select 720p radio
    fireEvent.click(screen.getByRole('radio', { name: '720p' }))

    const submitButton = screen.getByRole('button', { name: /ดาวน์โหลด/i })
    expect(submitButton).not.toBeDisabled()
  })

  it('disables submit button when only format is selected but URL is empty', () => {
    render(<DownloadForm />)
    fireEvent.click(screen.getByRole('radio', { name: '1080p' }))
    const submitButton = screen.getByRole('button', { name: /ดาวน์โหลด/i })
    expect(submitButton).toBeDisabled()
  })

  it('calls startDownload with correct values when form is submitted', async () => {
    const apiModule = await import('../../lib/api')
    vi.mocked(apiModule.startDownload).mockResolvedValue({ job_id: 'test-123', status: 'pending' })

    render(<DownloadForm />)

    // Fill URL
    fireEvent.change(screen.getByRole('textbox', { name: /วางลิงก์ที่นี่/i }), {
      target: { value: 'https://www.youtube.com/watch?v=abc' },
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
    // Use a promise that we control
    let resolveFn: (value: any) => void
    const slowPromise = new Promise<any>((resolve) => {
      resolveFn = resolve
    })
    vi.mocked(apiModule.startDownload).mockReturnValue(slowPromise)

    render(<DownloadForm />)

    // Fill form and submit
    fireEvent.change(screen.getByRole('textbox', { name: /วางลิงก์ที่นี่/i }), {
      target: { value: 'https://youtube.com/watch?v=xyz' },
    })
    fireEvent.click(screen.getByRole('radio', { name: 'm4a' }))
    fireEvent.click(screen.getByRole('button', { name: /ดาวน์โหลด/i }))

    // Button text should change to loading state
    const button = await screen.findByRole('button', { name: /กำลังดาวน์โหลด/i })
    expect(button).toBeDisabled()

    // Resolve and wait for form to disappear
    resolveFn!({ job_id: 'job1', status: 'pending' })
    await waitFor(() => {
      expect(screen.queryByRole('button')).not.toBeInTheDocument()
    })
  })

  it('shows error message when API call fails', async () => {
    const apiModule = await import('../../lib/api')
    vi.mocked(apiModule.startDownload).mockRejectedValue(new Error('Download failed'))

    render(<DownloadForm />)

    fireEvent.change(screen.getByRole('textbox', { name: /วางลิงก์ที่นี่/i }), {
      target: { value: 'https://youtube.com/watch?v=xyz' },
    })
    fireEvent.click(screen.getByRole('radio', { name: '1080p' }))
    fireEvent.click(screen.getByRole('button', { name: /ดาวน์โหลด/i }))

    expect(await screen.findByText(/เกิดข้อผิดพลาด/i)).toBeInTheDocument()
  })

  it('transitions to DownloadStatus after successful download', async () => {
    const apiModule = await import('../../lib/api')
    vi.mocked(apiModule.startDownload).mockResolvedValue({ job_id: 'job-reset', status: 'pending' })

    render(<DownloadForm />)

    fireEvent.change(screen.getByRole('textbox', { name: /วางลิงก์ที่นี่/i }), {
      target: { value: 'https://youtube.com/watch?v=xyz' },
    })
    fireEvent.click(screen.getByRole('radio', { name: '480p' }))
    fireEvent.click(screen.getByRole('button', { name: /ดาวน์โหลด/i }))

    // After successful start, form transitions to status view (no more submit button)
    await waitFor(() => {
      expect(screen.queryByRole('button', { name: /ดาวน์โหลด/i })).not.toBeInTheDocument()
    })
  })
})
