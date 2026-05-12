# 📥 YouTube Loader

> ดาวน์โหลดวิดีโอและเสียงจาก YouTube — ง่าย, เร็ว, ใช้งานได้ผ่านมือถือทุกที่

Full-stack YouTube downloader with a **FastAPI backend** and **Next.js frontend**. Designed to be simple enough for anyone in your family to use — paste a link, preview the video, pick a format, and download. **Works as a PWA (installable app on your phone)** and runs on the cloud — accessible from anywhere.

---

## ✨ Features

- 🎬 **Download YouTube videos** in 1080p, 720p, or 480p (MP4)
- 🎵 **Extract audio** as MP3 (320kbps) or M4A
- 📱 **PWA installable** — Add to Home Screen for app-like experience on iOS & Android
- 👀 **Video preview** — See thumbnail, title, and duration before downloading
- 📂 **File management** — browse, play, and delete downloaded files from the web
- 🔄 **Async downloads** — start a download and the UI polls for status automatically
- 🔁 **Download again** — After completion, tap "ดาวน์โหลดวิดีโอใหม่" to download another
- 🧪 **136 tests** (95 backend + 41 frontend) — TDD throughout
- 🐳 **Docker & Cloud ready** — Deploy to Render + Cloudflare Pages

---

## 📱 How to Install (Add to Home Screen)

### Android (Chrome)
1. Open the website in Chrome
2. Tap the menu (⋮) → **"Add to Home screen"**
3. Choose a name → Tap **Add**
4. Icon appears on your home screen — tap to open like an app!

### iOS (Safari)
1. Open the website in Safari
2. Tap the **Share** button (box with arrow)
3. Tap **"Add to Home Screen"**
4. Confirm → Icon appears on your home screen!

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (Next.js)                │
│  localhost:3000  │  Mobile browser  │  Desktop      │
│  ┌─────────────────────────────────────────────┐    │
│  │  DownloadForm  │  DownloadStatus  │  FileList │   │
│  └──────────────┬──────────────────────────────┘    │
│                 │ HTTP (CORS)                        │
└─────────────────┼────────────────────────────────────┘
                  │
┌─────────────────▼────────────────────────────────────┐
│                   Backend (FastAPI)                  │
│  localhost:8000                                      │
│  ┌───────────┬─────────────┬────────────┐           │
│  │ Download  │  File       │  Video     │           │
│  │ Router    │  Router     │  Info      │           │
│  └─────┬─────┴──────┬──────┴──────┬─────┘           │
│        │            │             │                  │
│  ┌─────▼─────┐  ┌───▼────────────▼───┐              │
│  │ Youtube    │  │ FileStorage +      │              │
│  │ Service    │  │ JobStorage (SQLite)│              │
│  │ (yt-dlp)   │  │                    │              │
│  └───────────┘  └────────────────────┘              │
└─────────────────────────────────────────────────────┘
```

### Project Structure

```
youtube-loader/
├── backend-api/
│   ├── Main.py                    # FastAPI app entrypoint
│   ├── Requirements.txt           # Python dependencies
│   ├── config_settings/AppConfig.py
│   ├── core_services/
│   │   ├── YoutubeService.py      # yt-dlp wrapper
│   │   ├── FileStorageService.py  # File management
│   │   └── JobStorageService.py  # SQLite persistent job storage
│   ├── api_routes/
│   │   ├── DownloadRouter.py      # POST /api/download, GET /api/download/{id}, GET /api/video-info
│   │   ├── FileRouter.py          # GET/DELETE /api/files/{name}
│   │   └── StatusRouter.py        # GET /api/status
│   └── api_models/DownloadRequest.py
├── frontend-web/
│   ├── src/
│   │   ├── app/page.tsx
│   │   ├── components/
│   │   │   ├── DownloadForm.tsx   # URL + format + video preview
│   │   │   ├── DownloadStatus.tsx # Status polling + download again button
│   │   │   └── FileList.tsx       # File list with play/delete
│   │   └── lib/api.ts
│   ├── public/manifest.json       # PWA manifest
│   ├── public/sw.js               # Service worker
│   └── vitest.config.ts
├── tests/                         # Backend tests (pytest)
├── render.yaml                    # Deploy config for Render
├── start.bat                      # One-click dev server launcher
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** (backend)
- **Node.js 18+** (frontend)
- **FFmpeg** — required by yt-dlp for merging video+audio
  - Windows: `winget install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt install ffmpeg`

### Windows One-Click Start
```bash
start.bat
```

### Manual Start
```bash
# Backend
cd backend-api
..\venv\Scripts\python.exe Main.py
# → API running at http://localhost:8000

# Frontend (new terminal)
cd frontend-web
npm run dev
# → Frontend running at http://localhost:3000
```

### Run Tests

```bash
# Backend
cd backend-api && ..\venv\Scripts\python.exe -m pytest ../tests/ -v

# Frontend
cd frontend-web && npm test
```

---

## 📡 API Endpoints

### Download

| Method | Path | Body | Description |
|--------|------|------|-------------|
| `POST` | `/api/download` | `{ url, output_format }` | Start a download (returns `job_id`) |
| `GET`  | `/api/download/{job_id}` | — | Check download status |

**Video Preview**

| Method | Path | Query | Description |
|--------|------|-------|-------------|
| `GET`  | `/api/video-info` | `url=...` | Get title, duration, thumbnail before downloading |

**Supported formats:** `1080p`, `720p`, `480p`, `mp3`, `m4a`

### Files

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/files` | List all downloaded files |
| `GET` | `/api/files/{filename}` | Download/stream a specific file |
| `DELETE` | `/api/files/{filename}` | Delete a file |

### System

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/status` | Health check |

---

## 🧪 Test Coverage

```
Backend:  95 tests  (config, services, API routes, file management, job storage, video info)
Frontend: 41 tests  (API client, components, integration)
Total:    136 tests
```

Every feature was built TDD-style: red → green → refactor.

---

## 🔧 Customization

### Add Download Formats
Edit `backend-api/core_services/YoutubeService.py` and add a new format to `_get_format_opts()`.

### Change Default Download Directory
Edit `backend-api/config_settings/AppConfig.py`

### Add CORS Origins for Production
Set the environment variable:
```bash
export CORS_ORIGINS="http://localhost:3000,https://your-domain.com"
```

---

## 📝 What's New (v0.2.0)

- ✅ **Persistent job storage** — SQLite replaces in-memory dict, jobs survive server restarts
- ✅ **Video preview** — Thumbnail, title, and duration shown before downloading
- ✅ **Download again** — Button to download a new video after completion
- ✅ **PWA support** — Installable on iOS and Android home screens
- ✅ **Bug fixes** — `import os` in Main.py, Windows file overwrite compatibility

---

## 📋 Roadmap

- [ ] WebSocket real-time download progress (percentage)
- [ ] Playlist support (download all videos in a playlist)
- [ ] User authentication (protected downloads)
- [ ] Dark mode toggle
- [ ] Subtitle download
- [ ] Browser extension for one-click downloads

---

## 📄 License

MIT

---

*Built with ❤️ for family — simple enough for mom, powerful enough for devs.*
