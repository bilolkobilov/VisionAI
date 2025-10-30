/**
 * VisionAI Enhanced Frontend JavaScript
 * Improved UX with better responsiveness and animations
 */

// Global state
let currentFile = null;
let currentResults = null;
let cameraStream = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    checkHealth();
    initializeAnimations();
});

/**
 * Initialize all event listeners
 */
function initializeEventListeners() {
    const fileInput = document.getElementById('fileInput');
    const dropZone = document.getElementById('dropZone');

    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop with visual feedback
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('scale-105');
        dropZone.style.borderColor = '#3b82f6';
        dropZone.style.backgroundColor = 'rgba(59, 130, 246, 0.05)';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('scale-105');
        dropZone.style.borderColor = '';
        dropZone.style.backgroundColor = '';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('scale-105');
        dropZone.style.borderColor = '';
        dropZone.style.backgroundColor = '';

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    // Click to upload
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    // URL input - Enter key
    document.getElementById('urlInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') analyzeUrl();
    });

    // Close help modal on outside click
    document.getElementById('helpModal').addEventListener('click', (e) => {
        if (e.target.id === 'helpModal') closeHelp();
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeHelp();
            cancelPreview();
        }
    });
}

/**
 * Initialize scroll animations
 */
function initializeAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
            }
        });
    }, { threshold: 0.1 });

    // Observe result cards
    document.querySelectorAll('.bg-white').forEach(el => {
        observer.observe(el);
    });
}

/**
 * Check API health with retry
 */
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        if (data.status === 'healthy') {
            updateStatus('Ready', 'green');
        }
    } catch (error) {
        updateStatus('Offline', 'red');
        showToast('⚠️ Cannot connect to server. Please start the backend.', 'error');
        // Retry after 5 seconds
        setTimeout(checkHealth, 5000);
    }
}

/**
 * Update status badge with animation
 */
function updateStatus(text, color) {
    const badge = document.getElementById('statusBadge');
    const colors = {
        green: { bg: 'bg-green-100', text: 'text-green-700', dot: 'bg-green-500' },
        yellow: { bg: 'bg-yellow-100', text: 'text-yellow-700', dot: 'bg-yellow-500' },
        red: { bg: 'bg-red-100', text: 'text-red-700', dot: 'bg-red-500' }
    };

    const c = colors[color] || colors.green;
    badge.className = `px-3 sm:px-4 py-1.5 sm:py-2 ${c.bg} ${c.text} rounded-full text-xs sm:text-sm font-semibold flex items-center space-x-2 shadow-md transition-all`;
    badge.innerHTML = `
        <span class="w-2 h-2 ${c.dot} rounded-full ${color === 'green' ? 'animate-pulse' : ''}"></span>
        <span class="hidden sm:inline">${text}</span>
        <span class="sm:hidden">${color === 'green' ? '✓' : color === 'yellow' ? '⏳' : '✕'}</span>
    `;
}

/**
 * Switch between tabs with smooth transition
 */
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active', 'text-blue-600', 'border-blue-600', 'bg-blue-50');
        btn.classList.add('text-gray-600');
    });

    const activeBtn = event.target.closest('.tab-btn');
    activeBtn.classList.add('active', 'text-blue-600', 'border-blue-600', 'bg-blue-50');
    activeBtn.classList.remove('text-gray-600');

    // Update tab content with fade effect
    document.querySelectorAll('.tab-content').forEach(content => {
        content.style.opacity = '0';
        setTimeout(() => content.classList.add('hidden'), 200);
    });

    setTimeout(() => {
        const targetTab = document.getElementById(`${tabName}Tab`);
        targetTab.classList.remove('hidden');
        setTimeout(() => targetTab.style.opacity = '1', 50);
    }, 200);

    // Reset preview and camera
    hidePreview();
    if (tabName !== 'camera') {
        stopCamera();
    }
}

/**
 * Handle file selection
 */
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) handleFile(file);
}

/**
 * Process selected file with validation
 */
function handleFile(file) {
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'];

    if (!validTypes.includes(file.type)) {
        showToast('❌ Invalid file type. Please upload an image.', 'error');
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        showToast('❌ File exceeds 10MB limit', 'error');
        return;
    }

    currentFile = file;
    showToast(`✅ ${file.name} loaded`, 'success');

    const reader = new FileReader();
    reader.onload = (e) => showPreview(e.target.result);
    reader.readAsDataURL(file);
}

/**
 * Show image preview with animation
 */
function showPreview(imageSrc) {
    const previewSection = document.getElementById('previewSection');
    const previewImage = document.getElementById('previewImage');

    previewImage.src = imageSrc;
    previewImage.style.opacity = '0';

    previewSection.classList.remove('hidden');
    previewSection.scrollIntoView({ behavior: 'smooth', block: 'center' });

    setTimeout(() => {
        previewImage.style.transition = 'opacity 0.5s';
        previewImage.style.opacity = '1';
    }, 100);
}

/**
 * Hide preview
 */
function hidePreview() {
    document.getElementById('previewSection').classList.add('hidden');
}

/**
 * Cancel preview
 */
function cancelPreview() {
    hidePreview();
    currentFile = null;
    document.getElementById('fileInput').value = '';
    showToast('Preview cancelled', 'info');
}

/**
 * Analyze uploaded image
 */
async function analyzeImage() {
    if (!currentFile) {
        showToast('❌ No file selected', 'error');
        return;
    }

    hidePreview();
    showLoading();
    updateStatus('Analyzing', 'yellow');

    const formData = new FormData();
    formData.append('file', currentFile);

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        hideLoading();

        if (result.success) {
            displayResults(result.data);
            updateStatus('Complete', 'green');
            showToast('✅ Analysis completed!', 'success');
        } else {
            updateStatus('Error', 'red');
            showToast('❌ ' + result.message, 'error');
        }
    } catch (error) {
        hideLoading();
        updateStatus('Error', 'red');
        showToast('❌ Analysis failed: ' + error.message, 'error');
    }
}

/**
 * Analyze image from URL
 */
async function analyzeUrl() {
    const urlInput = document.getElementById('urlInput');
    const url = urlInput.value.trim();

    if (!url) {
        showToast('❌ Please enter an image URL', 'error');
        urlInput.focus();
        return;
    }

    try {
        new URL(url);
    } catch {
        showToast('❌ Invalid URL format', 'error');
        urlInput.focus();
        return;
    }

    showLoading();
    updateStatus('Analyzing', 'yellow');

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'url', data: url })
        });

        const result = await response.json();
        hideLoading();

        if (result.success) {
            displayResults(result.data);
            updateStatus('Complete', 'green');
            showToast('✅ Analysis completed!', 'success');
        } else {
            updateStatus('Error', 'red');
            showToast('❌ ' + result.message, 'error');
        }
    } catch (error) {
        hideLoading();
        updateStatus('Error', 'red');
        showToast('❌ Analysis failed: ' + error.message, 'error');
    }
}

/**
 * Camera functions
 */
async function startCamera() {
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            }
        });

        document.getElementById('videoElement').srcObject = cameraStream;
        document.getElementById('startCameraBtn').classList.add('hidden');
        document.getElementById('cameraContainer').classList.remove('hidden');

        showToast('📷 Camera started', 'success');
    } catch (error) {
        showToast('❌ Camera access denied', 'error');
    }
}

function stopCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }
    document.getElementById('cameraContainer').classList.add('hidden');
    document.getElementById('cameraPreview').classList.add('hidden');
    document.getElementById('startCameraBtn').classList.remove('hidden');
}

function capturePhoto() {
    const video = document.getElementById('videoElement');
    const canvas = document.getElementById('canvasElement');
    const image = document.getElementById('capturedImage');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    const imageData = canvas.toDataURL('image/jpeg', 0.9);
    image.src = imageData;

    document.getElementById('cameraContainer').classList.add('hidden');
    document.getElementById('cameraPreview').classList.remove('hidden');

    showToast('📸 Photo captured!', 'success');
}

function retakePhoto() {
    document.getElementById('cameraPreview').classList.add('hidden');
    document.getElementById('cameraContainer').classList.remove('hidden');
}

async function analyzeCapture() {
    const imageData = document.getElementById('capturedImage').src;

    showLoading();
    stopCamera();
    updateStatus('Analyzing', 'yellow');

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'base64', data: imageData })
        });

        const result = await response.json();
        hideLoading();

        if (result.success) {
            displayResults(result.data);
            updateStatus('Complete', 'green');
            showToast('✅ Analysis completed!', 'success');
        } else {
            updateStatus('Error', 'red');
            showToast('❌ ' + result.message, 'error');
        }
    } catch (error) {
        hideLoading();
        updateStatus('Error', 'red');
        showToast('❌ Analysis failed: ' + error.message, 'error');
    }
}

/**
 * Display analysis results with animations
 */
function displayResults(data) {
    currentResults = data;

    const resultsSection = document.getElementById('resultsSection');
    resultsSection.classList.remove('hidden');
    resultsSection.style.opacity = '0';

    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        resultsSection.style.transition = 'opacity 0.5s';
        resultsSection.style.opacity = '1';
    }, 100);

    document.getElementById('summaryText').textContent = data.summary || 'No summary available';
    displayStatistics(data.statistics);
    displayCaptions(data.captions);
    displayLabels(data.labels);
    displayObjects(data.objects);
    displayScene(data.scene_analysis);
    displayMetadata(data.metadata);
}

/**
 * Display statistics with cards
 */
function displayStatistics(stats) {
    const container = document.getElementById('statsContainer');

    if (!stats || Object.keys(stats).length === 0) {
        container.innerHTML = '';
        return;
    }

    const icons = {
        'total_objects': '📦',
        'unique_objects': '🔢',
        'avg_confidence': '📊',
        'top_confidence': '⭐',
        'scene_matches': '🎭'
    };

    container.innerHTML = Object.entries(stats).map(([key, value]) => `
        <div class="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-4 text-center border-2 border-blue-100 hover:shadow-lg transition-all transform hover:scale-105">
            <div class="text-2xl mb-1">${icons[key] || '📈'}</div>
            <div class="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">${value}</div>
            <div class="text-xs sm:text-sm text-gray-600 mt-1 font-semibold">${formatLabel(key)}</div>
        </div>
    `).join('');
}

/**
 * Display captions
 */
function displayCaptions(captions) {
    const container = document.getElementById('captionsContainer');

    if (!captions || captions.length === 0) {
        container.innerHTML = '<p class="text-gray-500 italic text-center py-4">No captions generated</p>';
        return;
    }

    container.innerHTML = captions.map((caption, i) => `
        <div class="flex items-start space-x-3 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border-2 border-blue-100 hover:shadow-md transition-all">
            <span class="flex-shrink-0 w-7 h-7 bg-gradient-to-br from-blue-600 to-purple-600 text-white rounded-full flex items-center justify-center text-sm font-bold shadow-md">
                ${i + 1}
            </span>
            <p class="text-gray-700 flex-1 leading-relaxed">${caption}</p>
        </div>
    `).join('');
}

/**
 * Display classification labels
 */
function displayLabels(labels) {
    const container = document.getElementById('labelsContainer');

    if (!labels || labels.length === 0) {
        container.innerHTML = '<p class="text-gray-500 italic text-center py-4">No classifications found</p>';
        return;
    }

    container.innerHTML = labels.slice(0, 15).map(label => `
        <div class="space-y-2 p-3 hover:bg-blue-50 rounded-lg transition-all">
            <div class="flex justify-between items-center">
                <span class="font-semibold text-gray-800">${label.description}</span>
                <span class="text-xs sm:text-sm font-bold ${getConfidenceColorClass(label.confidence)} px-2.5 py-1 rounded-full shadow-sm">
                    ${label.confidence}%
                </span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
                <div class="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 h-2.5 rounded-full transition-all duration-500 ease-out" 
                    style="width: ${label.confidence}%"></div>
            </div>
        </div>
    `).join('');
}

/**
 * Display detected objects
 */
function displayObjects(objects) {
    const container = document.getElementById('objectsContainer');

    if (!objects || objects.length === 0) {
        container.innerHTML = '<p class="text-gray-500 italic text-center py-4">No objects detected</p>';
        return;
    }

    container.innerHTML = objects.map(obj => `
        <div class="flex items-center justify-between p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl border-2 border-indigo-100 hover:shadow-md transition-all">
            <div class="flex items-center space-x-3">
                <span class="text-3xl">📦</span>
                <div>
                    <div class="font-bold text-gray-800">${obj.name}</div>
                    <div class="text-sm text-gray-600">Quantity: <span class="font-semibold">${obj.count}</span></div>
                </div>
            </div>
            <span class="text-xs sm:text-sm font-bold ${getConfidenceColorClass(obj.confidence)} px-2.5 py-1 rounded-full shadow-sm">
                ${obj.confidence}%
            </span>
        </div>
    `).join('');
}

/**
 * Display scene analysis
 */
function displayScene(scenes) {
    const container = document.getElementById('sceneContainer');

    if (!scenes || scenes.length === 0) {
        container.innerHTML = '<p class="text-gray-500 italic text-center py-4">No scene analysis available</p>';
        return;
    }

    container.innerHTML = scenes.map(scene => `
        <div class="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border-2 border-purple-100 hover:shadow-md transition-all">
            <span class="font-bold text-gray-800">${scene.category}</span>
            <span class="text-xs sm:text-sm font-bold ${getConfidenceColorClass(scene.confidence)} px-2.5 py-1 rounded-full shadow-sm">
                ${scene.confidence}%
            </span>
        </div>
    `).join('');
}

/**
 * Display metadata
 */
function displayMetadata(metadata) {
    const container = document.getElementById('metadataContainer');

    if (!metadata) {
        container.innerHTML = '<p class="text-gray-500 italic text-center py-4">No metadata available</p>';
        return;
    }

    const items = [
        { icon: '📐', label: 'Dimensions', value: `${metadata.width} × ${metadata.height} px` },
        { icon: '📄', label: 'Format', value: metadata.format },
        { icon: '💾', label: 'Size', value: `${metadata.size_kb} KB` },
        { icon: '📏', label: 'Aspect Ratio', value: metadata.aspect_ratio }
    ];

    container.innerHTML = items.map(item => `
        <div class="flex justify-between items-center py-3 border-b border-gray-100 last:border-0 hover:bg-blue-50 px-2 rounded transition-all">
            <span class="text-gray-600 flex items-center space-x-2">
                <span>${item.icon}</span>
                <span class="font-medium">${item.label}</span>
            </span>
            <span class="font-bold text-gray-800">${item.value}</span>
        </div>
    `).join('');
}

/**
 * Utility functions
 */
function formatLabel(key) {
    return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function getConfidenceColorClass(confidence) {
    if (confidence >= 70) return 'text-green-700 bg-green-100';
    if (confidence >= 40) return 'text-yellow-700 bg-yellow-100';
    return 'text-red-700 bg-red-100';
}

/**
 * Loading management
 */
function showLoading() {
    hidePreview();
    document.getElementById('resultsSection').classList.add('hidden');
    const loadingSection = document.getElementById('loadingSection');
    loadingSection.classList.remove('hidden');
    loadingSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function hideLoading() {
    document.getElementById('loadingSection').classList.add('hidden');
}

/**
 * Export functions
 */
async function exportJSON() {
    if (!currentResults) return;

    try {
        const response = await fetch('/api/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ format: 'json', data: currentResults })
        });

        const result = await response.json();

        if (result.success) {
            window.open(`/api/download/${result.data.filename}`, '_blank');
            showToast('✅ JSON exported successfully', 'success');
        }
    } catch (error) {
        showToast('❌ Export failed', 'error');
    }
}

async function exportPDF() {
    if (!currentResults) return;

    try {
        const response = await fetch('/api/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ format: 'pdf', data: currentResults })
        });

        const result = await response.json();

        if (result.success) {
            window.open(`/api/download/${result.data.filename}`, '_blank');
            showToast('✅ PDF exported successfully', 'success');
        }
    } catch (error) {
        showToast('❌ Export failed', 'error');
    }
}

/**
 * Start new analysis
 */
function newAnalysis() {
    document.getElementById('resultsSection').classList.add('hidden');
    hidePreview();
    currentFile = null;
    currentResults = null;
    document.getElementById('fileInput').value = '';
    document.getElementById('urlInput').value = '';
    updateStatus('Ready', 'green');
    window.scrollTo({ top: 0, behavior: 'smooth' });
    showToast('Ready for new analysis', 'info');
}

/**
 * Help modal
 */
function showHelp() {
    document.getElementById('helpModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeHelp() {
    document.getElementById('helpModal').classList.add('hidden');
    document.body.style.overflow = 'auto';
}

/**
 * Toast notification system
 */
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');

    toastMessage.textContent = message;

    const colors = {
        error: 'bg-red-600',
        success: 'bg-green-600',
        info: 'bg-blue-600'
    };

    toast.className = `fixed bottom-4 right-4 sm:bottom-8 sm:right-8 ${colors[type] || colors.info} text-white px-4 sm:px-6 py-3 sm:py-4 rounded-xl shadow-2xl transform translate-y-0 transition-all duration-300 z-50 max-w-xs sm:max-w-md text-sm sm:text-base`;

    setTimeout(() => {
        toast.classList.add('translate-y-32');
    }, type === 'error' ? 5000 : 3000);
}