'use client'

import { useState, type FormEvent } from 'react'
import { startDownload } from '../lib/api'
import { DownloadStatus } from './DownloadStatus'

const FORMATS = [
  { value: '1080p', label: '1080p' },
  { value: '720p', label: '720p' },
  { value: '480p', label: '480p' },
  { value: 'mp3', label: 'mp3' },
  { value: 'm4a', label: 'm4a' },
]

export function DownloadForm() {
  const [url, setUrl] = useState('')
  const [format, setFormat] = useState('1080p')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [jobId, setJobId] = useState<string | null>(null)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const result = await startDownload(url, format)
      setJobId(result.job_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      setLoading(false)
    }
  }

  if (jobId) {
    return (
      <DownloadStatus jobId={jobId} />
    )
  }

  return (
    <div className="w-full max-w-xl mx-auto p-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        <h1 className="text-2xl font-semibold tracking-tight text-center">
          ดาวน์โหลดวิดีโอ YouTube
        </h1>

        {/* URL Input */}
        <div className="space-y-2">
          <label htmlFor="url-input" className="block text-lg font-medium text-gray-700">
            ลิงก์วิดีโอ
          </label>
          <input
            id="url-input"
            type="text"
            aria-label="วางลิงก์ที่นี่"
            placeholder="วางลิงก์ที่นี่"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="w-full px-4 py-3 text-lg border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Format Selector */}
        <fieldset className="space-y-3">
          <legend className="text-lg font-medium text-gray-700">เลือกรูปแบบ</legend>
          <div className="flex flex-wrap gap-3 sm:gap-4">
            {FORMATS.map((fmt) => (
              <label
                key={fmt.value}
                className="flex items-center gap-2 text-base font-medium cursor-pointer px-4 py-3 border rounded-lg hover:bg-blue-50 min-h-[44px]"
              >
                <input
                  type="radio"
                  name="format"
                  value={fmt.value}
                  checked={format === fmt.value}
                  onChange={() => setFormat(fmt.value)}
                  className="w-5 h-5 accent-blue-600"
                />
                {fmt.label}
              </label>
            ))}
          </div>
        </fieldset>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || url.trim().length === 0}
          className="w-full px-6 py-4 text-xl font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors min-h-[56px] active:scale-[0.98]"
        >
          {loading ? 'กำลังดาวน์โหลด...' : 'ดาวน์โหลด'}
        </button>

        {/* Error Message */}
        {error && (
          <div className="p-4 text-lg text-red-700 bg-red-50 rounded-md border border-red-200">
            เกิดข้อผิดพลาด: {error}
          </div>
        )}
      </form>
    </div>
  )
}
