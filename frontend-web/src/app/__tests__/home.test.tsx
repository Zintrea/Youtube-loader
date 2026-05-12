import { render, screen } from '@testing-library/react'
import Home from '../page'

vi.mock('../../lib/api', () => ({
  startDownload: vi.fn().mockResolvedValue({ job_id: 'test', status: 'pending' }),
  getJobStatus: vi.fn(),
  listDownloads: vi.fn(),
}))

describe('Home Page', () => {
  it('renders the download form with heading', () => {
    render(<Home />)
    const heading = screen.getByRole('heading', {
      name: /ดาวน์โหลดวิดีโอ youtube/i,
    })
    expect(heading).toBeInTheDocument()
  })

  it('renders the URL input field', () => {
    render(<Home />)
    const input = screen.getByRole('textbox', { name: /วางลิงก์ที่นี่/i })
    expect(input).toBeInTheDocument()
  })
})
