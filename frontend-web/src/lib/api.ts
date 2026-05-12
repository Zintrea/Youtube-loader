// src/lib/api.ts

const API_BASE =
  typeof import.meta !== 'undefined' && import.meta.env?.NEXT_PUBLIC_API_URL
    ? import.meta.env.NEXT_PUBLIC_API_URL
    : 'http://localhost:8000'

export interface DownloadRequest {
  url: string
  output_format: string
}

export interface DownloadResponse {
  job_id: string
  status: string
}

export interface JobStatus {
  id: string
  url: string
  format?: string
  status: string
  filepath?: string
  title?: string
  error?: string
}

export interface DownloadsList {
  files: string[]
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })

  if (!res.ok) {
    throw new Error(`Failed: ${res.status}`)
  }

  return res.json()
}

export interface VideoInfo {
  title?: string
  duration?: number
  thumbnail?: string
  formats?: Array<{ format_id?: string; ext?: string; quality?: string | number }>
  error?: string
}

export function getVideoInfo(url: string): Promise<VideoInfo> {
  return request(`/api/video-info?url=${encodeURIComponent(url)}`)
}

export function startDownload(url: string, format: string): Promise<DownloadResponse> {
  return request('/api/download', {
    method: 'POST',
    body: JSON.stringify({ url, output_format: format }),
  })
}

export function getJobStatus(jobId: string): Promise<JobStatus> {
  return request(`/api/download/${jobId}`)
}

export function listDownloads(): Promise<DownloadsList> {
  return request('/api/downloads')
}

export function getFileUrl(filename: string): string {
  return `${API_BASE}/api/files/${encodeURIComponent(filename)}`
}

export async function deleteFile(filename: string): Promise<void> {
  await request(`/api/files/${encodeURIComponent(filename)}`, {
    method: 'DELETE',
  })
}
