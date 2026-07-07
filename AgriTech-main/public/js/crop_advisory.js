const API_BASE = '/api/v1/crop-advisory';

const COMPANION_RULES = {
    'Basil|Tomato': {
        type: 'friends',
        title: 'Tomato + Basil are friends!',
        message: 'Basil can help deter pests and improve the growing environment around tomatoes.',
    },
    'Marigold|Tomato': {
        type: 'friends',
        title: 'Tomato + Marigold are friends!',
        message: 'Marigolds are commonly planted near tomatoes to help discourage pests.',
    },
    'Beans|Corn': {
        type: 'friends',
        title: 'Corn + Beans are friends!',
        message: 'Beans can climb corn stalks while helping add nitrogen to the soil.',
    },
    'Corn|Squash': {
        type: 'friends',
        title: 'Corn + Squash are friends!',
        message: 'Squash helps shade the soil, which can support a healthier corn bed.',
    },
    'Carrot|Onion': {
        type: 'friends',
        title: 'Carrot + Onion are friends!',
        message: 'These crops are often paired because they can help confuse pests that target each other.',
    },
    'Cabbage|Dill': {
        type: 'friends',
        title: 'Cabbage + Dill are friends!',
        message: 'Dill can support beneficial insects that help protect cabbage family crops.',
    },
    'Lettuce|Carrot': {
        type: 'friends',
        title: 'Lettuce + Carrot are friends!',
        message: 'They occupy different layers of the bed and usually share space well.',
    },
    'Pepper|Basil': {
        type: 'friends',
        title: 'Pepper + Basil are friends!',
        message: 'Basil is a common companion for peppers in mixed vegetable beds.',
    },
    'Potato|Tomato': {
        type: 'foes',
        title: 'Potato + Tomato are foes!',
        message: 'They belong to the same family and can share disease pressure and nutrient demand.',
    },
    'Beans|Onion': {
        type: 'foes',
        title: 'Beans + Onion are foes!',
        message: 'Onions can suppress bean growth when planted too close together.',
    },
    'Cabbage|Tomato': {
        type: 'foes',
        title: 'Cabbage + Tomato are foes!',
        message: 'These crops can compete for resources and are not ideal bedmates in tight spaces.',
    },
};

function normalizePair(cropA, cropB) {
    return [cropA, cropB].sort().join('|');
}

function updateCompanionResult(type, title, message, crops) {
    const result = document.getElementById('companionResult');
    if (!result) return;

    result.className = `compatibility-result ${type}`;
    result.innerHTML = `
        <h3>${title}</h3>
        <p>${message}</p>
        ${crops ? `<div class="compatibility-meta"><span class="compatibility-pill">${crops[0]}</span><span class="compatibility-pill">${crops[1]}</span></div>` : ''}
    `;
}

function checkCompanionPlanting() {
    const cropA = document.getElementById('companionCropA').value;
    const cropB = document.getElementById('companionCropB').value;

    if (!cropA || !cropB) {
        updateCompanionResult(
            'neutral',
            'Choose two crops to compare',
            'Select both Crop A and Crop B to see whether they make a good planting pair.'
        );
        return;
    }

    if (cropA === cropB) {
        updateCompanionResult(
            'neutral',
            'Pick two different crops',
            'Companion planting works best when comparing two different plants.'
        );
        return;
    }

    const relation = COMPANION_RULES[normalizePair(cropA, cropB)];

    if (relation) {
        updateCompanionResult(relation.type, relation.title, relation.message, [cropA, cropB]);
        return;
    }

    updateCompanionResult(
        'neutral',
        'No direct pairing in the current library',
        'This combination is not in the quick-reference list yet. Try a well-known pairing like Tomato + Basil or Potato + Tomato.'
    );
}

function resetCompanionChecker() {
    const cropA = document.getElementById('companionCropA');
    const cropB = document.getElementById('companionCropB');
    if (cropA) cropA.value = '';
    if (cropB) cropB.value = '';

    updateCompanionResult(
        'neutral',
        'Choose two crops to compare',
        'You’ll see a quick companion planting verdict here.'
    );
}

function bindCompanionChecker() {
    const cropA = document.getElementById('companionCropA');
    const cropB = document.getElementById('companionCropB');

    if (cropA) cropA.addEventListener('change', checkCompanionPlanting);
    if (cropB) cropB.addEventListener('change', checkCompanionPlanting);
}

// Lightweight loader helper
function ensureLoaderStyles() {
    if (document.getElementById('agri-loader-styles')) return;
    const style = document.createElement('style');
    style.id = 'agri-loader-styles';
    style.textContent = `
    .agri-loader{display:flex;align-items:center;justify-content:center;padding:24px}
    .agri-spinner{width:36px;height:36px;border-radius:50%;border:4px solid rgba(0,0,0,0.08);border-top-color:var(--primary,#16a34a);animation:agri-spin 0.9s linear infinite}
    @keyframes agri-spin{to{transform:rotate(360deg)}}
    `;
    document.head.appendChild(style);
}

function showLoader(containerId, message) {
    ensureLoaderStyles();
    const el = document.getElementById(containerId);
    if (!el) return;
    el.__orig = el.innerHTML;
    el.innerHTML = `<div class="agri-loader"><div style="text-align:center"><div class="agri-spinner" aria-hidden="true"></div>${message ? `<div style=\"margin-top:8px;color:#64748b;font-size:0.95rem\">${message}</div>` : ''}</div></div>`;
}

function hideLoader(containerId) {
    const el = document.getElementById(containerId);
    if (!el) return;
    if (el.__orig !== undefined) el.innerHTML = el.__orig;
}

async function getRecommendations() {
    const location = document.getElementById('location').value;
    const soilType = document.getElementById('soilType').value;
    
    if (!location) {
        alert('Please enter a location');
        return;
    }
    
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Please login first');
        return;
    }
    
    try {
        document.getElementById('recommendationsCard').classList.add('hidden');
        document.getElementById('alertsCard').classList.add('hidden');
        document.getElementById('climateCard').classList.add('hidden');
        document.getElementById('weatherStats').classList.add('hidden');
        showLoader('recommendationsContainer', 'Loading recommendations...');
        
        const response = await fetch(`${API_BASE}/recommendations?location=${encodeURIComponent(location)}&soil_type=${soilType || ''}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            renderRecommendations(data.data);
            hideLoader('recommendationsContainer');
            
            document.getElementById('statTemp').textContent = `${data.data.current_weather.temperature}C`;
            document.getElementById('statHumidity').textContent = `${data.data.current_weather.humidity}%`;
            document.getElementById('statCondition').textContent = data.data.current_weather.condition;
            document.getElementById('weatherStats').classList.remove('hidden');
            
            loadAlerts();
            loadClimateAnalysis(location);
        } else {
            const errorData = await response.json();
            hideLoader('recommendationsContainer');
            alert(`Error: ${errorData.message}`);
        }
    } catch (error) {
        console.error('Error fetching recommendations:', error);
        hideLoader('recommendationsContainer');
        alert('Error fetching recommendations. Please try again.');
    }
}

function renderRecommendations(data) {
    const container = document.getElementById('recommendationsContainer');
    
    if (!data.recommendations || data.recommendations.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #64748b;">No recommendations available for this location.</p>';
        return;
    }
    
    container.innerHTML = `
        <div class="current-weather">
            <div class="weather-item">
                <div class="label">Current Month</div>
                <div class="value">${data.current_month}</div>
            </div>
            <div class="weather-item">
                <div class="label">Temperature</div>
                <div class="value">${data.current_weather.temperature}C</div>
            </div>
            <div class="weather-item">
                <div class="label">Humidity</div>
                <div class="value">${data.current_weather.humidity}%</div>
            </div>
        </div>
        <div class="recommendations-grid">
            ${data.recommendations.map(rec => `
                <div class="recommendation-item">
                    <div class="recommendation-header">
                        <div class="recommendation-title">${rec.crop}</div>
                        <div class="score-badge">${rec.score}% Match</div>
                    </div>
                    <ul class="reasons-list">
                        ${rec.reasons.map(reason => `<li>${reason}</li>`).join('')}
                    </ul>
                    <div class="info-grid">
                        <div class="info-item">
                            <label>Planting Time</label>
                            <span>${rec.planting_time.join(', ')}</span>
                        </div>
                        <div class="info-item">
                            <label>Harvesting Time</label>
                            <span>${rec.harvesting_time.join(', ')}</span>
                        </div>
                        <div class="info-item">
                            <label>Water Requirement</label>
                            <span>${rec.water_requirement}</span>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    
    document.getElementById('recommendationsCard').classList.remove('hidden');
}

async function loadAlerts() {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        showLoader('alertsContainer', 'Loading alerts...');
        const response = await fetch(`${API_BASE}/alerts`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            renderAlerts(data.data);
            hideLoader('alertsContainer');
        }
    } catch (error) {
        console.error('Error loading alerts:', error);
        hideLoader('alertsContainer');
    }
}

function renderAlerts(alerts) {
    const container = document.getElementById('alertsContainer');
    
    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #64748b;">No active alerts. Great!</p>';
        return;
    }
    
    container.innerHTML = alerts.map(alert => `
        <div class="alert-item alert-${alert.priority.toLowerCase()}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: var(--primary);">${alert.type}</strong>
                    <p style="margin: 0.5rem 0;">${alert.message}</p>
                    <small style="color: #64748b;">
                        <i class="fas fa-map-marker-alt"></i> ${alert.location} | 
                        <i class="fas fa-calendar"></i> ${alert.crop}
                    </small>
                </div>
                <div style="text-align: right;">
                    <div style="color: var(--accent); font-weight: 600; margin-bottom: 0.5rem;">${alert.priority}</div>
                    <div style="font-size: 0.875rem;">${alert.action}</div>
                </div>
            </div>
        </div>
    `).join('');
    
    document.getElementById('alertsCard').classList.remove('hidden');
}

async function loadClimateAnalysis(location) {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        showLoader('climateContainer', 'Analyzing climate...');
        const response = await fetch(`${API_BASE}/climate-analysis?location=${encodeURIComponent(location)}&days=30`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            renderClimateAnalysis(data.data);
            hideLoader('climateContainer');
        }
    } catch (error) {
        console.error('Error loading climate analysis:', error);
        hideLoader('climateContainer');
    }
}

function renderClimateAnalysis(data) {
    const container = document.getElementById('climateContainer');
    
    if (data.error) {
        container.innerHTML = `<p style="text-align: center; color: #64748b;">${data.error}</p>`;
        return;
    }
    
    container.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
            <div class="info-item">
                <label>Average Temperature</label>
                <span>${data.average_temperature}C</span>
            </div>
            <div class="info-item">
                <label>Average Humidity</label>
                <span>${data.average_humidity}%</span>
            </div>
            <div class="info-item">
                <label>Total Rainfall</label>
                <span>${data.total_rainfall}mm</span>
            </div>
            <div class="info-item">
                <label>Rainy Days</label>
                <span>${data.rainy_days}</span>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
            <div class="info-item">
                <label>Temperature Trend</label>
                <span>${data.temperature_trend} (${data.temperature_change > 0 ? '+' : ''}${data.temperature_change}C)</span>
            </div>
            <div class="info-item">
                <label>Analysis Period</label>
                <span>${data.period_days} days</span>
            </div>
        </div>
        ${data.advisory ? `
            <div style="margin-top: 1rem; padding: 1rem; background: #fef3c7; border-radius: 8px; border-left: 4px solid #f59e0b;">
                <strong style="color: #92400e;"><i class="fas fa-exclamation-triangle"></i> Advisory:</strong>
                <p style="margin: 0.5rem 0 0 0; color: #92400e;">${data.advisory}</p>
            </div>
        ` : ''}
        ${data.rainfall_advisory ? `
            <div style="margin-top: 1rem; padding: 1rem; background: #dbeafe; border-radius: 8px; border-left: 4px solid #3b82f6;">
                <strong style="color: #1e40af;"><i class="fas fa-cloud-rain"></i> Rainfall Advisory:</strong>
                <p style="margin: 0.5rem 0 0 0; color: #1e40af;">${data.rainfall_advisory}</p>
            </div>
        ` : ''}
    `;
    
    document.getElementById('climateCard').classList.remove('hidden');
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('location').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            getRecommendations();
        }
    });

    bindCompanionChecker();
    resetCompanionChecker();
});
