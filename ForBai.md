# YouTube-loader — สรุปโปรเจคต์สำหรับใบ

---

## ภาพรวมโปรเจคต์

YouTube-loader เป็น Backend API ที่เขียนด้วย **FastAPI (Python)** ใช้สำหรับดาวน์โหลดวิดีโอและแยกไฟล์เสียงจาก YouTube ผ่านไลบรารี `yt-dlp` โครงสร้างถูกออกแบบเป็นแบบ Layered Architecture แยกส่วนการทำงานอย่างชัดเจน รองรับการใช้งานแบบ Async (BackgroundTasks)

---

## สถาปัตยกรรม (Architecture)

มี 4 Layer หลัก:

| Layer | โฟลเดอร์ | หน้าที่ |
|---|---|---|
| **Routes** | `backend-api/api_routes/` | จัดการ URL Endpoints, รับ/ส่ง Response |
| **Models** | `backend-api/api_models/` | Pydantic schemas สำหรับ validate request/response |
| **Services** | `backend-api/core_services/` | โลจิกการทำงานหลัก (ดาวน์โหลด, จัดการไฟล์) |
| **Config** | `backend-api/config_settings/` | การตั้งค่าแอป (download_dir, port, host) |

---

## ไฟล์ทั้งหมดในโปรเจคต์

### 🔧 Backend Core
- **`backend-api/Main.py`** — จุดเริ่มต้นของ FastAPI app, รันเซิร์ฟเวอร์
- **`backend-api/config_settings/AppConfig.py`** — dataclass เก็บ config: `download_dir`, `server_host`, `server_port`, `allowed_extensions`
- **`backend-api/core_services/YoutubeService.py`** — คลาส Singleton ห่อ yt-dlp ไว้ มี 2 method:
  - `get_video_info(url)` — ดึง metadata (title, duration, thumbnail, formats) โดยไม่ดาวน์โหลด
  - `download_video(url, output_format, output_dir)` — ดาวน์โหลดวิดีโอ เสียง ตามฟอร์แมต
- **`backend-api/core_services/FileStorageService.py`** — จัดการไฟล์ที่ดาวน์โหลดไว้: `save_file()`, `list_files()`, `delete_file()`

### 📡 API Routes
- **`backend-api/api_routes/DownloadRouter.py`** — Endpoint เกี่ยวกับการดาวน์โหลด:
  - `POST /api/download` — เริ่มดาวน์โหลด (รับ JSON body)
  - `GET /api/download/{job_id}` — เช็คสถานะดาวน์โหลด
  - `GET /api/downloads` — รายการไฟล์ที่ดาวน์โหลดไว้แล้ว
- **`backend-api/api_routes/StatusRouter.py`** — Endpoint เช็คสถานะระบบ:
  - `GET /api/status` — คืน `{"status": "ok", "version": "0.1.0"}`

### 🔐 Pydantic Models (Validate Request/Response)
- **`backend-api/api_models/__init__.py`**
- **`backend-api/api_models/DownloadRequest.py`** — มี 5 models:
  - `DownloadRequest` — validate `url` (ต้องมี youtube.com หรือ youtu.be), `output_format` (ต้องเป็นหนึ่งใน 1080p/720p/480p/mp3/m4a), `custom_filename` (Optional)
  - `DownloadResponse` — `job_id`, `status`
  - `StatusResponse` — `url`, `status`, `format`, `filepath`, `title`, `error` (Optional)
  - `VideoInfoResponse` — `title`, `duration`, `thumbnail`, `formats`, `error` (Optional)
  - `ErrorResponse` — `detail`, `code` (Optional)

### 🧪 Tests (72 tests — 100% ผ่าน)
- **`tests/conftest.py`** — ตั้งค่า sys.path ให้ import backend-api ได้, มี fixtures
- **`tests/test_config.py`** — 9 tests: ทดสอบ AppConfig defaults, custom values, instance independence
- **`tests/test_file_storage.py`** — 14 tests: สร้าง/ลบ/ลิสต์ไฟล์, edge cases
- **`tests/test_youtube_service.py`** — 23 tests: Singleton pattern, format options, video info, download (mock yt-dlp)
- **`tests/test_api.py`** — 26 tests: Integration tests ด้วย `TestClient` ครอบคลุมทุก endpoint, validation errors, full download flow

### 📄 Project Files
- **`pyproject.toml`** — ตั้งค่า dependencies, pytest config, ruff config
- **`BACKEND-api/Requirements.txt`** — fastapi, uvicorn, yt-dlp, websockets, pytest, httpx, pytest-asyncio
- **`README.md`** — คู่มือติดตั้งและใช้งาน
- **`YoutubeDownloader.py`** — CLI script เดิม (legacy v2)

---

## API Endpoints — รายละเอียดการใช้งาน

### 1. `GET /api/status`
เช็คสถานะเซิร์ฟเวอร์

**Response:**
```json
{"status": "ok", "version": "0.1.0"}
```

### 2. `POST /api/download`
เริ่มดาวน์โหลดวิดีโอ/เสียง

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "output_format": "720p",
  "custom_filename": "my_video.mp4"  // Optional
}
```

**output_format ที่รองรับ:**
- `1080p` — วิดีโอคุณภาพสูงสุด H.264 MP4
- `720p` — วิดีโอ HD MP4 (ค่าเริ่มต้น)
- `480p` — วิดีโอขนาดเล็กลง
- `mp3` — เสียง MP3 320kbps
- `m4a` — เสียงต้นฉบับ M4A/AAC

**Response:**
```json
{"job_id": "uuid-here", "status": "pending"}
```

**Validation Error (422):**
- URL ไม่มี youtube.com หรือ youtu.be → reject
- output_format ไม่อยู่ในรายการ → reject
- url ว่างเปล่า → reject

### 3. `GET /api/download/{job_id}`
เช็คสถานะดาวน์โหลด

**Response (กำลังดาวน์โหลด):**
```json
{"id": "...", "url": "...", "format": "720p", "status": "downloading"}
```

**Response (เสร็จแล้ว):**
```json
{"id": "...", "url": "...", "format": "720p", "status": "completed", "filepath": "/path/to/file.mp4", "title": "Video Title"}
```

**Response (ล้มเหลว):**
```json
{"id": "...", "url": "...", "format": "720p", "status": "failed", "error": "error message"}
```

**404:** ถ้า job_id ไม่มีในระบบ

### 4. `GET /api/downloads`
รายการไฟล์ทั้งหมดที่ดาวน์โหลดไว้

**Response:**
```json
{"files": ["video1.mp4", "song.mp3", "video2.mp4"]}
```

---

## โฟลว์การทำงาน (How it works)

1. **ผู้ใช้ส่ง POST /api/download** พร้อม URL และ format ที่ต้องการใน JSON body
2. **Pydantic Validate** — `DownloadRequest` ตรวจสอบว่า URL เป็น YouTube URL จริง, format ถูกต้อง
3. **สร้าง Job ID** — สร้าง UUID เก็บสถานะเป็น "pending" ใน memory dict
4. **BackgroundTasks** — FastAPI ส่งงานดาวน์โหลดให้ทำงานใน background ไม่ block response
5. **YoutubeService.download_video()** — เรียก yt-dlp เพื่อดาวน์โหลด
6. **อัปเดตสถานะ** — เมื่อเสร็จ/ล้มเหลว อัปเดต job ใน dict ให้ client เช็คได้
7. **ผู้ใช้เช็คสถานะ** — GET /api/download/{job_id} เพื่อดูผล

---

## สิ่งที่ Iris ทำตอนใบไปนอน

| สิ่งที่ทำ | ก่อนหน้า | หลังทำ |
|---|---|---|
| แก้ StatusRouter.py docstring | syntax error → ใช้ไม่ได้เลย | ✅ ทำงานได้ |
| แก้ test_file_storage.py | 2 tests (1 ผิด) → 14 tests | ✅ ผ่านทั้งหมด |
| แก้ test_youtube_service.py | 2 tests (ผิด) → 23 tests | ✅ ผ่านทั้งหมด |
| เพิ่ม test_config.py | 2 tests → 9 tests | ✅ ผ่านทั้งหมด |
| เพิ่ม test_api.py | ไม่มี → 26 tests | ✅ ผ่านทั้งหมด |
| สร้าง Pydantic Models | ไม่มี → 5 models | ✅ Request validation ครบ |
| อัปเดต DownloadRouter | query params → JSON body | ✅ RESTful pattern |
| สร้าง pyproject.toml | ไม่มี → มีแล้ว | ✅ Standard Python project |

**ผลลัพธ์รวม:** 3/6 tests (50%) → **72/72 tests (100%)** ✅

---

## สิ่งที่ควรทำต่อ (ถ้าใบอยากขยายโปรเจค)

1. **Persistent Job Storage** — ตอนนี้เก็บ jobs ใน memory dict (dict) ถ้า restart server jobs จะหาย ใช้ SQLite หรือ Redis แทนได้
2. **YouTube URL Extractor** — รองรับ TikTok, Facebook, Twitter, Instagram เพิ่มใน core_services
3. **Frontend (Next.js/React)** — README บอกว่ามีแผนจะทำ frontend แต่โฟลเดอร์ frontend-web ยังไม่มี สร้างหน้าเว็บให้ผู้ใช้ paste URL เลือก format แล้วกดดาวน์โหลด
4. **WebSocket Progress** — แจ้งความคืบหน้าดาวน์โหลดแบบ real-time ลง frontend
5. **File Streaming/Download** — ให้ผู้ใช้ดาวน์โหลดไฟล์ที่ดาวน์โหลดไว้ผ่าน GET /api/download/{job_id}/stream
6. **Rate Limiting** — จำกัดจำนวนดาวน์โหลดต่อ IP
7. **Docker** — สร้าง Dockerfile + docker-compose รันทั้ง backend + frontend

---

*สรุปนี้เขียนโดย Iris สำหรับใบ — อ่านจบเข้าใจทั้งหมดแน่นอนค่ะ*
