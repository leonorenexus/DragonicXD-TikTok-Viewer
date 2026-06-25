import os
import shutil
import json
from datetime import datetime

class StorageManager:
    def __init__(self, storage_path='data/videos'):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    def save_video(self, source_file, filename):
        """Simpan video ke storage private"""
        try:
            dest_path = os.path.join(self.storage_path, filename)
            
            # Cek apakah file sudah ada
            if os.path.exists(dest_path):
                # Tambahkan timestamp biar unik
                name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{name}_{timestamp}{ext}"
                dest_path = os.path.join(self.storage_path, filename)
            
            # Copy file ke storage
            shutil.copy2(source_file, dest_path)
            
            # Hapus file temporary
            if source_file != dest_path and os.path.exists(source_file):
                os.remove(source_file)
            
            return {
                'success': True,
                'filename': os.path.basename(dest_path),
                'filepath': dest_path,
                'size': os.path.getsize(dest_path)
            }
        except Exception as e:
            return {'error': f'Gagal simpan video: {str(e)}'}
    
    def delete_video(self, filename):
        """Hapus video dari storage"""
        try:
            filepath = os.path.join(self.storage_path, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return {'success': True, 'message': 'Video berhasil dihapus'}
            return {'error': 'File tidak ditemukan'}
        except Exception as e:
            return {'error': f'Gagal hapus video: {str(e)}'}
    
    def delete_all_videos(self):
        """Hapus semua video di storage"""
        try:
            files = os.listdir(self.storage_path)
            deleted_count = 0
            for f in files:
                filepath = os.path.join(self.storage_path, f)
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    deleted_count += 1
            return {
                'success': True,
                'message': f'{deleted_count} video berhasil dihapus',
                'count': deleted_count
            }
        except Exception as e:
            return {'error': f'Gagal hapus semua: {str(e)}'}
    
    def get_video_list(self):
        """Dapatkan daftar semua video di storage"""
        try:
            files = []
            for f in os.listdir(self.storage_path):
                filepath = os.path.join(self.storage_path, f)
                if os.path.isfile(filepath) and f.endswith(('.mp4', '.webm', '.mkv')):
                    files.append({
                        'filename': f,
                        'filepath': filepath,
                        'size': os.path.getsize(filepath),
                        'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                    })
            return files
        except Exception as e:
            return {'error': f'Gagal baca daftar video: {str(e)}'}
    
    def get_storage_info(self):
        """Dapatkan info storage"""
        try:
            total_size = 0
            total_files = 0
            
            for f in os.listdir(self.storage_path):
                filepath = os.path.join(self.storage_path, f)
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)
                    total_files += 1
            
            # Format ukuran
            if total_size < 1024:
                size_str = f'{total_size} B'
            elif total_size < 1024**2:
                size_str = f'{total_size/1024:.1f} KB'
            elif total_size < 1024**3:
                size_str = f'{total_size/(1024**2):.1f} MB'
            else:
                size_str = f'{total_size/(1024**3):.1f} GB'
            
            return {
                'success': True,
                'total_size': total_size,
                'formatted': size_str,
                'total_files': total_files,
                'path': self.storage_path
            }
        except Exception as e:
            return {'error': f'Gagal dapat info storage: {str(e)}'}
    
    def clear_storage(self):
        """Bersihkan semua file di storage (termasuk subfolder)"""
        try:
            for f in os.listdir(self.storage_path):
                filepath = os.path.join(self.storage_path, f)
                if os.path.isfile(filepath):
                    os.remove(filepath)
                elif os.path.isdir(filepath):
                    shutil.rmtree(filepath)
            return {'success': True, 'message': 'Storage berhasil dibersihkan'}
        except Exception as e:
            return {'error': f'Gagal bersihkan storage: {str(e)}'}
    
    def check_disk_space(self):
        """Cek sisa ruang disk"""
        try:
            stat = shutil.disk_usage(self.storage_path)
            free_space = stat.free
            
            if free_space < 1024**3:  # Kurang dari 1 GB
                warning = '⚠️ Peringatan: Ruang penyimpanan hampir habis!'
            else:
                warning = '✅ Ruang penyimpanan cukup'
            
            return {
                'success': True,
                'free_space': free_space,
                'formatted': self._format_size(free_space),
                'warning': warning
            }
        except Exception as e:
            return {'error': f'Gagal cek disk: {str(e)}'}
    
    def _format_size(self, size):
        """Format ukuran file"""
        if size < 1024:
            return f'{size} B'
        elif size < 1024**2:
            return f'{size/1024:.1f} KB'
        elif size < 1024**3:
            return f'{size/(1024**2):.1f} MB'
        else:
            return f'{size/(1024**3):.1f} GB'
