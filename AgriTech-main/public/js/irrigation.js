const cropDatabase = {
  rice: { label: 'Rice', stages: { germination: 7.8, vegetative: 8.6, flowering: 9.8, fruiting: 8.9, harvest: 5.4 } },
  wheat: { label: 'Wheat', stages: { germination: 4.0, vegetative: 5.0, flowering: 5.8, fruiting: 4.9, harvest: 3.2 } },
  maize: { label: 'Maize', stages: { germination: 4.2, vegetative: 5.6, flowering: 6.8, fruiting: 6.0, harvest: 3.8 } },
  cotton: { label: 'Cotton', stages: { germination: 3.4, vegetative: 4.5, flowering: 5.4, fruiting: 5.0, harvest: 3.0 } },
  tomato: { label: 'Tomato', stages: { germination: 3.2, vegetative: 4.4, flowering: 5.6, fruiting: 5.1, harvest: 3.0 } },
  potato: { label: 'Potato', stages: { germination: 4.1, vegetative: 5.3, flowering: 5.9, fruiting: 5.2, harvest: 3.4 } }
};

const soilFactors = { sandy: 1.15, loamy: 1.0, clay: 0.9, silt: 0.95 };
const irrigationEfficiency = { drip: 0.9, sprinkler: 0.75, flood: 0.6 };
const deliveryRates = { drip: 2800, sprinkler: 4200, flood: 6500 };
const forecastCache = new Map();
const state = {
  forecast: [],
  plan: [],
  alerts: [],
  sms: '',
  summary: null
};

const els = {};

function $(id) {
  return document.getElementById(id);
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function formatIndianNumber(value) {
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(Math.round(value));
}

function dayLabel(date) {
  return new Intl.DateTimeFormat('en-IN', { weekday: 'short', month: 'short', day: 'numeric' }).format(date);
}

function weatherIconFor(code, rainChance) {
  if (rainChance >= 65 || [61, 63, 65, 80, 81, 82].includes(code)) return 'fa-cloud-rain';
  if (code === 71 || code === 75 || code === 85) return 'fa-snowflake';
  if (code === 0) return 'fa-sun';
  if (code === 1 || code === 2) return 'fa-cloud-sun';
  if (code === 3) return 'fa-cloud';
  if (code === 95 || code === 96 || code === 99) return 'fa-bolt';
  return 'fa-cloud-sun';
}

function weatherLabelFor(code, rainChance) {
  if (rainChance >= 65 || [61, 63, 65, 80, 81, 82].includes(code)) return 'Rain likely';
  if (code === 0) return 'Clear and dry';
  if (code === 1 || code === 2) return 'Partly cloudy';
  if (code === 3) return 'Cloud cover';
  if (code === 95 || code === 96 || code === 99) return 'Storm risk';
  return 'Weather watch';
}

function createFallbackForecast(location) {
  const now = new Date();
  const template = [
    { max: 32, min: 22, rain: 12, precip: 0.5, code: 2 },
    { max: 36, min: 24, rain: 18, precip: 0.0, code: 0 },
    { max: 38, min: 25, rain: 8, precip: 0.0, code: 0 },
    { max: 31, min: 23, rain: 72, precip: 8.4, code: 61 },
    { max: 30, min: 22, rain: 45, precip: 2.1, code: 3 },
    { max: 34, min: 24, rain: 15, precip: 0.2, code: 1 },
    { max: 33, min: 23, rain: 10, precip: 0.0, code: 2 }
  ];

  return template.map((item, index) => {
    const date = new Date(now);
    date.setDate(now.getDate() + index);
    return {
      date,
      maxTemp: item.max,
      minTemp: item.min,
      rainChance: item.rain,
      precipitation: item.precip,
      code: item.code,
      source: `Offline estimate for ${location || 'your farm'}`
    };
  });
}

async function fetchForecast(location) {
  const normalized = (location || '').trim().toLowerCase();
  if (forecastCache.has(normalized)) {
    return forecastCache.get(normalized);
  }

  try {
    const geoUrl = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(location)}&count=1&language=en&format=json`;
    const geoResponse = await fetch(geoUrl);
    const geoData = await geoResponse.json();
    const match = geoData.results && geoData.results[0];

    if (!match) {
      throw new Error('No location match');
    }

    const weatherUrl = `https://api.open-meteo.com/v1/forecast?latitude=${match.latitude}&longitude=${match.longitude}&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,weather_code&timezone=auto&forecast_days=7`;
    const weatherResponse = await fetch(weatherUrl);
    const weatherData = await weatherResponse.json();
    const daily = weatherData.daily || {};

    const forecast = (daily.time || []).map((dateString, index) => ({
      date: new Date(`${dateString}T00:00:00`),
      maxTemp: Number(daily.temperature_2m_max?.[index] ?? 0),
      minTemp: Number(daily.temperature_2m_min?.[index] ?? 0),
      rainChance: Number(daily.precipitation_probability_max?.[index] ?? 0),
      precipitation: Number(daily.precipitation_sum?.[index] ?? 0),
      code: Number(daily.weather_code?.[index] ?? 1),
      source: `${match.name}${match.admin1 ? `, ${match.admin1}` : ''}`
    }));

    forecastCache.set(normalized, forecast);
    return forecast;
  } catch (error) {
    const fallback = createFallbackForecast(location);
    forecastCache.set(normalized, fallback);
    return fallback;
  }
}

function getBaseNeedMm(crop, stage) {
  const cropEntry = cropDatabase[crop] || cropDatabase.rice;
  return cropEntry.stages[stage] ?? cropEntry.stages.vegetative;
}

function getMoistureFactor(moisture) {
  if (moisture <= 20) return 1.35;
  if (moisture <= 35) return 1.18;
  if (moisture <= 55) return 1.0;
  if (moisture <= 70) return 0.82;
  return 0.65;
}

function getWeatherFactor(day) {
  if (day.rainChance >= 65 || day.precipitation >= 2.5) return 0;
  let factor = 1;
  if (day.rainChance >= 35 || day.precipitation >= 0.8) {
    factor -= 0.35;
  }
  if (day.maxTemp >= 35) {
    factor += 0.2;
  }
  if (day.maxTemp >= 40) {
    factor += 0.15;
  }
  if (day.maxTemp <= 20) {
    factor -= 0.1;
  }
  return clamp(factor, 0, 1.7);
}

function buildPlan(inputs, forecast) {
  const cropEntry = cropDatabase[inputs.crop] || cropDatabase.rice;
  const baseNeedMm = getBaseNeedMm(inputs.crop, inputs.stage);
  const soilFactor = soilFactors[inputs.soil] ?? 1;
  const moistureFactor = getMoistureFactor(inputs.moisture);
  const efficiency = irrigationEfficiency[inputs.method] ?? 0.75;
  const deliveryRate = deliveryRates[inputs.method] ?? deliveryRates.sprinkler;
  const area = Number(inputs.area) || 1;
  const baselinePerDay = baseNeedMm * soilFactor * moistureFactor * area * 10000 / irrigationEfficiency.flood;
  const baselineWeekly = baselinePerDay * 7;

  const plan = forecast.map((day, index) => {
    const weatherFactor = getWeatherFactor(day);
    const heatBoost = day.maxTemp >= 35 ? 1.15 : 1;
    let netMm = baseNeedMm * soilFactor * moistureFactor * weatherFactor * heatBoost;
    const rainBuffer = day.precipitation * 0.8;
    netMm = Math.max(netMm - rainBuffer, 0);

    const shouldSkip = day.rainChance >= 65 || day.precipitation >= 2.5;
    const liters = shouldSkip ? 0 : (netMm / efficiency) * area * 10000;
    const hours = liters > 0 ? liters / (deliveryRate * area) : 0;
    const action = shouldSkip ? 'Skip irrigation' : liters <= 500 ? 'Light irrigation' : 'Water as planned';
    const timing = shouldSkip ? 'Hold off' : inputs.method === 'flood' ? '06:00 AM' : '05:30 AM';

    const alerts = [];
    if (shouldSkip) {
      alerts.push('Skip irrigation tomorrow — rain expected.');
    } else if (day.maxTemp >= 35) {
      alerts.push('Increase watering — heatwave coming.');
    }
    if (inputs.moisture < 25 && !shouldSkip) {
      alerts.push('Soil is dry; add one extra check before watering.');
    }
    if (inputs.soil === 'sandy' && inputs.method === 'flood') {
      alerts.push('Consider drip or sprinkler: sandy soils lose water faster.');
    }
    if (inputs.method === 'drip' && day.precipitation > 0) {
      alerts.push('Drip irrigation is ideal today because you can fine-tune the dose.');
    }

    return {
      dayIndex: index,
      date: day.date,
      label: dayLabel(day.date),
      liters,
      hours,
      action,
      timing,
      shouldSkip,
      alerts,
      weather: day,
      summary: `${day.maxTemp}°C high, ${day.rainChance}% rain chance`
    };
  });

  const weeklyWater = plan.reduce((total, entry) => total + entry.liters, 0);
  const savings = Math.max(baselineWeekly - weeklyWater, 0);
  const savingsPct = baselineWeekly > 0 ? Math.round((savings / baselineWeekly) * 100) : 0;
  const cycleCount = plan.filter((entry) => entry.liters > 0).length;
  const nextAction = plan.find((entry) => entry.liters > 0) || plan[0];
  const topAlert = plan.flatMap((entry) => entry.alerts).find(Boolean) || 'No urgent irrigation alerts.';

  const summaryText = `${cropEntry.label} at ${area.toFixed(1)} ha in ${inputs.location} needs about ${formatIndianNumber(weeklyWater)} liters this week. ${topAlert}`;
  const sms = `AgriTech Water Advisory: ${topAlert} Next irrigation: ${nextAction ? nextAction.label + ' at ' + nextAction.timing : 'none'}. Weekly water use: ${formatIndianNumber(weeklyWater)} L.`;

  return {
    plan,
    weeklyWater,
    baselineWeekly,
    savings,
    savingsPct,
    cycleCount,
    nextAction,
    summaryText,
    sms,
    topAlert,
    cropLabel: cropEntry.label,
    weatherRisk: forecast.some((day) => day.rainChance >= 65) ? 'Moderate' : (forecast.some((day) => day.maxTemp >= 35) ? 'High' : 'Low')
  };
}

function renderWeather(day) {
  if (!day) return;
  els.currentTemp.textContent = `${Math.round(day.maxTemp)}°C`;
  els.weatherStatus.textContent = weatherLabelFor(day.code, day.rainChance);
  els.weatherIcon.className = `fas ${weatherIconFor(day.code, day.rainChance)}`;
  els.rainChance.textContent = `${Math.round(day.rainChance)}%`;
  els.rainTotal.textContent = `${day.precipitation.toFixed(1)} mm`;
  els.tempMax.textContent = `${Math.round(day.maxTemp)}°C`;
  els.humidityHint.textContent = day.maxTemp >= 35 ? 'Heat stress risk' : day.precipitation > 0 ? 'Rain buffer active' : 'Stable';
  els.connectionStatus.textContent = day.source && day.source.startsWith('Offline') ? 'Offline fallback ready' : `Live weather • ${day.source}`;
}

function renderPlan(results) {
  state.plan = results.plan;
  state.summary = results;
  state.sms = results.sms;
  state.alerts = results.plan.flatMap((entry, index) => {
    const list = [];
    if (entry.shouldSkip) {
      list.push({ severity: 'warning', title: `${entry.label}: rain expected`, text: 'Skip irrigation to avoid runoff and save water.' });
    }
    if (entry.weather.maxTemp >= 35) {
      list.push({ severity: 'danger', title: `${entry.label}: heatwave coming`, text: 'Increase watering or move irrigation earlier in the morning.' });
    }
    if (!entry.shouldSkip && entry.liters > 0) {
      list.push({ severity: 'success', title: `${entry.label}: watering scheduled`, text: `${entry.action} at ${entry.timing}. Estimated dose: ${formatIndianNumber(entry.liters)} liters.` });
    }
    if (index === 0 && results.topAlert) {
      list.unshift({ severity: 'info', title: 'Top advisory', text: results.topAlert });
    }
    return list;
  });

  els.resultsPanel.classList.remove('hidden');
  els.summaryCopy.textContent = results.summaryText;
  els.waterSaved.textContent = `${formatIndianNumber(results.savings)} L`;
  els.waterSavedNote.textContent = `${results.savingsPct}% less than flood baseline`;
  els.nextAction.textContent = results.nextAction ? results.nextAction.action : 'No action';
  els.nextActionNote.textContent = results.nextAction ? `${results.nextAction.label} • ${results.nextAction.timing}` : 'No active watering required';
  els.weatherRisk.textContent = results.weatherRisk;
  els.weatherRiskNote.textContent = results.topAlert;
  els.weeklyWater.textContent = `${formatIndianNumber(results.weeklyWater)} L`;
  els.cycleCount.textContent = `${results.cycleCount}`;
  els.savingsPercent.textContent = `${results.savingsPct}%`;
  els.alertsEnabled.textContent = els.offlineAlerts.checked ? 'On' : 'Off';
  els.baselineLabel.textContent = `${formatIndianNumber(results.baselineWeekly)} L`;
  els.advisorLabel.textContent = `${formatIndianNumber(results.weeklyWater)} L`;
  els.baselineBar.style.width = '100%';
  const advisorWidth = results.baselineWeekly > 0 ? Math.max(10, Math.min(100, (results.weeklyWater / results.baselineWeekly) * 100)) : 0;
  els.advisorBar.style.width = `${advisorWidth}%`;
  els.trackerNote.textContent = `${results.cropLabel} water use is reduced by ${results.savingsPct}% compared with a flood baseline while keeping the crop stage and weather outlook in view.`;
  els.smsPreview.textContent = results.sms;
  renderAlerts(results);
  renderSchedule(results.plan);
}

function renderAlerts(results) {
  const alerts = results.plan.flatMap((entry, index) => {
    const output = [];
    if (index === 0) {
      output.push({ severity: 'info', title: 'AI summary', text: results.summaryText });
    }
    if (entry.shouldSkip) {
      output.push({ severity: 'warning', title: `${entry.label}: rain expected`, text: `Skip irrigation. ${entry.summary}.` });
    } else if (entry.weather.maxTemp >= 35) {
      output.push({ severity: 'danger', title: `${entry.label}: heat alert`, text: `Increase watering. ${entry.summary}.` });
    } else {
      output.push({ severity: 'success', title: `${entry.label}: scheduled`, text: `${entry.action} at ${entry.timing} with ${formatIndianNumber(entry.liters)} liters.` });
    }
    entry.alerts.forEach((alert) => {
      output.push({ severity: alert.includes('Skip') ? 'warning' : 'info', title: entry.label, text: alert });
    });
    return output;
  }).slice(0, 8);

  els.alertList.innerHTML = alerts.map((alert) => `
    <article class="alert-item ${alert.severity}">
      <strong>${alert.title}</strong>
      <span>${alert.text}</span>
    </article>
  `).join('');
}

function renderSchedule(plan) {
  els.scheduleGrid.innerHTML = plan.map((entry) => {
    const pillClass = entry.shouldSkip ? 'rain' : entry.weather.maxTemp >= 35 ? 'heat' : '';
    return `
      <article class="plan-day ${entry.shouldSkip ? 'skip' : 'water'}">
        <div class="day-top">
          <strong>${entry.label}</strong>
          <span class="day-pill ${pillClass}">${entry.shouldSkip ? 'Skip' : entry.weather.maxTemp >= 35 ? 'Heat' : 'Water'}</span>
        </div>
        <small>${entry.summary}</small>
        <strong>${entry.shouldSkip ? '0 L' : `${formatIndianNumber(entry.liters)} L`}</strong>
        <span>${entry.action}</span>
        <small>${entry.timing}</small>
        <small>${entry.hours > 0 ? `${entry.hours.toFixed(1)} hrs estimated` : 'No irrigation needed'}</small>
      </article>
    `;
  }).join('');
}

async function generateAdvisor(loadWeather = true) {
  const inputs = {
    crop: els.cropType.value,
    stage: els.growthStage.value,
    area: Number(els.farmSize.value),
    method: els.irrigationMethod.value,
    soil: els.soilType.value,
    moisture: Number(els.soilMoisture.value),
    location: els.location.value.trim() || 'Indore'
  };

  const forecast = loadWeather ? await fetchForecast(inputs.location) : (state.forecast.length ? state.forecast : createFallbackForecast(inputs.location));
  state.forecast = forecast;
  renderWeather(forecast[0]);
  const results = buildPlan(inputs, forecast);
  renderPlan(results);
  els.connectionStatus.textContent = forecast[0].source && forecast[0].source.startsWith('Offline') ? 'Offline fallback ready' : `Live weather • ${forecast[0].source}`;
}

function updateMoistureLabel() {
  els.moistureVal.textContent = `${els.soilMoisture.value}%`;
}

async function copySms() {
  const text = state.sms || els.smsPreview.textContent || '';
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
    els.copySms.textContent = 'Copied';
    setTimeout(() => {
      els.copySms.innerHTML = '<i class="fas fa-sms"></i> Copy SMS';
    }, 1200);
  } catch (error) {
    window.prompt('Copy SMS advisory:', text);
  }
}

function downloadReport() {
  const anchor = $('report-anchor');
  if (!anchor || typeof html2pdf === 'undefined') return;
  html2pdf().set({
    margin: 0.35,
    filename: 'Water_Management_Advisor.pdf',
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2, useCORS: true },
    jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
  }).from(anchor).save();
}

function bindEvents() {
  els.advisorForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    await generateAdvisor(true);
  });

  els.generateBtn.addEventListener('click', async () => {
    await generateAdvisor(true);
  });

  els.useWeatherBtn.addEventListener('click', async () => {
    await generateAdvisor(true);
  });

  els.soilMoisture.addEventListener('input', updateMoistureLabel);
  els.copySms.addEventListener('click', copySms);
  els.downloadReport.addEventListener('click', downloadReport);

  window.addEventListener('online', () => {
    if (els.connectionStatus) {
      els.connectionStatus.textContent = 'Live weather available';
    }
  });

  window.addEventListener('offline', () => {
    if (els.connectionStatus) {
      els.connectionStatus.textContent = 'Offline fallback ready';
    }
  });
}

function cacheElements() {
  els.advisorForm = $('advisor-form');
  els.generateBtn = $('generate-plan-btn');
  els.useWeatherBtn = $('use-weather-btn');
  els.downloadReport = $('download-report');
  els.copySms = $('copy-sms');
  els.resultsPanel = $('results-panel');
  els.scheduleGrid = $('schedule-grid');
  els.alertList = $('alert-list');
  els.smsPreview = $('sms-preview');
  els.summaryCopy = $('summary-copy');
  els.waterSaved = $('water-saved');
  els.waterSavedNote = $('water-saved-note');
  els.nextAction = $('next-action');
  els.nextActionNote = $('next-action-note');
  els.weatherRisk = $('weather-risk');
  els.weatherRiskNote = $('weather-risk-note');
  els.weeklyWater = $('weekly-water');
  els.cycleCount = $('cycle-count');
  els.savingsPercent = $('savings-percent');
  els.alertsEnabled = $('alerts-enabled');
  els.baselineLabel = $('baseline-label');
  els.advisorLabel = $('advisor-label');
  els.baselineBar = $('baseline-bar');
  els.advisorBar = $('advisor-bar');
  els.trackerNote = $('tracker-note');
  els.currentTemp = $('current-temp');
  els.weatherStatus = $('weather-status');
  els.weatherIcon = $('weather-icon');
  els.rainChance = $('rain-chance');
  els.rainTotal = $('rain-total');
  els.tempMax = $('temp-max');
  els.humidityHint = $('humidity-hint');
  els.connectionStatus = $('connection-status');
  els.cropType = $('crop-type');
  els.growthStage = $('growth-stage');
  els.farmSize = $('farm-size');
  els.irrigationMethod = $('irrigation-method');
  els.soilType = $('soil-type');
  els.soilMoisture = $('soil-moisture');
  els.moistureVal = $('moisture-val');
  els.location = $('location');
  els.offlineAlerts = $('offline-alerts');
}

document.addEventListener('DOMContentLoaded', async () => {
  cacheElements();
  bindEvents();
  updateMoistureLabel();
  els.alertsEnabled.textContent = els.offlineAlerts.checked ? 'On' : 'Off';
  await generateAdvisor(true);
});
