import yt_dlp
import os
import re
from urllib.parse import urlparse

class TikTokDownloader:
    def __init__(self, storage_path='data/videos'):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    def validate_url(self, url):
        """Validasi URL TikTok"""
        patterns = [
            r'https?://(www\.)?tiktok\.com/@[\w.-]+/video/\d+',
            r'https?://(www\.)?tiktok\.com/t/[\w-]+',
            r'https?://(www\.)?vt\.tiktok\.com/[\w-]+'
        ]
        return any(re.match(p, url) for p in patterns)
    
    def download_video(self, url):
        """Download video TikTok"""
        if not self.validate_url(url):
            return {'error': 'URL TikTok tidak valid!'}
        
        # Cek duplicate
        # (Simplifikasi - di real implementation pake database)
        
        ydl_opts = {
            'outtmpl': os.path.join(self.storage_path, '%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'format': 'best[height<=720]',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                # Hapus karakter aneh dari judul
                title = re.sub(r'[^\w\s-]', '', info.get('title', 'No Title'))
                
                return {
                    'success': True,
                    'title': title[:100],
                    'filename': os.path.basename(filename),
                    'filepath': filename,
                    'size': os.path.getsize(filename),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'url': url
                }
        except Exception as e:
            return {'error': f'Download gagal: {str(e)}'}
