'use client'

import { useState } from 'react'
import useSWR from 'swr'
import { listDownloads, getFileUrl, deleteFile } from '../lib/api'

export default function FileList() {
  const { data, error, mutate } = useSWR('/api/files', () => listDownloads(), {
    refreshInterval: 10_000,
    revalidateOnFocus: true,
  })
  const [pendingDelete, setPendingDelete] = useState<string | null>(null)

  const handleDelete = async (filename: string) => {
    try {
      await deleteFile(filename)
      mutate()
    } catch (err) {
      console.error('Delete failed:', err)
    } finally {
      setPendingDelete(null)
    }
  }

  if (error) {
    return (
      <div className="w-full max-w-2xl mx-auto p-4">
        <p className="text-red-600 text-lg">เกิดข้อผิดพลาดในการโหลดรายการ</p>
      </div>
    )
  }

  const files = data?.files ?? []

  return (
    <div className="w-full max-w-2xl mx-auto px-4">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">ไฟล์ที่ดาวน์โหลด</h2>

      {/* Confirmation dialog */}
      {pendingDelete && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" role="dialog" aria-modal="true">
          <div className="bg-white rounded-lg p-6 max-w-sm w-full shadow-xl">
            <p className="text-lg text-gray-800 mb-4">ต้องการลบไฟล์ &quot;{pendingDelete}&quot; ใช่หรือไม่?</p>
            <div className="flex gap-3">
              <button
                onClick={() => setPendingDelete(null)}
                className="flex-1 px-4 py-3 min-h-[44px] rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors text-base font-medium"
              >
                ยกเลิก
              </button>
              <button
                onClick={() => handleDelete(pendingDelete)}
                className="flex-1 px-4 py-3 min-h-[44px] rounded-md bg-red-600 text-white hover:bg-red-700 transition-colors text-base font-medium"
              >
                ยืนยัน
              </button>
            </div>
          </div>
        </div>
      )}

      {files.length === 0 ? (
        <p className="text-gray-500 text-lg py-8 text-center">ยังไม่มีไฟล์ที่ดาวน์โหลด</p>
      ) : (
        <div className="space-y-3">
          {files.map((filename) => (
            <div
              key={filename}
              className="table-row-group flex items-center gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200"
            >
              <span
                className="flex-1 truncate text-base font-medium text-gray-900 min-w-0"
                title={filename}
                role="cell"
                aria-label={filename}
              >
                {filename}
              </span>
              <a
                href={getFileUrl(filename)}
                className="flex-shrink-0 w-11 h-11 flex items-center justify-center rounded-md bg-blue-600 text-white hover:bg-blue-700 transition-colors min-w-[44px] min-h-[44px]"
                aria-label={`ดู/เล่น ${filename}`}
              >
                ▶
              </a>
              <button
                onClick={() => setPendingDelete(filename)}
                className="flex-shrink-0 w-11 h-11 flex items-center justify-center rounded-md bg-red-600 text-white hover:bg-red-700 transition-colors min-w-[44px] min-h-[44px]"
                aria-label={`ลบ ${filename}`}
              >
                🗑
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
