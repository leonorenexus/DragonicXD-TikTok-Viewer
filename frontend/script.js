// ============================================
// DRAGONICXD OFFLINE TIKTOK VIEWER
// ============================================

const API_BASE = 'http://localhost:5000';
let currentVideos = [];
let currentIndex = 0;
let isPlaying = false;
let observer = null;

// ============ DOM ELEMENTS ============
const feedContainer = document.getElementById('feedContainer');
const floatingBtn = document.getElementById('floatingBtn');
const modal = document.getElementById('downloadModal');
const closeModal = document.getElementById('closeModal');
const urlInput = document.getElementById('urlInput');
const downloadBtn = document.getElementById('downloadBtn');
const statusMsg = document.getElementById('downloadStatus');
const videoCount = document.getElementById('videoCount');
const storageInfo = document.getElementById('storageInfo');

// ============ FETCH FEED ============
async function loadFeed() {
    try {
        const response = await fetch(`${API_BASE}/api/feed`);
        const data = await response.json();
        
        if (data.success) {
            currentVideos = data.videos;
            renderFeed();
            updateInfo();
        }
    } catch (error) {
        console.error('Gagal load feed:', error);
        feedContainer.innerHTML = `
            <div class="empty-state">
                <div class="icon">📡</div>
                <h2>Gagal Konek ke Server</h2>
                <p>Pastikan server backend berjalan di port 5000</p>
            </div>
        `;
    }
}

// ============ RENDER FEED ============
function renderFeed() {
    if (currentVideos.length === 0) {
        feedContainer.innerHTML = `
            <div class="empty-state">
                <div class="icon">🎬</div>
                <h2>Belum Ada Video</h2>
                <p>Klik tombol + di pojok kanan bawah untuk download video TikTok</p>
            </div>
        `;
        return;
    }
    
    feedContainer.innerHTML = '';
    
    currentVideos.forEach((video, index) => {
        const wrapper = document.createElement('div');
        wrapper.className = 'video-wrapper';
        wrapper.dataset.index = index;
        
        // Video element
        const videoEl = document.createElement('video');
        videoEl.src = `${API_BASE}/api/video/${video.id}`;
        videoEl.preload = 'metadata';
        videoEl.playsInline = true;
        videoEl.setAttribute('playsinline', '');
        
        // Controls
        const controls = document.createElement('div');
        controls.className = 'video-controls';
        
        const muteBtn = document.createElement('button');
        muteBtn.className = 'mute-btn';
        muteBtn.textContent = '🔊';
        
        const progressContainer = document.createElement('div');
        progressContainer.className = 'progress-container';
        
        const progressFill = document.createElement('div');
        progressFill.className = 'progress-fill';
        
        progressContainer.appendChild(progressFill);
        
        const titleSpan = document.createElement('span');
        titleSpan.className = 'video-title';
        titleSpan.textContent = video.title || 'No Title';
        
        controls.appendChild(muteBtn);
        controls.appendChild(progressContainer);
        controls.appendChild(titleSpan);
        
        wrapper.appendChild(videoEl);
        wrapper.appendChild(controls);
        feedContainer.appendChild(wrapper);
        
        // Event listeners
        videoEl.addEventListener('timeupdate', () => {
            if (videoEl.duration) {
                progressFill.style.width = `${(videoEl.currentTime / videoEl.duration) * 100}%`;
            }
        });
        
        muteBtn.addEventListener('click', () => {
            videoEl.muted = !videoEl.muted;
            muteBtn.textContent = videoEl.muted ? '🔇' : '🔊';
        });
        
        progressContainer.addEventListener('click', (e) => {
            const rect = progressContainer.getBoundingClientRect();
            const pos = (e.clientX - rect.left) / rect.width;
            videoEl.currentTime = pos * videoEl.duration;
        });
        
        wrapper.addEventListener('click', () => {
            controls.classList.toggle('active');
        });
    });
    
    // Setup Intersection Observer for autoplay
    setupAutoplay();
    
    // Scroll ke pertama
    setTimeout(() => {
        feedContainer.scrollTop = 0;
    }, 100);
}

// ============ AUTOPLAY ============
function setupAutoplay() {
    if (observer) observer.disconnect();
    
    const videos = feedContainer.querySelectorAll('.video-wrapper video');
    
    observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const video = entry.target;
            if (entry.isIntersecting) {
                video.play().catch(() => {});
                video.closest('.video-wrapper').classList.add('active');
            } else {
                video.pause();
                video.closest('.video-wrapper').classList.remove('active');
            }
        });
    }, { threshold: 0.7 });
    
    videos.forEach(video => observer.observe(video));
}

// ============ DOWNLOAD VIDEO ============
async function downloadVideo(url) {
    statusMsg.className = 'status-message loading';
    statusMsg.textContent = '⏳ Sedang mendownload...';
    downloadBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/api/download`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        
        const data = await response.json();
        
        if (response.status === 409) {
            statusMsg.className = 'status-message error';
            statusMsg.textContent = `⚠️ Video sudah ada: ${data.video.title}`;
            return;
        }
        
        if (data.success) {
            statusMsg.className = 'status-message success';
            statusMsg.textContent = `✅ ${data.message}`;
            urlInput.value = '';
            await loadFeed();
        } else {
            statusMsg.className = 'status-message error';
            statusMsg.textContent = `❌ ${data.error || 'Gagal download'}`;
        }
    } catch (error) {
        statusMsg.className = 'status-message error';
        statusMsg.textContent = `❌ Error: ${error.message}`;
    } finally {
        downloadBtn.disabled = false;
    }
}

// ============ UPDATE INFO ============
async function updateInfo() {
    try {
        const response = await fetch(`${API_BASE}/api/storage`);
        const data = await response.json();
        
        if (data.success) {
            videoCount.textContent = `${data.video_count} video`;
            storageInfo.textContent = data.formatted;
        }
    } catch (error) {
        console.error('Gagal update info:', error);
    }
}

// ============ EVENT LISTENERS ============
floatingBtn.addEventListener('click', () => {
    modal.classList.add('show');
    urlInput.focus();
});

closeModal.addEventListener('click', () => {
    modal.classList.remove('show');
});

modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.classList.remove('show');
});

downloadBtn.addEventListener('click', () => {
    const url = urlInput.value.trim();
    if (!url) {
        statusMsg.className = 'status-message error';
        statusMsg.textContent = '⚠️ Masukkan URL TikTok!';
        return;
    }
    downloadVideo(url);
});

urlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') downloadBtn.click();
});

// ============ INIT ============
loadFeed();

// Refresh setiap 30 detik
setInterval(updateInfo, 30000);

console.log('🐉 DragonicXD Offline TikTok Viewer loaded!');
