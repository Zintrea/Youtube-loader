'use client'

import { useEffect, useState } from 'react'
import { getJobStatus } from '../lib/api'
import type { JobStatus } from '../lib/api'

export function DownloadStatus({ jobId }: { jobId: string }) {
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
      <div className="w-full max-w-xl mx-auto p-6">
        <div className="p-4 text-lg text-red-700 bg-red-50 rounded-md border border-red-200">
          เกิดข้อผิดพลาด: {status.error || 'เกิดข้อผิดพลาดในการดาวน์โหลด'}
        </div>
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
          <p className="text-lg text-gray-700">
            {status.title}
          </p>
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
