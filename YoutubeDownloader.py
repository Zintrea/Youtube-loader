import yt_dlp
import os

def get_download_options(choice):
    """
    ตั้งค่า ydl_opts ตามตัวเลือกที่ผู้ใช้เลือก
    """
    # ตั้งค่าพื้นฐาน: เซฟไฟล์ไว้ในโฟลเดอร์ Downloads
    base_opts = {
        'outtmpl': 'Downloads/%(title)s.%(ext)s',
        'quiet': False,
        'no_warnings': True,
    }
    
    if choice == '1':
        # วิดีโอ 1080p + เสียง (บังคับ Codec H.264 สำหรับมือถือ)
        base_opts['format'] = 'bestvideo[vcodec^=avc1][height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        base_opts['merge_output_format'] = 'mp4'
        
    elif choice == '2':
        # วิดีโอ 720p + เสียง
        base_opts['format'] = 'bestvideo[vcodec^=avc1][height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        base_opts['merge_output_format'] = 'mp4'
        
    elif choice == '3':
        # วิดีโอ 480p + เสียง (ไฟล์เล็ก)
        base_opts['format'] = 'bestvideo[vcodec^=avc1][height<=480][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        base_opts['merge_output_format'] = 'mp4'
        
    elif choice == '4':
        # เฉพาะเสียง (แปลงเป็น MP3)
        base_opts['format'] = 'bestaudio/best'
        base_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192', # คุณภาพเสียง 192kbps
        }]
    else:
        print("ตัวเลือกไม่ถูกต้อง จะใช้ค่าเริ่มต้น (1080p)")
        base_opts['format'] = 'bestvideo[vcodec^=avc1][height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        base_opts['merge_output_format'] = 'mp4'
        
    return base_opts

def download_youtube_video(url, choice):
    # ตรวจสอบและสร้างโฟลเดอร์ Downloads หากยังไม่มี
    if not os.path.exists('Downloads'):
        os.makedirs('Downloads')
        
    ydl_opts = get_download_options(choice)

    try:
        print(f"\n⏳ กำลังเริ่มกระบวนการดาวน์โหลด...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("\n✨ ดาวน์โหลดเสร็จสิ้น! ไฟล์ของคุณอยู่ในโฟลเดอร์ 'Downloads'")
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    print("=== YoutubeDownloader v2 ===")
    video_url = input("ใส่ URL ของวิดีโอ: ").strip()
    
    if video_url:
        print("\nเลือกรูปแบบที่ต้องการดาวน์โหลด:")
        print("1. วิดีโอ 1080p (MP4 - ภาพชัดสุด เปิดในมือถือได้)")
        print("2. วิดีโอ 720p  (MP4 - ประหยัดพื้นที่ลงมา)")
        print("3. วิดีโอ 480p  (MP4 - ไฟล์เล็กมาก โหลดไว)")
        print("4. เฉพาะเสียง   (MP3 - สำหรับฟังเพลงหรือแกะคอร์ด)")
        
        choice = input("\nพิมพ์หมายเลข (1-4): ").strip()
        download_youtube_video(video_url, choice)
    else:
        print("คุณไม่ได้ใส่ URL โปรแกรมจบการทำงาน")