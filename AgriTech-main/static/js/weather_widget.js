// Simple weather widget client
// Fetches /api/weather?lat=&lon= and renders minimal UI into #weather-widget

async function loadWeather(lat, lon) {
  try {
    const res = await fetch(`/api/weather?lat=${lat}&lon=${lon}`);
    if (!res.ok) throw new Error('Weather fetch failed');
    const data = await res.json();
    const el = document.getElementById('weather-widget');
    if (!el) return;
    el.innerHTML = `<div><strong>${data.city || 'Weather'}</strong><div>Temp: ${data.current?.temp || 'N/A'}</div></div>`;
  } catch (e) {
    console.error('Weather widget error', e);
  }
}

// Example usage: loadWeather(12.97, 77.59);
