const API_BASE = '/api';
const DUMMY_MEASUREMENTS = [
    { created: '2025-06-22 08:00:00', temperature: 21.3 },
    { created: '2025-06-22 09:00:00', temperature: 21.5 },
    { created: '2025-06-22 10:00:00', temperature: 22.8 },
    { created: '2025-06-22 11:00:00', temperature: 23.2 },
    { created: '2025-06-22 12:00:00', temperature: 24.1 },
    { created: '2025-06-22 13:00:00', temperature: 24.7 },
    { created: '2025-06-22 14:00:00', temperature: 25.0 },
    { created: '2025-06-22 15:00:00', temperature: 24.3 },
    { created: '2025-06-22 16:00:00', temperature: 23.7 },
    { created: '2025-06-22 17:00:00', temperature: 22.9 },
    { created: '2025-06-22 18:00:00', temperature: 22.1 },
    { created: '2025-06-22 19:00:00', temperature: 21.5 }
];

document.addEventListener('DOMContentLoaded', async () => {
    const potId = new URLSearchParams(window.location.search).get('pot_id') || '1';
    const ctx = document.getElementById('chart-temp');
    if (!ctx) return;

    const chart = new Chart(ctx, {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'Temperatur (°C)', data: [], borderColor: 'rgb(75, 192, 192)', tension: 0.1 }] },
        options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });

    try {
        const resp = await fetch(`${API_BASE}/all-today?pot_id=${potId}`);
        const data = await resp.json();
        if (Array.isArray(data)) {
            data.forEach(d => {
                chart.data.labels.push(d.created);
                chart.data.datasets[0].data.push(d.temperature);
            });
            chart.update();
            return;
        }
    } catch (e) {
        console.error('Fehler beim Laden der Temperaturdaten', e);
    }

    // Fallback
    DUMMY_MEASUREMENTS.forEach(d => {
        chart.data.labels.push(d.created);
        chart.data.datasets[0].data.push(d.temperature);
    });
    chart.update();
});
