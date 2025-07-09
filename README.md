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

## Running

Install the dependencies and start the Flask development server:

```bash
pip install -r "Plantify new/plantify/requirements.txt"

# optional: provide your own secret key for production use
export SECRET_KEY=$(python3 -c 'import os,base64;print(base64.b64encode(os.urandom(32)).decode())')

python "Plantify new/plantify/app.py"
```

If `SECRET_KEY` is not set, the application falls back to the insecure value
`dev-secret` and prints a warning. This is intended only for local development.

