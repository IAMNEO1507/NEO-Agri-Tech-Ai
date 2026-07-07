// Simple farm progress widget: fetches activity summary and renders a timeline

async function loadFarmProgress(userId) {
  try {
    const res = await fetch(`/api/activities/summary?user_id=${userId}`);
    if (!res.ok) throw new Error('Activities summary fetch failed');
    const data = await res.json();
    const el = document.getElementById('farm-progress-widget');
    if (!el) return;
    el.innerHTML = `<div><strong>Recent activities</strong><ul>${data.activities.slice(0,5).map(a=>`<li>${a.activity_type} - ${a.activity_date}</li>`).join('')}</ul></div>`;
  } catch (e) {
    console.error('Farm progress widget error', e);
  }
}

// Example usage: loadFarmProgress(123);
