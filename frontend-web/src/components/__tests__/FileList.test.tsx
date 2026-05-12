// src/components/__tests__/FileList.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, describe, it, beforeEach, expect } from 'vitest'
import FileList from '../FileList'
import * as apiModule from '../../lib/api'

// Mutable mock state for SWR — must use a mutable object reference
// so the mock always returns the latest value
const swrState: {
  data: any
  error: any
  isLoading: boolean
  mutate: () => void
} = {
  data: null,
  error: null,
  isLoading: false,
  mutate: vi.fn(),
}

// Mock SWR
vi.mock('swr', () => ({
  default: vi.fn((_key: any, _fetcher: any, _opts?: any) => swrState),
}))

// Mock the api module with real getFileUrl
vi.mock('../../lib/api', async () => {
  const actual = await vi.importActual<typeof apiModule>('../../lib/api')
  return {
    ...actual,
    listDownloads: vi.fn(),
    deleteFile: vi.fn(),
  }
})

beforeEach(() => {
  vi.clearAllMocks()
  swrState.data = null
  swrState.error = null
  swrState.isLoading = false
  swrState.mutate = vi.fn()
})

describe('FileList', () => {
  describe('empty state', () => {
    it('renders empty message when no files exist', () => {
      swrState.data = { files: [] }
      render(<FileList />)
      expect(screen.getByText('ยังไม่มีไฟล์ที่ดาวน์โหลด')).toBeInTheDocument()
    })

    it('renders empty message when data is undefined (loading)', () => {
      swrState.isLoading = true
      swrState.data = undefined
      render(<FileList />)
      expect(screen.getByText('ยังไม่มีไฟล์ที่ดาวน์โหลด')).toBeInTheDocument()
    })
  })

  describe('file cards', () => {
    it('renders file cards when files exist', () => {
      swrState.data = { files: ['video1.mp4', 'audio.mp3'] }
      render(<FileList />)
      expect(screen.getByText('video1.mp4')).toBeInTheDocument()
      expect(screen.getByText('audio.mp3')).toBeInTheDocument()
    })

    it('truncates long file names and shows title attribute', () => {
      const longName = 'a'.repeat(100) + '.mp4'
      swrState.data = { files: [longName] }
      render(<FileList />)
      const nameEl = screen.getByRole('cell', { name: longName })
      expect(nameEl).toHaveAttribute('title', longName)
    })
  })

  describe('play/download button', () => {
    it('links to the correct file URL', () => {
      swrState.data = { files: ['video1.mp4'] }
      render(<FileList />)
      const link = screen.getByRole('link', { name: /ดู\/เล่น/i })
      expect(link).toBeInTheDocument()
      expect(link).toHaveAttribute('href', 'http://localhost:8000/api/files/video1.mp4')
    })
  })

  describe('delete functionality', () => {
    it('shows the delete button for each file', () => {
      swrState.data = { files: ['video1.mp4'] }
      render(<FileList />)
      expect(screen.getByRole('button', { name: /ลบ/i })).toBeInTheDocument()
    })

    it('calls deleteFile and revalidates when delete is confirmed', async () => {
      vi.mocked(apiModule.deleteFile).mockResolvedValue(undefined)
      swrState.data = { files: ['video1.mp4'] }

      render(<FileList />)

      const deleteBtn = screen.getByRole('button', { name: /ลบ video1/i })
      fireEvent.click(deleteBtn)

      // Confirmation dialog appears
      expect(screen.getByText(/ต้องการลบไฟล์/i)).toBeInTheDocument()

      const confirmBtn = screen.getByRole('button', { name: /ยืนยัน/i })
      fireEvent.click(confirmBtn)

      await waitFor(() => {
        expect(vi.mocked(apiModule.deleteFile)).toHaveBeenCalledWith('video1.mp4')
        expect(swrState.mutate).toHaveBeenCalled()
      })
    })

    it('does not call deleteFile when user cancels confirmation', async () => {
      swrState.data = { files: ['video1.mp4'] }
      render(<FileList />)

      const deleteBtn = screen.getByRole('button', { name: /ลบ/i })
      fireEvent.click(deleteBtn)

      const cancelBtn = screen.getByRole('button', { name: /ยกเลิก/i })
      fireEvent.click(cancelBtn)

      expect(vi.mocked(apiModule.deleteFile)).not.toHaveBeenCalled()
    })

    it('handles delete error gracefully', async () => {
      vi.mocked(apiModule.deleteFile).mockRejectedValue(new Error('Delete failed'))
      swrState.data = { files: ['video1.mp4'] }
      vi.spyOn(console, 'error').mockImplementation(() => {})

      render(<FileList />)

      const deleteBtn = screen.getByRole('button', { name: /ลบ/i })
      fireEvent.click(deleteBtn)

      const confirmBtn = screen.getByRole('button', { name: /ยืนยัน/i })
      fireEvent.click(confirmBtn)

      await waitFor(() => {
        expect(console.error).toHaveBeenCalled()
      })
    })
  })
})
