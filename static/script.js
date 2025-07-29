let currentChart = null;

// Toast notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast show ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// AMC Page
function initializeAMCPage() {
    const amcSelect = document.getElementById('amc-select');
    const viewBtn = document.getElementById('view-schemes-btn');
    
    if (amcSelect && viewBtn) {
        loadAMCs();
        
        amcSelect.addEventListener('change', function() {
            viewBtn.disabled = !this.value;
        });
        
        viewBtn.addEventListener('click', function() {
            if (amcSelect.value) {
                window.location.href = `/schemes/${encodeURIComponent(amcSelect.value)}`;
            }
        });
    }
}

async function loadAMCs() {
    const loader = document.getElementById('amc-loader');
    const amcSelect = document.getElementById('amc-select');
    
    if (!loader || !amcSelect) return;
    
    loader.style.display = 'block';
    
    try {
        const response = await fetch("/get_amc");
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json();
        amcSelect.innerHTML = '<option value="">-- Select AMC --</option>';
        
        data.data.forEach(amc => {
            const option = document.createElement('option');
            option.value = amc;
            option.textContent = amc;
            amcSelect.appendChild(option);
        });
        
        showToast(`${data.data.length} AMCs loaded`, 'success');
    } catch (error) {
        console.error('Error fetching AMCs:', error);
        showToast('Failed to load AMCs. Please try again.', 'error');
    } finally {
        loader.style.display = 'none';
    }
}

// Schemes Page
function initializeSchemesPage() {
    const amc = document.getElementById('schemes-container')?.dataset.amc;
    if (amc) {
        loadSchemes(amc);
    }
}

async function loadSchemes(amc) {
    const loader = document.getElementById('scheme-loader');
    const schemeList = document.getElementById('scheme-list');
    
    if (!loader || !schemeList) return;
    
    loader.style.display = 'block';
    schemeList.innerHTML = '';
    
    try {
        const response = await fetch(`/get_schemes/${encodeURIComponent(amc)}`);
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json();
        
        if (data.data.length === 0) {
            schemeList.innerHTML = '<div class="empty-state"><p>No schemes found for this AMC</p></div>';
            return;
        }

        data.data.forEach(scheme => {
            const card = document.createElement('div');
            card.className = 'scheme-card';
            card.innerHTML = `
                <h3>${scheme}</h3>
                <div class="scheme-actions">
                    <button onclick="window.location.href='/scheme-details/${encodeURIComponent(scheme)}'">
                        <i class="fas fa-eye"></i> View Details
                    </button>
                </div>
            `;
            schemeList.appendChild(card);
        });
        
        showToast(`${data.data.length} schemes loaded`, 'success');
    } catch (error) {
        console.error('Error fetching schemes:', error);
        showToast('Failed to load schemes. Please try again.', 'error');
    } finally {
        loader.style.display = 'none';
    }
}

// Scheme Details Page
function initializeSchemeDetails() {
    const schemeCode = document.getElementById('scheme-details')?.dataset.schemeCode;
    if (schemeCode) {
        fetchHistoricalNAV(schemeCode);
    }
}

async function fetchHistoricalNAV(schemeCode) {
    try {
        const response = await fetch(`/get_historical_nav/${schemeCode}`);
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json();
        
        if (data.error) throw new Error(data.error);
        if (data.scheme.length === 0) throw new Error('No historical data available');
        
        // Reverse to show chronological order
        const schemeData = data.scheme.reverse();
        const niftyData = data.nifty50.reverse();
        
        renderComparisonChart(schemeData, niftyData);
        calculatePerformance(schemeData, niftyData);
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('navChart').innerHTML = `
            <div class="chart-error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${error.message || 'Could not load historical data'}</p>
            </div>
        `;
        resetPerformanceMetrics();
    }
}

function renderNAVChart(history) {
    const ctx = document.getElementById('navChart').getContext('2d');
    
    // Reverse to show chronological order
    history.reverse();
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: history.map(item => item.date),
            datasets: [{
                label: 'NAV Value',
                data: history.map(item => item.nav),
                borderColor: '#4361ee',
                backgroundColor: 'rgba(67, 97, 238, 0.1)',
                borderWidth: 2,
                tension: 0.1,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                    callbacks: {
                        label: (context) => `NAV: ₹${context.parsed.y.toFixed(4)}`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: (value) => '₹' + value.toFixed(2)
                    }
                }
            }
        }
    });
}

function renderComparisonChart(schemeData, niftyData) {
    const ctx = document.getElementById('navChart').getContext('2d');
    
    // Destroy previous chart if exists
    if (currentChart) {
        currentChart.destroy();
    }
    
    // Normalize both datasets to percentage change from first point
    const schemeBase = schemeData[0].nav;
    const niftyBase = niftyData[0].close;
    
    currentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: schemeData.map(item => item.date),
            datasets: [
                {
                    label: 'Scheme Performance (%)',
                    data: schemeData.map(item => ((item.nav - schemeBase) / schemeBase * 100)),
                    borderColor: '#4361ee',
                    backgroundColor: 'rgba(67, 97, 238, 0.1)',
                    borderWidth: 2,
                    tension: 0.1,
                    fill: true
                },
                {
                    label: 'Nifty 50 Performance (%)',
                    data: niftyData.map(item => ((item.close - niftyBase) / niftyBase * 100)),
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    borderWidth: 2,
                    tension: 0.1,
                    fill: false,
                    borderDash: [5, 5]
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(2)}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: (value) => `${value}%`
                    },
                    title: {
                        display: true,
                        text: 'Percentage Change'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
}

// Calculate performance metrics
function calculatePerformance(schemeData, niftyData) {
    if (schemeData.length < 2 || niftyData.length < 2) return;
    
    const schemeStart = schemeData[0].nav;
    const schemeEnd = schemeData[schemeData.length - 1].nav;
    const schemeReturn = ((schemeEnd - schemeStart) / schemeStart) * 100;
    
    const niftyStart = niftyData[0].close;
    const niftyEnd = niftyData[niftyData.length - 1].close;
    const niftyReturn = ((niftyEnd - niftyStart) / niftyStart) * 100;
    
    const outperformance = schemeReturn - niftyReturn;
    
    // Update the metric cards
    updateMetricCard('schemeReturn', schemeReturn);
    updateMetricCard('niftyReturn', niftyReturn);
    updateMetricCard('outperformance', outperformance);
}

function updateMetricCard(elementId, value) {
    const element = document.getElementById(elementId).querySelector('.metric-value');
    element.textContent = `${value.toFixed(2)}%`;
    element.className = `metric-value ${value >= 0 ? 'positive' : 'negative'}`;
}

function resetPerformanceMetrics() {
    const metrics = ['schemeReturn', 'niftyReturn', 'outperformance'];
    metrics.forEach(metric => {
        const element = document.getElementById(metric).querySelector('.metric-value');
        element.textContent = '--';
        element.className = 'metric-value';
    });
}

// Add event listener for the toggle
document.addEventListener("DOMContentLoaded", function() {
    // Initialize page based on which container exists
    if (document.getElementById('amc-select')) {
        initializeAMCPage();
    } else if (document.getElementById('schemes-container')) {
        initializeSchemesPage();
    } else if (document.getElementById('scheme-details')) {
        initializeSchemeDetails();
    }

    // Comparison toggle event listener
    const compareToggle = document.getElementById('compareToggle');
    if (compareToggle) {
        compareToggle.addEventListener('change', function() {
            const schemeCode = document.getElementById('scheme-details')?.dataset.schemeCode;
            if (schemeCode) {
                fetchHistoricalNAV(schemeCode);
            }
        });
    }
});
