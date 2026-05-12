// src/lib/__tests__/api.test.ts

import { startDownload, getJobStatus, listDownloads, getFileUrl, deleteFile } from '../api'

const API_BASE = 'http://localhost:8000'

// Mock environment
vi.stubEnv('NEXT_PUBLIC_API_URL', API_BASE)

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('API client', () => {
  describe('startDownload', () => {
    it('calls POST /api/download with correct body', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ job_id: 'abc123', status: 'pending' }),
      })
      vi.stubGlobal('fetch', mockFetch)

      const result = await startDownload('https://youtube.com/watch?v=xyz', '1080p')

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE}/api/download`,
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            url: 'https://youtube.com/watch?v=xyz',
            output_format: '1080p',
          }),
        })
      )
      expect(result).toEqual({ job_id: 'abc123', status: 'pending' })
    })

    it('throws on non-ok response', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => ({ error: 'Server error' }),
      })
      vi.stubGlobal('fetch', mockFetch)

      await expect(
        startDownload('https://youtube.com/watch?v=xyz', 'mp3')
      ).rejects.toThrow('Failed')
    })
  })

  describe('getJobStatus', () => {
    it('calls GET /api/download/{job_id}', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          id: 'job42',
          url: 'https://youtube.com/watch?v=abc',
          status: 'completed',
          title: 'Test Video',
          filepath: '/path/to/file.mp4',
        }),
      })
      vi.stubGlobal('fetch', mockFetch)

      const result = await getJobStatus('job42')

      expect(mockFetch).toHaveBeenCalledWith(`${API_BASE}/api/download/job42`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      })
      expect(result).toEqual({
        id: 'job42',
        url: 'https://youtube.com/watch?v=abc',
        status: 'completed',
        title: 'Test Video',
        filepath: '/path/to/file.mp4',
      })
    })

    it('throws when job not found', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        json: async () => ({ error: 'Not found' }),
      })
      vi.stubGlobal('fetch', mockFetch)

      await expect(getJobStatus('nonexistent'))
        .rejects.toThrow('Failed')
    })
  })

  describe('listDownloads', () => {
    it('calls GET /api/downloads and returns file list', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          files: ['video1.mp4', 'audio.mp3'],
        }),
      })
      vi.stubGlobal('fetch', mockFetch)

      const result = await listDownloads()

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE}/api/downloads`,
        {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        }
      )
      expect(result).toEqual({ files: ['video1.mp4', 'audio.mp3'] })
    })

    it('throws on error response', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
      })
      vi.stubGlobal('fetch', mockFetch)

      await expect(listDownloads()).rejects.toThrow('Failed')
    })
  })

  describe('getFileUrl', () => {
    it('returns correct URL for a simple filename', () => {
      const url = getFileUrl('video.mp4')
      expect(url).toBe(`${API_BASE}/api/files/video.mp4`)
    })

    it('encodes special characters in filename', () => {
      const url = getFileUrl('my video (1).mp4')
      expect(url).toBe(`${API_BASE}/api/files/my%20video%20(1).mp4`)
    })
  })

  describe('deleteFile', () => {
    it('calls DELETE /api/files/{filename}', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({}),
      })
      vi.stubGlobal('fetch', mockFetch)

      await deleteFile('video.mp4')

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE}/api/files/video.mp4`,
        expect.objectContaining({
          method: 'DELETE',
        })
      )
    })

    it('throws on non-ok response', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
      })
      vi.stubGlobal('fetch', mockFetch)

      await expect(deleteFile('nonexistent.mp4')).rejects.toThrow('Failed')
    })
  })
})
