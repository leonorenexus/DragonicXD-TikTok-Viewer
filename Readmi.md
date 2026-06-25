# 🐉 DragonicXD Offline TikTok Viewer

Aplikasi web modern untuk download & tonton video TikTok secara offline. Video tersimpan di folder private, TIDAK masuk galeri HP!

## ✨ Fitur
- Download video TikTok dari URL
- Feed mirip TikTok (scroll vertikal, autoplay)
- Manajemen video (hapus, cari, info storage)
- Tema dark futuristik
- Mobile friendly

## 📦 Instalasi (Termux)

```bash
# Install dependencies
pkg update && pkg upgrade
pkg install python python-pip git ffmpeg

# Clone repo
git clone https://github.com/leonorenexus/DragonicXD-TikTok-Viewer.git
cd DragonicXD-TikTok-Viewer

# Install Python packages
pip install -r backend/requirements.txt

# Jalankan
bash run.sh
