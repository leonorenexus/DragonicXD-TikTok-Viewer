#!/bin/bash

echo "🐉 DRAGONICXD OFFLINE TIKTOK VIEWER"
echo "=================================="
echo ""

# Buat folder data
mkdir -p data/videos

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r backend/requirements.txt

# Jalankan backend
echo "🚀 Starting backend server..."
cd backend
python3 app.py &
BACKEND_PID=$!

echo ""
echo "✅ Server running at: http://localhost:5000"
echo "📱 Buka frontend/index.html di browser"
echo ""
echo "🔴 Press Ctrl+C to stop"

# Wait for background process
wait $BACKEND_PID
