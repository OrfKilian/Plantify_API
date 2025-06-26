
// Chart configurations
const chartConfigs = {
    data: {
        type: 'line',
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    }
};

// Initialize charts
const charts = {};
function initializeCharts() {
    const chartElements = {
        data: document.getElementById('chart-data')
    };

    for (const [key, element] of Object.entries(chartElements)) {
        if (element) {
            charts[key] = new Chart(element, {
                ...chartConfigs[key],
                data: {
                    labels: [],
                    datasets: [{
                        label: key.charAt(0).toUpperCase() + key.slice(1),
                        data: [],
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                }
            });
        }
    }
}


// Generate a new random data point based on the previous value and type
function getRandomValue(prev, type) {
    let min, max, delta;
    switch (type) {
        case 'temperature':
            min = 18; max = 28; delta = 0.5; break; // °C
        case 'ground_humidity':
            min = 20; max = 60; delta = 2; break; // %
        case 'air_humidity':
            min = 30; max = 60; delta = 2; break; // %
        default:
            min = 0; max = 100; delta = 1;
    }
    let next = prev + (Math.random() * 2 - 1) * delta;
    return Math.max(min, Math.min(max, next));
}

// Store the last values for each metric
let lastData = {
    temperature: 22.5,
    ground_humidity: 35.5,
    air_humidity: 40.0
};

// Track the current time for data points, starting at 12:00 am
let baseDate = new Date();
baseDate.setHours(0, 0, 0, 0); // Set to 12:00 am today
let dataPointIndex = 0;

function getNextTimestamp() {
    // Each data point is 30 minutes apart
    let next = new Date(baseDate.getTime() + dataPointIndex * 30 * 60 * 1000);
    dataPointIndex++;
    // Format as HH:mm (e.g., 00:00, 00:30, 01:00, ...)
    return next.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Update charts with new random data, excluding sun chart
function updateChartsRandom() {
    const label = getNextTimestamp();
    // Generate new values
    lastData.temperature = getRandomValue(lastData.temperature, 'temperature');
    lastData.ground_humidity = getRandomValue(lastData.ground_humidity, 'ground_humidity');
    lastData.air_humidity = getRandomValue(lastData.air_humidity, 'air_humidity');
    // Datenwerte: average of the three metrics
    const avgData = ((lastData.temperature - 18) / 10 + lastData.ground_humidity / 100 + lastData.air_humidity / 100) / 3 * 100;

    // Update data chart (average metric)
    if (charts.data) {
        charts.data.data.labels.push(label);
        charts.data.data.datasets[0].data.push(avgData);
        if (charts.data.data.labels.length > 10) {
            charts.data.data.labels.shift();
            charts.data.data.datasets[0].data.shift();
        }
        charts.data.update();
    }
}

// Main initialization
document.addEventListener('DOMContentLoaded', async function() {
    initializeCharts();
    
    // Get pot_id from URL or use default
    const urlParams = new URLSearchParams(window.location.search);
    const potId = urlParams.get('pot_id') || '1'; // Default to pot 1 if not specified

    // Initialize with one data point
    updateChartsRandom();

    // Set up periodic updates every 10 seconds
    setInterval(() => {
        updateChartsRandom();
    }, 10000);
}); 