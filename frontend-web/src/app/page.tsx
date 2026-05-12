import { DownloadForm } from '../components/DownloadForm'
import FileList from '../components/FileList'

export default function Home() {
  return (
    <div className="flex flex-col flex-1 items-center bg-white font-sans">
      <main className="flex flex-1 w-full max-w-3xl flex-col items-center py-8 sm:py-12 lg:py-16 px-4 sm:px-6 gap-8 sm:gap-12">
        <div className="w-full px-2 sm:px-4">
          <DownloadForm />
        </div>

        <div className="w-full border-t border-gray-200" />

        <div className="w-full px-2 sm:px-4">
          <FileList />
        </div>
      </main>
    </div>
  )
}
