const API_BASE = '/api';
const ENDPOINTS = {
    today: `${API_BASE}/all-today`,
    sunlight: `${API_BASE}/sunlight-30days`,
    latest: `${API_BASE}/latest-value`
};

function createChart(ctx, label) {
    return new Chart(ctx, {
        type: 'line',
        data: { labels: [], datasets: [{ label, data: [], borderColor: 'rgb(75, 192, 192)', tension: 0.1 }] },
        options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });
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
        }
    }
});
