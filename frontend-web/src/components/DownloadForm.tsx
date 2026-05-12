'use client'

import { useState, type FormEvent, useCallback, useRef, useEffect } from 'react'
import { startDownload, getVideoInfo } from '../lib/api'
import type { VideoInfo } from '../lib/api'
import { DownloadStatus } from './DownloadStatus'

const FORMATS = [
  { value: '1080p', label: '1080p' },
  { value: '720p', label: '720p' },
  { value: '480p', label: '480p' },
  { value: 'mp3', label: 'mp3' },
  { value: 'm4a', label: 'm4a' },
]

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

function isValidYouTubeUrl(url: string): boolean {
  return url.includes('youtube.com') || url.includes('youtu.be')
}

export function DownloadForm() {
  const [url, setUrl] = useState('')
  const [format, setFormat] = useState('720p')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [jobId, setJobId] = useState<string | null>(null)

  // Video preview state
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null)
  const [fetchingInfo, setFetchingInfo] = useState(false)
  const [infoError, setInfoError] = useState<string | null>(null)

  const fetchTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  const fetchVideoInfo = useCallback(async (videoUrl: string) => {
    if (!isValidYouTubeUrl(videoUrl)) {
      setVideoInfo(null)
      setInfoError(null)
      return
    }

    setFetchingInfo(true)
    setInfoError(null)

    // Cancel any previous in-flight request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    abortControllerRef.current = new AbortController()

    try {
      const info = await getVideoInfo(videoUrl)
      if (info.error) {
        setInfoError(info.error)
        setVideoInfo(null)
      } else {
        setVideoInfo(info)
        setInfoError(null)
      }
    } catch {
      setInfoError('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้')
      setVideoInfo(null)
    } finally {
      setFetchingInfo(false)
    }
  }, [])

  // Debounced fetch when URL changes and is valid
  const handleUrlChange = useCallback((value: string) => {
    setUrl(value)
    setVideoInfo(null)
    setInfoError(null)

    if (fetchTimeoutRef.current) {
      clearTimeout(fetchTimeoutRef.current)
    }

    if (isValidYouTubeUrl(value) && value.trim().length > 0) {
      fetchTimeoutRef.current = setTimeout(() => {
        fetchVideoInfo(value)
      }, 500)
    }
  }, [fetchVideoInfo])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (fetchTimeoutRef.current) clearTimeout(fetchTimeoutRef.current)
      if (abortControllerRef.current) abortControllerRef.current.abort()
    }
  }, [])

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

  // After successful download start, show status
  if (jobId) {
    return <DownloadStatus jobId={jobId} onNewDownload={() => {
      setJobId(null)
      setUrl('')
      setVideoInfo(null)
      setInfoError(null)
    }} />
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
            onChange={(e) => handleUrlChange(e.target.value)}
            onBlur={() => {
              if (isValidYouTubeUrl(url) && url.trim().length > 0 && !videoInfo && !fetchingInfo) {
                fetchVideoInfo(url)
              }
            }}
            className="w-full px-4 py-3 text-lg border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Video Preview */}
        {fetchingInfo && (
          <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-lg text-gray-600">กำลังดึงข้อมูลวิดีโอ...</span>
          </div>
        )}

        {infoError && (
          <div className="p-4 text-lg text-red-700 bg-red-50 rounded-md border border-red-200">
            ไม่สามารถดึงข้อมูลวิดีโอ: {infoError}
          </div>
        )}

        {videoInfo && (
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200 space-y-3">
            <div className="flex gap-4">
              {videoInfo.thumbnail && (
                <img
                  src={videoInfo.thumbnail}
                  alt={videoInfo.title || 'Video thumbnail'}
                  className="w-40 h-auto rounded-md object-cover"
                />
              )}
              <div className="flex flex-col justify-center">
                <h2 className="text-lg font-semibold text-gray-900">{videoInfo.title}</h2>
                {videoInfo.duration && (
                  <p className="text-base text-gray-600 mt-1">
                    ความยาว: {formatDuration(videoInfo.duration)}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

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
