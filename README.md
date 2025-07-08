# Plantify

This repository contains the Plantify project including a small Flask application and static frontend files. The dashboard integrates a temperature history chart for each room.

Graphs on the dashboard are loaded from the separate `plantify_api` service and
embedded with Plotly via `static/plots.js`.

Plant and room data are now fetched from this API on each request. Edited plant
details are stored temporarily via `/api/plant/<id>` so the "Schnellübersicht"
reflects the changes after a reload.

## Configuration

Set the `SECRET_KEY` environment variable before starting the Flask app to
enable secure sessions. During development you can set `FLASK_ENV=development`
to allow a default key to be used.

