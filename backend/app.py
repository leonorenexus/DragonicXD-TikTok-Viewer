from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from database import Database
from downloader import TikTokDownloader
import os
import json
import shutil

app = Flask(__name__)
CORS(app)

# Inisialisasi
db = Database()
downloader = TikTokDownloader()

# ============= API DOWNLOAD =============
@app.route('/api/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL tidak boleh kosong'}), 400
    
    # Cek duplicate di database
    existing = db.get_all_videos()
    for v in existing:
        if v['url'] == url:
            return jsonify({
                'success': False,
                'message': 'Video sudah pernah di-download!',
                'video': v
            }), 409
    
    result = downloader.download_video(url)
    
    if 'error' in result:
        return jsonify({'error': result['error']}), 400
    
    # Simpan ke database
    video_id = db.add_video(
        title=result['title'],
        url=result['url'],
        filename=result['filename'],
        filepath=result['filepath'],
        size=result['size'],
        duration=result['duration'],
        thumbnail=result['thumbnail']
    )
    
    if video_id:
        result['id'] = video_id
        return jsonify({
            'success': True,
            'message': 'Video berhasil di-download!',
            'video': result
        })
    else:
        return jsonify({'error': 'Gagal menyimpan ke database'}), 500

# ============= API FEED =============
@app.route('/api/feed', methods=['GET'])
def get_feed():
    videos = db.get_all_videos()
    return jsonify({
        'success': True,
        'videos': videos,
        'total': len(videos)
    })

# ============= API VIDEO STREAM =============
@app.route('/api/video/<int:video_id>', methods=['GET'])
def stream_video(video_id):
    videos = db.get_all_videos()
    video = next((v for v in videos if v['id'] == video_id), None)
    
    if not video:
        return jsonify({'error': 'Video tidak ditemukan'}), 404
    
    filepath = video['filepath']
    if not os.path.exists(filepath):
        return jsonify({'error': 'File video tidak ada'}), 404
    
    return send_file(filepath, mimetype='video/mp4')

# ============= API DELETE =============
@app.route('/api/video/<int:video_id>', methods=['DELETE'])
def delete_video(video_id):
    # Ambil data video
    videos = db.get_all_videos()
    video = next((v for v in videos if v['id'] == video_id), None)
    
    if not video:
        return jsonify({'error': 'Video tidak ditemukan'}), 404
    
    # Hapus file
    try:
        if os.path.exists(video['filepath']):
            os.remove(video['filepath'])
    except:
        pass
    
    # Hapus dari database
    deleted = db.delete_video(video_id)
    
    if deleted:
        return jsonify({
            'success': True,
            'message': 'Video berhasil dihapus!'
        })
    else:
        return jsonify({'error': 'Gagal menghapus video'}), 500

# ============= API DELETE ALL =============
@app.route('/api/videos', methods=['DELETE'])
def delete_all_videos():
    videos = db.get_all_videos()
    
    # Hapus semua file
    for v in videos:
        try:
            if os.path.exists(v['filepath']):
                os.remove(v['filepath'])
        except:
            pass
    
    # Hapus dari database
    deleted = db.delete_all()
    
    return jsonify({
        'success': True,
        'message': f'{deleted} video berhasil dihapus!'
    })

# ============= API STORAGE INFO =============
@app.route('/api/storage', methods=['GET'])
def get_storage_info():
    total_size = db.get_total_size()
    
    # Format ukuran
    if total_size < 1024:
        size_str = f'{total_size} B'
    elif total_size < 1024**2:
        size_str = f'{total_size/1024:.1f} KB'
    elif total_size < 1024**3:
        size_str = f'{total_size/(1024**2):.1f} MB'
    else:
        size_str = f'{total_size/(1024**3):.1f} GB'
    
    return jsonify({
        'success': True,
        'total_size': total_size,
        'formatted': size_str,
        'video_count': len(db.get_all_videos())
    })

# ============= API SEARCH =============
@app.route('/api/search', methods=['GET'])
def search_videos():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Query kosong'}), 400
    
    videos = db.search_videos(query)
    return jsonify({
        'success': True,
        'videos': videos,
        'total': len(videos)
    })

# ============= RUN SERVER =============
if __name__ == '__main__':
    print('''
    🐉 DRAGONICXD OFFLINE TIKTOK VIEWER
    =================================
    Server running on: http://localhost:5000
    API Endpoints:
    - POST /api/download  : Download video
    - GET  /api/feed      : Get all videos
    - GET  /api/video/<id>: Stream video
    - DELETE /api/video/<id>: Delete video
    - DELETE /api/videos  : Delete all videos
    - GET  /api/storage   : Storage info
    - GET  /api/search?q= : Search videos
    ''')
    app.run(host='0.0.0.0', port=5000, debug=False)
