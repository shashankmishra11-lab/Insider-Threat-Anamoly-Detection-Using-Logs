// Main JavaScript file for the dashboard

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the upload form handler
    const uploadForm = document.getElementById('uploadForm');
    const uploadArea = document.querySelector('.upload-area');
    const loadingOverlay = document.getElementById('loadingOverlay');
    
    uploadForm.addEventListener('submit', handleFileUpload);
    
    // Add drag and drop functionality
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('border-primary');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('border-primary');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('border-primary');
        const file = e.dataTransfer.files[0];
        if (file) {
            const fileInput = document.getElementById('logFile');
            fileInput.files = e.dataTransfer.files;
            handleFileUpload(e);
        }
    });

    // Load initial data
    loadAnomalies();
});

function showLoading() {
    document.getElementById('loadingOverlay').classList.remove('d-none');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('d-none');
}

function showNotification(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = message;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

async function handleFileUpload(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('logFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showNotification('Please select a file first.', 'danger');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    showLoading();
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        if (data.error) {
            showNotification(data.error, 'danger');
        } else {
            showNotification(`File processed successfully. Found ${data.anomalies_count} anomalies.`);
            await loadAnomalies();
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('An error occurred while processing the file.', 'danger');
    } finally {
        hideLoading();
    }
}

async function loadAnomalies() {
    try {
        const response = await fetch('/anomalies');
        const data = await response.json();
        
        updateDashboard(data);
        updateCharts(data);
        populateTable(data);
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to load anomalies.', 'danger');
    }
}

function updateDashboard(data) {
    // Update summary statistics with animations
    animateNumber('totalAnomalies', data.length);
    
    const uniqueUsers = new Set(data.map(a => a.user_id)).size;
    animateNumber('highRiskUsers', uniqueUsers);
    
    const latestDate = new Date(Math.max(...data.map(a => new Date(a.timestamp))));
    document.getElementById('latestDetection').textContent = latestDate.toLocaleDateString();
}

function animateNumber(elementId, final, duration = 1000) {
    const element = document.getElementById(elementId);
    const start = parseInt(element.textContent) || 0;
    const step = Math.ceil((final - start) / (duration / 16));
    let current = start;
    
    const animate = () => {
        current += step;
        if ((step > 0 && current >= final) || (step < 0 && current <= final)) {
            element.textContent = final;
        } else {
            element.textContent = current;
            requestAnimationFrame(animate);
        }
    };
    
    animate();
}

function updateCharts(data) {
    // Dark theme for charts
    const chartConfig = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: {
            color: '#ffffff'
        },
        showlegend: true,
        legend: {
            bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#ffffff' }
        }
    };

    // Anomaly Distribution Chart
    const anomalyTypes = data.reduce((acc, curr) => {
        acc[curr.anomaly_type] = (acc[curr.anomaly_type] || 0) + 1;
        return acc;
    }, {});
    
    Plotly.newPlot('anomalyChart', [{
        values: Object.values(anomalyTypes),
        labels: Object.keys(anomalyTypes),
        type: 'pie',
        textinfo: 'label+percent',
        hoverinfo: 'label+value',
        marker: {
            colors: ['#3498db', '#e74c3c', '#f39c12', '#2ecc71']
        }
    }], {
        ...chartConfig,
        height: 350,
        margin: { t: 20, b: 20, l: 20, r: 20 }
    });
    
    // Time Pattern Chart
    const hourlyDistribution = Array(24).fill(0);
    data.forEach(a => {
        const hour = new Date(a.timestamp).getHours();
        hourlyDistribution[hour]++;
    });
    
    Plotly.newPlot('timePatternChart', [{
        x: Array.from({length: 24}, (_, i) => i),
        y: hourlyDistribution,
        type: 'bar',
        marker: {
            color: '#3498db'
        }
    }], {
        ...chartConfig,
        height: 350,
        margin: { t: 20, b: 40, l: 40, r: 20 },
        xaxis: {
            title: 'Hour of Day',
            gridcolor: '#404040'
        },
        yaxis: {
            title: 'Number of Anomalies',
            gridcolor: '#404040'
        }
    });
}

function populateTable(data) {
    const tbody = document.querySelector('#anomaliesTable tbody');
    tbody.innerHTML = '';
    
    data.forEach(anomaly => {
        const row = document.createElement('tr');
        const riskScore = anomaly.score;
        
        if (riskScore < 0.3) {
            row.classList.add('high-risk');
        } else if (riskScore < 0.6) {
            row.classList.add('medium-risk');
        }
        
        row.innerHTML = `
            <td>
                <div class="d-flex align-items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="me-2">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                        <circle cx="12" cy="7" r="4"/>
                    </svg>
                    ${anomaly.user_id}
                </div>
            </td>
            <td>${new Date(anomaly.timestamp).toLocaleString()}</td>
            <td>${anomaly.action}</td>
            <td>${anomaly.resource}</td>
            <td>${anomaly.ip_address}</td>
            <td>
                <span class="badge bg-${riskScore < 0.3 ? 'danger' : riskScore < 0.6 ? 'warning' : 'success'}">
                    ${anomaly.anomaly_type}
                </span>
            </td>
            <td>
                <div class="d-flex align-items-center">
                    <div class="progress flex-grow-1" style="height: 6px;">
                        <div class="progress-bar bg-${riskScore < 0.3 ? 'danger' : riskScore < 0.6 ? 'warning' : 'success'}"
                             style="width: ${(1 - riskScore) * 100}%">
                        </div>
                    </div>
                    <span class="ms-2">${riskScore.toFixed(3)}</span>
                </div>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

function exportData(format) {
    window.location.href = `/export?format=${format}`;
}