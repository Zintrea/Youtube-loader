# YoutubeDownloader

This YouTube video and audio downloader is developed using Python and `yt-dlp`. It supports downloads up to 1080p resolution and automatically merges video and audio files. The program is configured to enforce codecs (H.264/AAC) to ensure that the downloaded files can be played immediately on smartphones, tablets, and other devices without compatibility issues.

## 🌟 Features
- **Video Download:** Choose your desired video resolution (1080p, 720p, 480p).
- **Audio Only:** Supports downloading only audio for further use.
- **MP3 (320kbps):** Highest quality MP3, ensuring 100% compatibility with all devices.
- **M4A (AAC):** Extracts the original audio from YouTube without further compression, providing maximum clarity.
- **Auto-Folder:** Automatically organizes downloaded files into the `Downloads` folder.

## 🛠️ Prerequisites (Requirements)
This program requires **FFmpeg** to combine video and audio files. Please install before use.
- **Windows:** Open Terminal and type `winget install ffmpeg`
- **Mac:** Open Terminal and type `brew install ffmpeg`
- **Linux:** Open Terminal and type `sudo apt install ffmpeg`

## 🚀 Installation

It is recommended to always use Git to clone the project and create a Virtual Environment to prevent libraries from interfering with the operation of other projects on the machine.

```bash
# 1. Clone the project repository
git clone <insert your repository URL here>
cd <project folder name>

# 2. Create a Virtual Environment
python -m venv Venv

# 3. Activate the Virtual Environment
# For Windows:
Venv\Scripts\activate
# For Mac / Linux:
source Venv/bin/activate

# 4. Install necessary libraries
pip install yt-dlp

# YoutubeDownloader

โปรแกรมดาวน์โหลดวิดีโอและเสียงจาก YouTube พัฒนาด้วย Python และ `yt-dlp` รองรับการดาวน์โหลดความละเอียดสูงสุด 1080p พร้อมรวมไฟล์ภาพและเสียงเข้าด้วยกันโดยอัตโนมัติ โปรแกรมนี้ถูกตั้งค่าให้บังคับใช้ Codec (H.264/AAC) เพื่อให้มั่นใจว่าไฟล์ที่ได้สามารถนำไปเปิดเล่นบนสมาร์ทโฟน แท็บเล็ต หรืออุปกรณ์อื่น ๆ ได้ทันทีโดยไม่เจอปัญหาไฟล์ไม่รองรับ

## 🌟 Features (คุณสมบัติ)
- **Video Download:** เลือกความละเอียดของวิดีโอได้ตามต้องการ (1080p, 720p, 480p)
- **Audio Only:** รองรับการดาวน์โหลดเฉพาะเสียงเพื่อนำไปใช้งานต่อ
  - **MP3 (320kbps):** คุณภาพสูงสุดของ MP3 มั่นใจได้ว่าเปิดได้กับทุกอุปกรณ์ 100%
  - **M4A (AAC):** ดึงเสียงต้นฉบับจาก YouTube โดยไม่ผ่านการบีบอัดซ้ำ ให้ความคมชัดสูงสุด
- **Auto-Folder:** จัดเก็บไฟล์ที่ดาวน์โหลดเสร็จแล้วลงในโฟลเดอร์ `Downloads` อย่างเป็นระเบียบโดยอัตโนมัติ

## 🛠️ Prerequisites (สิ่งที่ต้องมี)
โปรแกรมนี้จำเป็นต้องใช้ **FFmpeg** ในการประกอบไฟล์วิดีโอและไฟล์เสียงเข้าด้วยกัน กรุณาติดตั้งก่อนเริ่มใช้งาน
- **Windows:** เปิด Terminal แล้วพิมพ์ `winget install ffmpeg`
- **Mac:** เปิด Terminal แล้วพิมพ์ `brew install ffmpeg`
- **Linux:** เปิด Terminal แล้วพิมพ์ `sudo apt install ffmpeg`

## 🚀 Installation (การติดตั้ง)

แนะนำให้ใช้ Git ในการโคลนโปรเจคต์ และสร้าง Virtual Environment เสมอ เพื่อป้องกันไม่ให้ไลบรารีไปรบกวนการทำงานของโปรเจคต์อื่นในเครื่อง

```bash
# 1. Clone repository ของโปรเจคต์นี้
git clone <ใส่-URL-ของ-Repository-คุณตรงนี้>
cd <ชื่อโฟลเดอร์โปรเจคต์>

# 2. สร้าง Virtual Environment 
python -m venv Venv

# 3. เปิดใช้งาน Virtual Environment
# สำหรับ Windows:
Venv\Scripts\activate
# สำหรับ Mac / Linux:
source Venv/bin/activate

# 4. ติดตั้งไลบรารีที่จำเป็น
pip install yt-dlp
