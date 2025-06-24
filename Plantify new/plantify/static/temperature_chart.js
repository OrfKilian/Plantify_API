const API_BASE = '/api';

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
        }
    } catch (e) {
        console.error('Fehler beim Laden der Temperaturdaten', e);
    }
});
