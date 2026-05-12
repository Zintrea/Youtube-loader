# 🚀 คู่มือ Deploy YouTube Loader

---

## ขั้นตอนที่ 1: Deploy Backend (Render.com) — 5 นาที

### 1.1 สร้าง Web Service บน Render

1. เปิดเบราว์เซอร์แล้วเข้า **https://dashboard.render.com**
2. คลิกปุ่ม **"New +"** → เลือก **"Web Service"**
3. เลือก **"Connect a repository"** → เลือก `Zintrea/Youtube-loader`
4. ตั้งค่าดังนี้:

| ช่อง | ค่า |
|------|-----|
| **Name** | `youtube-loader-api` |
| **Root Directory** | `backend-api` |
| **Runtime** | `Python 3` |
| **Region** | เลือกที่ใกล้สุด (Singapore ถ้าเห็น) |
| **Build Command** | `pip install -r Requirements.txt` |
| **Start Command** | `python Main.py` |
| **Instance Type** | `Free` |

### 1.2 ตั้งค่า Environment Variables

ในหน้า Web Service → ไปที่ tab **Environment** → เพิ่มตัวแปร:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.12.0` |
| `DOWNLOAD_DIR` | `/opt/render/project/src/backend-api/Downloads` |
| `CORS_ORIGINS` | (ใส่ URL Frontend ที่ได้จากขั้นตอนที่ 2 ก่อน — ถ้ายังไม่ได้ deploy ให้ใส่ `http://localhost:3000` ไปก่อนแล้วกลับมาแก้ทีหลัง) |

### 1.3 Deploy

1. คลิก **"Create Web Service"**
2. รอ Render build และ deploy (ประมาณ 2-5 นาที)
3. จด URL ที่ได้ เช่น `https://youtube-loader-api-xxxx.onrender.com` ← **เก็บไว้ใช้!**

---

## ขั้นตอนที่ 2: Deploy Frontend (Cloudflare Pages) — 3 นาที

### 2.1 สร้าง Project บน Cloudflare Pages

1. เปิด **https://pages.cloudflare.com** (ต้องล็อกอินก่อน)
2. คลิก **"Create a project"** → **"Connect to Git"**
3. เลือก repo `Zintrea/Youtube-loader`
4. ตั้งค่าดังนี้:

| ช่อง | ค่า |
|------|-----|
| **Project name** | `youtube-loader` (หรือชื่ออื่นที่อยากได้) |
| **Production branch** | `feat/pwa-cloud-deploy` (หรือ `main` หลัง merge แล้ว) |
| **Framework preset** | `Next.js` |
| **Build command** | `cd frontend-web && npm install && npx next build` |
| **Build output directory** | `frontend-web/.next` |
| **Root directory (Advanced)** | `frontend-web` |

### 2.2 ตั้งค่า Environment Variables

ใน Deploy settings → **Environment variables (Production)**:

| Variable name | Value |
|---------------|-------|
| `NEXT_PUBLIC_API_URL` | URL ของ Render ที่ได้จากขั้นตอน 1.3 (เช่น `https://youtube-loader-api-xxxx.onrender.com`) |

### 2.3 Deploy

1. คลิก **"Save and Deploy"**
2. รอ Cloudflare build และ deploy (ประมาณ 1-3 นาที)
3. จด URL ที่ได้ เช่น `https://youtube-loader.pages.dev` ← **เว็บนี้คือเว็บที่แม่/ญาติจะเข้าใช้งาน!**

### 2.4 แก้ CORS Origins บน Render

1. กลับไปที่ Render Dashboard → เปิด Web Service ที่สร้างไว้
2. ไปที่ tab **Environment**
3. แก้ค่า `CORS_ORIGINS` เป็น URL ของ Cloudflare Pages ที่ได้จากขั้นตอน 2.3:
   ```
   https://youtube-loader.pages.dev
   ```
4. คลิก **"Save Changes"** → Deploy อัตโนมัติ

---

## ขั้นตอนที่ 3: ตั้งค่า Custom Domain (ถ้ามี)

### 3.1 บน Cloudflare Pages

1. เข้า **Cloudflare Pages** → เลือก project
2. ไปที่ tab **"Custom domains"**
3. คลิก **"Set up a custom domain"**
4. กรอก domain ที่ต้องการ เช่น `ytloader.zintrea.com`
5. Cloudflare จะบอกให้เพิ่ม DNS record → ทำตามคำแนะนำ

### 3.2 บน Render

1. เข้า **Render Dashboard** → เลือก Web Service
2. ไปที่ tab **"Settings"** → **"Custom domains"**
3. เพิ่ม domain ของคุณ
4. Render จะบอกให้เพิ่ม DNS CNAME record → ทำตามคำแนะนำ

---

## ขั้นตอนที่ 4: ใช้จริง!

### 4.1 สอนแม่/ญาติใช้งาน

1. เปิดเว็บที่ deploy ไว้บนมือถือ
2. (Android) เปิด Chrome → เมนู (⋮) → **"Add to Home screen"**
3. (iOS) เปิด Safari → ปุ่ม Share → **"Add to Home Screen"**
4. ไอคอนจะอยู่บนหน้าจอหลัก เปิดง่ายเหมือนแอพ!

### 4.2 วิธีใช้งาน

1. คัดลอกลิงก์ YouTube จากแอพ YouTube
2. เปิด YouTube Loader → วางลิงก์ → รอสักครู่ระบบจะแสดงรูปคลิป + ชื่อคลิป
3. เลือกรูปแบบ (1080p, 720p, mp3, etc.)
4. กด **"ดาวน์โหลด"** → รอให้เสร็จ
5. กด **"ดาวน์โหลดวิดีโอใหม่"** เพื่อโหลดคลิปถัดไป

---

## 🔄 อัปเดตโค้ด (CI/CD)

เมื่อ push code ขึ้น branch `feat/pwa-cloud-deploy` (หรือ `main` หลัง merge):
- **Render** จะ detect การเปลี่ยนแปลงและ deploy อัตโนมัติ
- **Cloudflare Pages** จะ build และ deploy อัตโนมัติ

---

## 🔍 Troubleshooting

| ปัญหา | วิธีแก้ |
|--------|--------|
| Backend crash on Render | ดู logs ใน Render Dashboard → tab **Logs** |
| CORS Error | ตรวจสอบว่า `CORS_ORIGINS` ตรงกับ URL ของ Cloudflare Pages |
| Video ไม่โหลด | ดูว่า FFmpeg ติดตั้งใน Render แล้ว — ถ้าใช้ rootDir = `backend-api` จะไม่ต้องลง FFmpeg เอง |
| Frontend build fail | ตรวจสอบ `NEXT_PUBLIC_API_URL` ใน environment variables |
| FFmpeg ไม่ทำงาน | ใน Render ต้องเพิ่ม `apt-get install ffmpeg` ใน build script — แก้ build command เป็น: `apt-get update && apt-get install -y ffmpeg && pip install -r Requirements.txt` |

### ⚠️ สำคัญ: FFmpeg บน Render Free Tier

Render Free Tier **ไม่มี FFmpeg ติดตั้งมาให้** และ build command ธรรมดาไม่สามารถ apt-get ได้!

**วิธีแก้:** สร้างไฟล์ `_render-build.sh` ใน `backend-api/`:
```bash
#!/bin/bash
apt-get update
apt-get install -y ffmpeg
pip install -r Requirements.txt
```

แล้วตั้ง Build Command เป็น: `bash _render-build.sh`

แต่ถ้าง่ายกว่านั้น — ให้ **Deploy Backend บน Railway แทน** เพราะ Railway มี FFmpeg ติดตั้งมาให้เลย! หรือใช้ Docker บน Render (แต่ Docker ใช้ได้เฉพาะ paid plan)

---

## 📊 ข้อจำกัด Render Free Tier

| สิ่ง | ค่า |
|------|-----|
| RAM | 512MB — ใช้ได้กับ 720p, mp3, m4a |
| Sleep |หลับถ้าไม่มีคนเข้า 15 นาที (Cold Start ~30-50 วินาที) |
| Bandwidth | 100GB/month |
| Storage | Persistent disk 1GB |

**แนะนำ:** ตั้ง default format เป็น `720p` จะปลอดภัยสุด สำหรับ 1080p อาจ crash ได้จาก RAM น้อย
