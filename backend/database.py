import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self, db_path='data/videos.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                size INTEGER NOT NULL,
                duration INTEGER DEFAULT 0,
                thumbnail TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_video(self, title, url, filename, filepath, size, duration=0, thumbnail=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO videos (title, url, filename, filepath, size, duration, thumbnail)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (title, url, filename, filepath, size, duration, thumbnail))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_all_videos(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, url, filename, filepath, size, duration, thumbnail, created_at
            FROM videos ORDER BY created_at DESC
        ''')
        videos = cursor.fetchall()
        conn.close()
        
        return [{
            'id': v[0],
            'title': v[1],
            'url': v[2],
            'filename': v[3],
            'filepath': v[4],
            'size': v[5],
            'duration': v[6],
            'thumbnail': v[7],
            'created_at': v[8]
        } for v in videos]
    
    def delete_video(self, video_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM videos WHERE id = ?', (video_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    def delete_all(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM videos')
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted
    
    def get_total_size(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT SUM(size) FROM videos')
        total = cursor.fetchone()[0] or 0
        conn.close()
        return total
    
    def search_videos(self, query):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, url, filename, filepath, size, duration, thumbnail, created_at
            FROM videos WHERE title LIKE ? ORDER BY created_at DESC
        ''', (f'%{query}%',))
        videos = cursor.fetchall()
        conn.close()
        
        return [{
            'id': v[0],
            'title': v[1],
            'url': v[2],
            'filename': v[3],
            'filepath': v[4],
            'size': v[5],
            'duration': v[6],
            'thumbnail': v[7],
            'created_at': v[8]
        } for v in videos]
