# 📥 YouTube Loader

> ดาวน์โหลดวิดีโอและเสียงจาก YouTube — ง่าย, เร็ว, ใช้งานได้ผ่านมือถือทุกที่

Full-stack YouTube downloader with a **FastAPI backend** and **Next.js frontend**. Designed to be simple enough for anyone in your family to use — paste a link, pick a format, and download. Works on mobile and desktop browsers.

---

## ✨ Features

- 🎬 **Download YouTube videos** in 1080p, 720p, or 480p (MP4)
- 🎵 **Extract audio** as MP3 (320kbps) or M4A
- 📱 **Mobile-friendly UI** with large touch targets — works great on phones
- 📂 **File management** — browse, play, and delete downloaded files from the web
- 🔄 **Async downloads** — start a download and the UI polls for status automatically
- 🧪 **114 tests** (78 backend + 36 frontend) — TDD throughout
- 🐳 **Docker ready** — single `docker compose up` to run everything

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
│  │ Download  │  File       │  Status    │           │
│  │ Router    │  Router     │  Router    │           │
│  └─────┬─────┴──────┬──────┴──────┬─────┘           │
│        │            │             │                  │
│  ┌─────▼─────┐  ┌───▼───────────▼───┐              │
│  │ Youtube    │  │ FileStorage       │              │
│  │ Service    │  │ Service           │              │
│  │ (yt-dlp)   │  │ (list/play/delete) │             │
│  └───────────┘  └───────────────────┘              │
└─────────────────────────────────────────────────────┘
```

### Project Structure

```
youtube-loader/
├── backend-api/
│   ├── Main.py                    # FastAPI app entrypoint
│   ├── Requirements.txt           # Python dependencies
│   ├── config_settings/
│   │   └── AppConfig.py           # App configuration
│   ├── core_services/
│   │   ├── YoutubeService.py      # yt-dlp wrapper (download + metadata)
│   │   └── FileStorageService.py  # File management (list/delete/move)
│   ├── api_routes/
│   │   ├── DownloadRouter.py      # POST /api/download, GET /api/download/{id}
│   │   ├── FileRouter.py          # GET /api/files, GET/DELETE /api/files/{name}
│   │   └── StatusRouter.py        # GET /api/status
│   └── api_models/
│       └── DownloadRequest.py     # Pydantic request/response schemas
├── frontend-web/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx         # Root layout (Inter font, Thai lang)
│   │   │   └── page.tsx           # Home page (DownloadForm + FileList)
│   │   ├── components/
│   │   │   ├── DownloadForm.tsx   # URL input + format selector
│   │   │   ├── DownloadStatus.tsx # Polling download status display
│   │   │   └── FileList.tsx       # Downloaded files list (play/delete)
│   │   ├── lib/
│   │   │   └── api.ts             # API client functions
│   │   └── test/
│   │       └── setup.ts           # Vitest test setup
│   ├── vitest.config.ts           # Vitest configuration
│   └── package.json
├── tests/                         # Backend tests (pytest)
│   ├── test_api.py
│   ├── test_config.py
│   ├── test_file_router.py
│   ├── test_file_storage.py
│   └── test_youtube_service.py
├── pyproject.toml
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (backend)
- **Node.js 18+** (frontend)
- **FFmpeg** — required by yt-dlp for merging video+audio
  - Windows: `winget install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt install ffmpeg`

### Backend Setup

```bash
cd backend-api

# Create virtual environment
python -m venv venv  # Windows: venv\Scripts\activate
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r Requirements.txt

# Run server
python Main.py
# → API running at http://localhost:8000
# → Swagger docs at http://localhost:8000/docs
```

### Frontend Setup

```bash
cd frontend-web
npm install
npm run dev
# → Frontend running at http://localhost:3000
```

### Run Tests

```bash
# Backend tests
cd backend-api && .venv/bin/python -m pytest tests/ -v

# Frontend tests
cd frontend-web && npm test
```

---

## 📡 API Endpoints

### Download

| Method | Path | Body | Description |
|--------|------|------|-------------|
| `POST` | `/api/download` | `{ url, output_format }` | Start a download (returns `job_id`) |
| `GET`  | `/api/download/{job_id}` | — | Check download status |

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
| `GET` | `/api/downloads` | Legacy file list (from FileStorageService) |

### Example: Start Download

```bash
curl -X POST http://localhost:8000/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID", "output_format": "720p"}'
```

Response:
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending"
}
```

### Example: Check Status

```bash
curl http://localhost:8000/api/download/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

Response (completed):
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "format": "720p",
  "status": "completed",
  "title": "Video Title Here",
  "filepath": "/path/to/video.mp4"
}
```

---

## 📱 How to Use on Mobile

### Option A: Same WiFi Network

1. Find your PC's local IP address:
   - Windows: `ipconfig` → look for "IPv4 Address" (e.g., `192.168.1.100`)
   - macOS/Linux: `ip addr` or `ifconfig`
2. Start the backend: `python backend-api/Main.py`
3. Start the frontend: `cd frontend-web && npm run dev -- -H 0.0.0.0`
4. On your phone, open: `http://192.168.1.100:3000`

### Option B: Cloudflare Tunnel (Public URL — Free)

1. Install cloudflared:
   ```bash
   # macOS
   brew install cloudflared
   # Linux
   curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared && chmod +x cloudflared && sudo mv cloudflared /usr/local/bin/
   # Windows (winget)
   winget install --id Cloudflare.cloudflared
   ```

2. Run tunnel:
   ```bash
   cloudflared tunnel --url http://localhost:3000
   ```

3. You'll get a URL like `https://abc-123.trycloudflare.com` — share this with your mom!

### Option C: Deploy to Cloud (Render/Railway/Fly.io)

See the Docker Compose section below for containerized deployment.

---

## 🐳 Docker Compose

Create `docker-compose.yml` in the project root:

```yaml
version: '3.8'
services:
  backend:
    build: ./backend-api
    ports:
      - "8000:8000"
    volumes:
      - downloads:/app/Downloads
    environment:
      - DOWNLOAD_DIR=/app/Downloads
    restart: unless-stopped

  frontend:
    build: ./frontend-web
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  downloads:
```

```bash
docker compose up -d
```

Downloads are persisted in the `downloads` volume between restarts.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, uvicorn, yt-dlp |
| Frontend | Next.js 15 (App Router), TypeScript, Tailwind CSS |
| Testing | pytest (backend), Vitest + React Testing Library (frontend) |
| Data fetching | SWR (auto-polling for download status + file list) |
| Video/Audio | yt-dlp + FFmpeg |
| Design | Notion-inspired (Inter font, warm whites, Notion Blue accent) |

---

## 🧪 Test Coverage

```
Backend:  78 tests  (config, services, API routes, file management)
Frontend: 36 tests  (API client, components, integration)
Total:    114 tests
```

Every feature was built TDD-style: red → green → refactor. Run the full suite:

```bash
# Backend
cd youtube-loader && python -m pytest tests/ -v

# Frontend
cd frontend-web && npm test
```

---

## 🔧 Customization

### Add Download Formats

Edit `backend-api/core_services/YoutubeService.py` and add a new format to `_get_format_opts()`.

### Change Default Download Directory

Edit `backend-api/config_settings/AppConfig.py`:

```python
download_dir: str = "/path/to/your/folder"
```

### Add CORS Origins for Production

Edit `backend-api/Main.py` to add your production domain:

```python
allow_origins=["http://localhost:3000", "https://your-domain.com"],
```

---

## 📝 Development Workflow

This project follows a strict TDD-first workflow:

1. **Write tests first** — define the expected behavior
2. **Run tests** — they should fail (Red)
3. **Write minimal code** to make tests pass (Green)
4. **Refactor** — clean up without changing behavior
5. **Commit** — small, atomic commits with descriptive messages

Each component, service, and API endpoint has its own test file. The CI should run both test suites.

---

## 📋 Roadmap

- [ ] Persistent job storage (SQLite/Redis instead of in-memory dict)
- [ ] WebSocket real-time download progress
- [ ] Playlist support (download all videos in a playlist)
- [ ] Thumbnail preview before downloading
- [ ] User authentication (protected downloads)
- [ ] Dark mode toggle
- [ ] Subtitle download
- [ ] Browser extension for one-click downloads

---

## 📄 License

MIT

---

*Built with ❤️ for family — simple enough for mom, powerful enough for devs.*
