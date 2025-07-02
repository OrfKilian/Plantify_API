# Plantify

This repository contains the Plantify project including a small Flask application and static frontend files. The dashboard integrates a temperature history chart for each room.

The chart is rendered in `templates/dashboard.html` using Chart.js and dummy measurement data in `static/dashboard.js`. Chart.js is loaded from a CDN.

Plant details can be edited on the plant page. Changes are sent to the new
`/api/plant/<id>` endpoint which updates the in-memory `PLANTS` list so that the
"Schnellübersicht" reflects the saved target values after a reload.

