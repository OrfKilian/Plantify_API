// Befüllt die Iframes mit den von der API gerenderten Plotly-Grafen
document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    let potId = params.get('pot_id');
    if (!potId) {
        const firstRow = document.querySelector('#care-guidelines tbody tr');
        potId = firstRow ? firstRow.dataset.potId : '1';
    }

    const baseUrl = 'http://localhost:5001/plots';
    const frames = {
        sun: document.getElementById('frame-sun'),
        temp: document.getElementById('frame-temp'),
        soil: document.getElementById('frame-soil'),
        air: document.getElementById('frame-air')
    };

    if (frames.sun) frames.sun.src = `${baseUrl}/sunlight?pot_id=${potId}`;
    if (frames.temp) frames.temp.src = `${baseUrl}/temperature?pot_id=${potId}`;
    if (frames.soil) frames.soil.src = `${baseUrl}/soil?pot_id=${potId}`;
    if (frames.air) frames.air.src = `${baseUrl}/luftfeuchtigkeit?pot_id=${potId}`;
});
