```markdown
# 📥 Youtube-loader (Web Application Edition 2026)

โปรแกรมดาวน์โหลดวิดีโอและแยกไฟล์เสียงจาก YouTube ที่ถูกยกระดับสถาปัตยกรรมเป็น Web Application อย่างเต็มรูปแบบ โดยแบ่งแยกการทำงานระหว่าง **Frontend (Next.js/React)** สำหรับส่วนแสดงผล และ **Backend (FastAPI/Python)** สำหรับประมวลผลการดาวน์โหลดผ่าน `yt-dlp` และ `FFmpeg`

โปรเจคต์นี้ถูกออกแบบโครงสร้างให้รองรับการขยายสเกลในอนาคต (Scalable Architecture) ทำให้ง่ายต่อการเพิ่มฟีเจอร์ใหม่ ๆ เข้าไป

---

## 🏗️ Project Architecture & Folder Structure

เพื่อความเป็นระเบียบและป้องกันโค้ดตีกัน โปรเจคต์นี้ใช้มาตรฐานการตั้งชื่อดังนี้:
- **โฟลเดอร์ (Directories):** ใช้รูปแบบ `kebab-case` (เช่น `backend-api`, `core-services`)
- **ไฟล์ (Files):** ใช้รูปแบบ `PascalCase` (เช่น `Main.py`, `YoutubeService.py`, `Page.tsx`)

```text
youtube-loader/
│
├── backend-api/                    <-- ส่วนจัดการระบบหลังบ้าน (FastAPI)
│   ├── venv/                       (⚠️ ห้ามนำขึ้น Git - ใช้สำหรับเก็บไลบรารี)
│   ├── Main.py                     (จุดเริ่มต้นของเซิร์ฟเวอร์ API)
│   ├── Requirements.txt            (รายการไลบรารีที่ต้องใช้)
│   ├── api-routes/                 <-- จัดการ URL Endpoints
│   │   ├── DownloadRouter.py       
│   │   └── StatusRouter.py         
│   ├── core-services/              <-- โลจิกการทำงานหลัก (ดาวน์โหลด/จัดการไฟล์)
│   │   ├── YoutubeService.py       
│   │   └── FileStorageService.py   
│   └── config-settings/            <-- การตั้งค่าระบบ
│       └── AppConfig.py            
│
└── frontend-web/                   <-- ส่วนหน้าบ้าน (Next.js/React)
    ├── Package.json                (รายการไลบรารีฝั่งหน้าเว็บ)
    ├── src-app/                    <-- โค้ดหลักของหน้าเว็บ
    │   ├── Page.tsx                
    │   └── Layout.tsx              
    ├── components-ui/              <-- ชิ้นส่วน UI ที่นำไปใช้ซ้ำได้
    │   ├── DownloadForm.tsx        
    │   └── ProgressBar.tsx         
    └── services-api/               <-- ตัวกลางสำหรับคุยกับหลังบ้าน
        └── ApiClient.ts            

```

---

## 🛠️ Prerequisites (สิ่งที่ต้องติดตั้งก่อนเริ่มงาน)

ก่อนจะทำการรันโปรเจคต์นี้ เครื่องคอมพิวเตอร์ของคุณต้องมีโปรแกรมพื้นฐานดังต่อไปนี้:

1. **Python 3.10+** สำหรับรัน Backend
2. **Node.js (v18 ขึ้นไป)** สำหรับรัน Frontend
3. **Git** สำหรับจัดการเวอร์ชันโค้ด
4. **FFmpeg** (สำคัญมาก! สำหรับรวมภาพและเสียงเข้าด้วยกัน)
* **Windows:** เปิด Terminal พิมพ์ `winget install ffmpeg`
* **Mac:** เปิด Terminal พิมพ์ `brew install ffmpeg`



---

## 🚀 Installation & Setup Guide (วิธีติดตั้งแบบจับมือทำ)

กรุณาทำตามขั้นตอนด้านล่างนี้อย่างละเอียด เพื่อรันโปรเจคต์ในโหมด Development

### ขั้นตอนที่ 1: เตรียมพื้นที่และ Git

เปิด Terminal แล้วรันคำสั่งต่อไปนี้เพื่อโคลนโปรเจคต์ลงเครื่อง:

```bash
git clone [https://github.com/Zintrea/Youtube-loader.git](https://github.com/Zintrea/Youtube-loader.git)
cd Youtube-loader

```

### ขั้นตอนที่ 2: ตั้งค่า Backend (Python / FastAPI)

> ⚠️ **คำเตือนที่สำคัญมาก:** คุณต้องสร้าง Virtual Environment (`venv`) ทุกครั้งก่อนติดตั้งไลบรารี เพื่อไม่ให้แพ็กเกจไปกวนโปรเจคต์อื่นในเครื่อง!

1. เข้าไปที่โฟลเดอร์หลังบ้าน:
```bash
cd backend-api


```



```
2. สร้างและเปิดใช้งาน Virtual Environment:
   ```bash
   # สร้าง venv
   python -m venv venv
   
   # เปิดใช้งาน (สำหรับ Windows)
   venv\Scripts\activate
   
   # เปิดใช้งาน (สำหรับ Mac/Linux)
   source venv/bin/activate
   

```

*(เมื่อเปิดสำเร็จ จะมีคำว่า `(venv)` ขึ้นหน้าบรรทัดคำสั่งใน Terminal)*

3. สร้างไฟล์ `Requirements.txt` (หากยังไม่มี) และใส่ข้อมูลนี้ลงไป:
```text
fastapi
uvicorn
yt-dlp
websockets

```


4. ติดตั้งไลบรารีทั้งหมด:
```bash
pip install -r Requirements.txt


```



```
5. รันเซิร์ฟเวอร์ Backend:
   ```bash
   uvicorn Main:app --reload
   

```

*(เซิร์ฟเวอร์หลังบ้านจะรันอยู่ที่ `http://localhost:8000`)*

### ขั้นตอนที่ 3: ตั้งค่า Frontend (Next.js / Node.js)

ให้เปิด Terminal หน้าต่างใหม่ (แยกจากหน้าต่างที่รัน Backend ไว้)

1. กลับไปที่โฟลเดอร์หลักและเข้าไปที่ส่วนหน้าบ้าน:
```bash
# เริ่มจากโฟลเดอร์หลัก youtube-loader
cd frontend-web


```



```
2. สร้างโปรเจคต์ Next.js เบื้องต้น (หากเป็นการเริ่มโปรเจคต์ครั้งแรก):
   ```bash
   # ใช้คำสั่งนี้ถ้าเพิ่งเริ่มสร้างโครงสร้าง
   npx create-next-app@latest .
   

```

3. ติดตั้งไลบรารีที่จำเป็น (ถ้ามี `Package.json` อยู่แล้ว):
```bash
npm install

```


4. รันเซิร์ฟเวอร์ Frontend:
```bash
npm run dev


```



```
   *(หน้าเว็บของคุณจะแสดงผลที่ `http://localhost:3000`)*

---

## 💻 How to Develop & Contribute (คู่มือการพัฒนาต่อ)

เมื่อคุณต้องการเขียนโค้ดเพิ่ม หรือแก้ไขบั๊ก ให้ยึดหลักการทำงานตามโครงสร้างนี้:

### 1. ถ้าต้องการเพิ่มฟีเจอร์ดาวน์โหลดเว็บอื่น (เช่น TikTok, Facebook)
- **ไม่ต้องยุ่งกับไฟล์เดิม:** ให้ไปสร้างไฟล์ใหม่ที่ `backend-api/core-services/TiktokService.py`
- แล้วไปเพิ่มเส้นทาง URL ใหม่ที่ `backend-api/api-routes/`
- วิธีนี้จะทำให้โค้ดไม่พัง และแยกการทำงานกันอย่างชัดเจน

### 2. การจัดการไฟล์ที่ดาวน์โหลดเสร็จแล้ว
- โลจิกทั้งหมดเกี่ยวกับการเซฟไฟล์ ย้ายไฟล์ หรือลบไฟล์ขยะ จะถูกเขียนไว้ในโฟลเดอร์ `backend-api/core-services/FileStorageService.py` เท่านั้น เพื่อให้ง่ายต่อการดูแล

### 3. การแสดงผล UI ฝั่งหน้าเว็บ
- หากแถบดาวน์โหลดบั๊ก หรือหน้าตาปุ่มไม่สวย ให้เข้าไปแก้ที่ `frontend-web/components-ui/` 
- หลีกเลี่ยงการเขียนสไตล์หรือลอจิกทุกอย่างรวมไว้ในหน้าเดียว (`Page.tsx`) ให้แยกเป็น Component เสมอ

## 📝 Git Workflow (ข้อแนะนำในการเซฟงาน)
เนื่องจากเราแยกส่วนหน้าบ้านและหลังบ้านออกจากกัน เวลาเซฟงาน (Commit) ควรแยกกันอย่างชัดเจน:
```bash
# ตรวจสอบสถานะก่อนเสมอ
git status

# ถ้าทำฝั่งหลังบ้านเสร็จ
git add backend-api/
git commit -m "อัปเดตระบบดาวน์โหลดใน YoutubeService.py"

# ถ้าทำฝั่งหน้าบ้านเสร็จ
git add frontend-web/
git commit -m "ปรับปรุงหน้าตา ProgressBar.tsx"

git push origin main

```

```


```