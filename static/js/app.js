// Wake Word Trainer - Frontend Application

let socket;
let currentJobId = null;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    loadJobHistory();
    setupEventListeners();
    connectWebSocket();
});

function initializeApp() {
    console.log('Wake Word Trainer initialized');
}

// WebSocket Connection
function connectWebSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to training server');
    });
    
    socket.on('training_progress', function(data) {
        updateProgress(data);
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
    });
}

// Event Listeners
function setupEventListeners() {
    // Form submission
    const form = document.getElementById('trainingForm');
    form.addEventListener('submit', handleFormSubmit);
    
    // Method selection
    const methodInputs = document.querySelectorAll('input[name="method"]');
    methodInputs.forEach(input => {
        input.addEventListener('change', handleMethodChange);
    });
    
    // Preset selection
    const presetSelect = document.getElementById('preset');
    presetSelect.addEventListener('change', handlePresetChange);
    
    // Download button
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', handleDownload);
    }
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading"></span> Starting Training...';
    
    // Get form data
    const formData = new FormData(e.target);
    const data = {
        wake_word: formData.get('wake_word'),
        method: formData.get('method'),
        num_samples: parseInt(formData.get('num_samples') || 2000),
        epochs: parseInt(formData.get('epochs') || 30),
        batch_size: parseInt(formData.get('batch_size') || 512),
        learning_rate: parseFloat(formData.get('learning_rate') || 0.001),
        probability_cutoff: parseFloat(formData.get('probability_cutoff') || 0.97),
        sliding_window_size: parseInt(formData.get('sliding_window_size') || 5)
    };
    
    try {
        const response = await fetch('/api/train', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            currentJobId = result.job_id;
            showProgressSection();
            subscribeToJob(result.job_id);
            showNotification('Training started successfully!', 'success');
            
            // Reload job history
            setTimeout(() => loadJobHistory(), 1000);
        } else {
            throw new Error(result.error || 'Failed to start training');
        }
    } catch (error) {
        console.error('Error starting training:', error);
        showNotification('Error: ' + error.message, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span class="btn-icon">🚀</span> Start Training';
    }
}

// Handle method change
function handleMethodChange(e) {
    const method = e.target.value;
    document.body.className = `method-${method}`;
    
    // Update preset options
    updatePresetOptions(method);
}

// Handle preset change
function handlePresetChange(e) {
    const presetValue = e.target.value;
    if (!presetValue) return;
    
    // Fetch preset configuration
    fetch('/api/presets')
        .then(response => response.json())
        .then(data => {
            const preset = data.presets[presetValue];
            if (preset) {
                applyPreset(preset);
            }
        });
}

// Apply preset configuration
function applyPreset(preset) {
    if (preset.method) {
        document.querySelector(`input[value="${preset.method}"]`).checked = true;
        document.body.className = `method-${preset.method}`;
    }
    
    if (preset.num_samples) {
        document.getElementById('numSamples').value = preset.num_samples;
    }
    
    if (preset.epochs) {
        document.getElementById('epochs').value = preset.epochs;
    }
    
    if (preset.batch_size) {
        document.getElementById('batchSize').value = preset.batch_size;
    }
}

// Update preset options based on method
function updatePresetOptions(method) {
    const presetSelect = document.getElementById('preset');
    const options = presetSelect.options;
    
    for (let i = 0; i < options.length; i++) {
        const option = options[i];
        const value = option.value;
        
        if (value === '') continue;
        
        if (method === 'openwakeword' && value.startsWith('openwakeword')) {
            option.style.display = 'block';
        } else if (method === 'microwakeword' && value.startsWith('microwakeword')) {
            option.style.display = 'block';
        } else if (value !== '') {
            option.style.display = 'none';
        }
    }
}

// Show progress section
function showProgressSection() {
    const progressSection = document.getElementById('progressSection');
    progressSection.style.display = 'block';
    progressSection.scrollIntoView({ behavior: 'smooth' });
    
    // Reset progress
    updateProgressUI(0, 'Initializing...', 'pending');
    document.getElementById('trainingLogs').innerHTML = '';
    document.getElementById('downloadBtn').style.display = 'none';
}

// Subscribe to job updates
function subscribeToJob(jobId) {
    socket.emit('subscribe', { job_id: jobId });
}

// Update progress from WebSocket
function updateProgress(data) {
    if (data.job_id !== currentJobId) return;
    
    updateProgressUI(data.progress, data.message, data.status);
    
    if (data.logs && data.logs.length > 0) {
        updateLogs(data.logs);
    }
    
    // Show download button if completed
    if (data.status === 'completed' || data.status === 'ready_for_training') {
        document.getElementById('downloadBtn').style.display = 'inline-flex';
    }
}

// Update progress UI
function updateProgressUI(progress, message, status) {
    const progressBar = document.getElementById('progressBar');
    const progressPercent = document.getElementById('progressPercent');
    const progressMessage = document.getElementById('progressMessage');
    const statusBadge = document.getElementById('progressStatus');
    
    progressBar.style.width = progress + '%';
    progressPercent.textContent = progress + '%';
    progressMessage.textContent = message;
    
    if (status) {
        statusBadge.textContent = status.replace(/_/g, ' ');
        statusBadge.className = 'status-badge ' + status;
    }
}

// Update logs
function updateLogs(logs) {
    const logsContainer = document.getElementById('trainingLogs');
    
    logsContainer.innerHTML = logs.map(log => {
        let className = 'log-entry';
        
        if (log.toLowerCase().includes('error') || log.toLowerCase().includes('failed')) {
            className += ' error';
        } else if (log.toLowerCase().includes('warning')) {
            className += ' warning';
        } else if (log.toLowerCase().includes('success') || log.toLowerCase().includes('complete')) {
            className += ' success';
        }
        
        return `<div class="${className}">${escapeHtml(log)}</div>`;
    }).join('');
    
    // Scroll to bottom
    logsContainer.scrollTop = logsContainer.scrollHeight;
}

// Load job history
async function loadJobHistory() {
    try {
        const response = await fetch('/api/jobs');
        const data = await response.json();
        
        displayJobHistory(data.jobs);
    } catch (error) {
        console.error('Error loading jobs:', error);
    }
}

// Display job history
function displayJobHistory(jobs) {
    const jobsList = document.getElementById('jobsList');
    
    if (jobs.length === 0) {
        jobsList.innerHTML = '<p class="empty-state">No training jobs yet. Create your first wake word above!</p>';
        return;
    }
    
    jobsList.innerHTML = jobs.map(job => `
        <div class="job-card">
            <div class="job-header">
                <div>
                    <div class="job-title">"${escapeHtml(job.wake_word)}"</div>
                    <span class="job-method">${job.method}</span>
                </div>
                <span class="status-badge ${job.status}">${job.status.replace(/_/g, ' ')}</span>
            </div>
            
            <div class="job-info">
                <div>
                    <strong>Created:</strong> ${formatDate(job.created_at)}
                </div>
                <div>
                    <strong>Progress:</strong> ${job.progress}%
                </div>
            </div>
            
            <div class="job-actions">
                ${job.status === 'completed' || job.status === 'ready_for_training' ?
                    `<button class="btn btn-primary" onclick="downloadModel('${job.job_id}')">
                        <span class="btn-icon">📱</span> Download Model
                    </button>
                    <button class="btn btn-secondary" onclick="downloadJob('${job.job_id}')">
                        <span class="btn-icon">📥</span> Download All Files
                    </button>` : ''}
                ${job.status === 'running' ?
                    `<button class="btn btn-secondary" onclick="viewJob('${job.job_id}')">
                        <span class="btn-icon">👁️</span> View Progress
                    </button>` : ''}
            </div>
        </div>
    `).join('');
}

// View job details
function viewJob(jobId) {
    currentJobId = jobId;
    showProgressSection();
    subscribeToJob(jobId);
    
    // Fetch job details
    fetch(`/api/jobs/${jobId}`)
        .then(response => response.json())
        .then(job => {
            updateProgressUI(job.progress, job.logs[job.logs.length - 1] || 'Loading...', job.status);
            if (job.logs) {
                updateLogs(job.logs);
            }
        });
}

// Download model file for ESPHome
function downloadModel(jobId) {
    window.location.href = `/api/jobs/${jobId}/download-model`;
}

// Download job files
function downloadJob(jobId) {
    window.location.href = `/api/jobs/${jobId}/download`;
}

// Handle download button click
function handleDownload() {
    if (currentJobId) {
        downloadModel(currentJobId);
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Style notification
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '1rem 1.5rem',
        borderRadius: '8px',
        backgroundColor: type === 'success' ? 'var(--success-color)' : 
                        type === 'error' ? 'var(--danger-color)' : 
                        'var(--primary-color)',
        color: 'white',
        fontWeight: '600',
        boxShadow: 'var(--shadow-lg)',
        zIndex: '9999',
        animation: 'slideIn 0.3s ease'
    });
    
    document.body.appendChild(notification);
    
    // Remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
