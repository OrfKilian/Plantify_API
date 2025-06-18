const API_BASE = '/api';
const ENDPOINTS = {
    today: `${API_BASE}/all-today`,
    sunlight: `${API_BASE}/sunlight-30days`
};

function createChart(ctx, label) {
    return new Chart(ctx, {
        type: 'line',
        data: { labels: [], datasets: [{ label, data: [], borderColor: 'rgb(75, 192, 192)', tension: 0.1 }] },
        options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    const potId = new URLSearchParams(window.location.search).get('pot_id') || '1';
    const charts = {
        sun: createChart(document.getElementById('chart-sun'), 'Sonnenstunden'),
        temp: createChart(document.getElementById('chart-temp'), 'Temperatur (°C)'),
        soil: createChart(document.getElementById('chart-soil'), 'Bodenfeuchtigkeit (%)'),
        air: createChart(document.getElementById('chart-air'), 'Luftfeuchtigkeit (%)')
    };

    try {
        const todayResp = await fetch(`${ENDPOINTS.today}?pot_id=${potId}`);
        const todayData = await todayResp.json();
        if (Array.isArray(todayData)) {
            todayData.forEach(d => {
                const t = d.created;
                charts.temp.data.labels.push(t);
                charts.soil.data.labels.push(t);
                charts.air.data.labels.push(t);
                charts.temp.data.datasets[0].data.push(d.temperature);
                charts.soil.data.datasets[0].data.push(d.ground_humidity);
                charts.air.data.datasets[0].data.push(d.air_humidity);
            });
            charts.temp.update();
            charts.soil.update();
            charts.air.update();
        }
    } catch (e) {
        console.error('Fehler beim Laden der Tagesdaten', e);
    }

    try {
        const sunResp = await fetch(`${ENDPOINTS.sunlight}?pot_id=${potId}`);
        const sunData = await sunResp.json();
        if (Array.isArray(sunData)) {
            sunData.forEach(d => {
                charts.sun.data.labels.push(d.created);
                charts.sun.data.datasets[0].data.push(d.HoS);
            });
            charts.sun.update();
        }
    } catch (e) {
        console.error('Fehler beim Laden der Sonnenstunden', e);
    }
});
