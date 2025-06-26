# Plantify

This repository contains the Plantify project including a small Flask application and static frontend files. The dashboard integrates a temperature history chart for each room.

The chart is rendered in `templates/dashboard.html` using Chart.js and dummy measurement data in `static/dashboard.js`. A local copy of Chart.js is bundled under `static/chart.min.js` so the page works without Internet access.

