const API_BASE = '/api';
const ENDPOINTS = {
    today: `${API_BASE}/all-today`,
    sunlight: `${API_BASE}/sunlight-30days`,
    latest: `${API_BASE}/latest-value`
};

// Fallback-Daten wenn die API nicht erreichbar ist
const DUMMY_MEASUREMENTS = [
    { created: '2025-06-22 08:00:00', temperature: 21.3, air_humidity: 40.0, ground_humidity: 35.5, HoS: 6.0 },
    { created: '2025-06-22 09:00:00', temperature: 21.5, air_humidity: 40.5, ground_humidity: 35.8, HoS: 6.0 },
    { created: '2025-06-22 10:00:00', temperature: 22.8, air_humidity: 41.0, ground_humidity: 36.1, HoS: 6.0 },
    { created: '2025-06-22 11:00:00', temperature: 23.2, air_humidity: 41.5, ground_humidity: 36.4, HoS: 6.0 },
    { created: '2025-06-22 12:00:00', temperature: 24.1, air_humidity: 42.0, ground_humidity: 36.7, HoS: 6.0 },
    { created: '2025-06-22 13:00:00', temperature: 24.7, air_humidity: 42.5, ground_humidity: 37.0, HoS: 6.0 },
    { created: '2025-06-22 14:00:00', temperature: 25.0, air_humidity: 43.0, ground_humidity: 37.3, HoS: 6.0 },
    { created: '2025-06-22 15:00:00', temperature: 24.3, air_humidity: 43.5, ground_humidity: 37.6, HoS: 6.0 },
    { created: '2025-06-22 16:00:00', temperature: 23.7, air_humidity: 44.0, ground_humidity: 37.9, HoS: 6.0 },
    { created: '2025-06-22 17:00:00', temperature: 22.9, air_humidity: 44.5, ground_humidity: 38.2, HoS: 6.0 },
    { created: '2025-06-22 18:00:00', temperature: 22.1, air_humidity: 45.0, ground_humidity: 38.5, HoS: 6.0 },
    { created: '2025-06-22 19:00:00', temperature: 21.5, air_humidity: 45.5, ground_humidity: 38.8, HoS: 6.0 }
];

function createChart(ctx, label) {
    return new Chart(ctx, {
        type: 'line',
        data: { labels: [], datasets: [{ label, data: [], borderColor: 'rgb(75, 192, 192)', tension: 0.1 }] },
        options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });
}

function applyMeasurements(measurements, charts) {
    measurements.forEach(d => {
        const t = d.created;
        if (charts.temp) {
            charts.temp.data.labels.push(t);
            charts.temp.data.datasets[0].data.push(d.temperature);
        }
        charts.soil.data.labels.push(t);
        charts.air.data.labels.push(t);
        charts.soil.data.datasets[0].data.push(d.ground_humidity);
        charts.air.data.datasets[0].data.push(d.air_humidity);
    });
    if (charts.temp) charts.temp.update();
    charts.soil.update();
    charts.air.update();
}

document.addEventListener('DOMContentLoaded', async () => {
    const params = new URLSearchParams(window.location.search);
    let potId = params.get('pot_id');
    if (!potId) {
        const firstRow = document.querySelector('#care-guidelines tbody tr');
        potId = firstRow ? firstRow.dataset.potId : '1';
    }
    const charts = {
        sun: createChart(document.getElementById('chart-sun'), 'Sonnenstunden'),
        temp: null,
        soil: createChart(document.getElementById('chart-soil'), 'Bodenfeuchtigkeit (%)'),
        air: createChart(document.getElementById('chart-air'), 'Luftfeuchtigkeit (%)')
    };
    const tempCtx = document.getElementById('chart-temp');
    if (tempCtx) {
        charts.temp = createChart(tempCtx, 'Temperatur (°C)');
    }

    try {
        const todayResp = await fetch(`${ENDPOINTS.today}?pot_id=${potId}`);
        const todayData = await todayResp.json();
        if (Array.isArray(todayData)) {
            applyMeasurements(todayData, charts);
        }
    } catch (e) {
        console.error('Fehler beim Laden der Tagesdaten', e);
        applyMeasurements(DUMMY_MEASUREMENTS, charts);
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
        DUMMY_MEASUREMENTS.forEach(d => {
            charts.sun.data.labels.push(d.created);
            charts.sun.data.datasets[0].data.push(d.HoS);
        });
        charts.sun.update();
    }

    // Ist-Werte für Pflegehinweise laden
    const rows = document.querySelectorAll('#care-guidelines tbody tr');
    for (const row of rows) {
        const id = row.dataset.potId;
        if (!id) continue;
        try {
            const resp = await fetch(`${ENDPOINTS.latest}?pot_id=${id}`);
            const data = await resp.json();
            row.querySelector('.val-temp').textContent = data.temperature.toFixed(1);
            row.querySelector('.val-air').textContent = data.air_humidity.toFixed(1);
            row.querySelector('.val-soil').textContent = data.ground_humidity.toFixed(1);
        } catch (e) {
            console.error('Fehler beim Laden der Ist-Werte', e);
            const d = DUMMY_MEASUREMENTS[DUMMY_MEASUREMENTS.length - 1];
            row.querySelector('.val-temp').textContent = d.temperature.toFixed(1);
            row.querySelector('.val-air').textContent = d.air_humidity.toFixed(1);
            row.querySelector('.val-soil').textContent = d.ground_humidity.toFixed(1);
        }
    }
});
