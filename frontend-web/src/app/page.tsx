import { DownloadForm } from '../components/DownloadForm'

export default function Home() {
  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-white font-sans">
      <main className="flex flex-1 w-full max-w-3xl flex-col items-center justify-center py-16 px-4">
        <DownloadForm />
      </main>
    </div>
  )
}
