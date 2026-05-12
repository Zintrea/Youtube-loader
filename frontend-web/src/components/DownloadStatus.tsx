'use client'

import { useEffect, useState } from 'react'
import { getJobStatus, getFileUrl } from '../lib/api'
import type { JobStatus } from '../lib/api'

export function DownloadStatus({ jobId, onNewDownload }: { jobId: string; onNewDownload?: () => void }) {
  const [status, setStatus] = useState<JobStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await getJobStatus(jobId)
        setStatus(data)
        setLoading(false)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch status')
        setLoading(false)
      }
    }

    // Initial fetch
    fetchStatus()

    // Poll every 3 seconds
    const interval = setInterval(fetchStatus, 3000)

    return () => clearInterval(interval)
  }, [jobId])

  if (loading) {
    return (
      <div className="w-full max-w-xl mx-auto p-6 text-center space-y-4">
        <div className="animate-pulse text-lg text-gray-600">กำลังดาวน์โหลด...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="w-full max-w-xl mx-auto p-6">
        <div className="p-4 text-lg text-red-700 bg-red-50 rounded-md border border-red-200">
          เกิดข้อผิดพลาด: {error}
        </div>
      </div>
    )
  }

  if (!status) return null

  if (status.status === 'error') {
    return (
      <div className="w-full max-w-xl mx-auto p-6 space-y-4">
        <div className="p-4 text-lg text-red-700 bg-red-50 rounded-md border border-red-200">
          เกิดข้อผิดพลาด: {status.error || 'เกิดข้อผิดพลาดในการดาวน์โหลด'}
        </div>
        {onNewDownload && (
          <button
            onClick={onNewDownload}
            className="w-full px-6 py-4 text-xl font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors min-h-[56px] active:scale-[0.98]"
          >
            ดาวน์โหลดวิดีโอใหม่
          </button>
        )}
      </div>
    )
  }

  if (status.status === 'completed') {
    return (
      <div className="w-full max-w-xl mx-auto p-6 text-center space-y-4">
        <div className="text-lg text-green-700 bg-green-50 rounded-md border border-green-200 p-4">
         เสร็จสิ้น
        </div>
        {status.title && (
          <p className="text-lg text-gray-700">{status.title}</p>
        )}
        {status.filepath && (
          <div className="pt-2">
            <a
              href={getFileUrl(status.filepath.split('/').pop() || status.filepath)}
              className="inline-block px-6 py-3 text-lg font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors"
              download
            >
              ดาวน์โหลดไฟล์
            </a>
          </div>
        )}
        {onNewDownload && (
          <button
            onClick={onNewDownload}
            className="w-full px-6 py-4 text-xl font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors min-h-[56px] active:scale-[0.98]"
          >
            ดาวน์โหลดวิดีโอใหม่
          </button>
        )}
      </div>
    )
  }

  // downloading / processing
  return (
    <div className="w-full max-w-xl mx-auto p-6 text-center space-y-4">
      <div className="animate-pulse text-lg text-blue-700 bg-blue-50 rounded-md border border-blue-200 p-4">
        กำลังดาวน์โหลด...
      </div>
      {status.title && (
        <p className="text-lg text-gray-600">{status.title}</p>
      )}
    </div>
  )
}
