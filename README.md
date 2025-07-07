# Plantify

This repository contains the Plantify project including a small Flask application and static frontend files. The dashboard integrates a temperature history chart for each room.

Graphs on the dashboard are loaded from the API and embedded with Plotly via
`static/plots.js`.

Plant details can be edited on the plant page. Changes are sent to the new
`/api/plant/<id>` endpoint which updates the in-memory `PLANTS` list so that the
"Schnellübersicht" reflects the saved target values after a reload.

## Configuration

Set the `SECRET_KEY` environment variable before starting the Flask app to
enable secure sessions. During development you can set `FLASK_ENV=development`
to allow a default key to be used.

