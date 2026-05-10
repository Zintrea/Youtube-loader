import yt_dlp

def download_youtube_video(url):
    """
    ดาวน์โหลดวิดีโอ YouTube ที่ความละเอียดสูงสุดไม่เกิน 1080p พร้อมเสียง
    """
    ydl_opts = {
        # เลือกวิดีโอที่ความละเอียด <= 1080p (mp4) + เสียงที่ดีที่สุด (m4a) 
        # หากไม่มี ให้เลือกรูปแบบที่ดีที่สุดที่มีอยู่
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        
        # ตั้งชื่อไฟล์ขาออกเป็น "ชื่อวิดีโอ.นามสกุลไฟล์"
        'outtmpl': '%(title)s.%(ext)s',
        
        # บังคับให้ไฟล์ที่รวมเสร็จแล้วเป็นนามสกุล mp4
        'merge_output_format': 'mp4',
        
        # แสดงผลลัพธ์ใน Console
        'quiet': False,
        'no_warnings': True
    }

    try:
        print(f"กำลังดาวน์โหลดข้อมูลจาก: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("\n✨ ดาวน์โหลดเสร็จสิ้น!")
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    print("=== โปรแกรมดาวน์โหลด YouTube 1080p ===")
    video_url = input("ใส่ URL ของวิดีโอ: ").strip()
    
    if video_url:
        download_youtube_video(video_url)
    else:
        print("คุณไม่ได้ใส่ URL โปรแกรมจบการทำงาน")