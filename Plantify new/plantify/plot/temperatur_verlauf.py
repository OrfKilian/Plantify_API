from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

# Dummy-Daten für Temperaturverlauf (jetzt stündlich bis 19 Uhr)
data = [
    {"created": "2025-06-22 08:00:00", "temperature": 21.3},
    {"created": "2025-06-22 09:00:00", "temperature": 21.5},
    {"created": "2025-06-22 10:00:00", "temperature": 22.8},
    {"created": "2025-06-22 11:00:00", "temperature": 23.2},
    {"created": "2025-06-22 12:00:00", "temperature": 24.1},
    {"created": "2025-06-22 13:00:00", "temperature": 24.7},
    {"created": "2025-06-22 14:00:00", "temperature": 25.0},
    {"created": "2025-06-22 15:00:00", "temperature": 24.3},
    {"created": "2025-06-22 16:00:00", "temperature": 23.7},
    {"created": "2025-06-22 17:00:00", "temperature": 22.9},
    {"created": "2025-06-22 18:00:00", "temperature": 22.1},
    {"created": "2025-06-22 19:00:00", "temperature": 21.5}
]

# In DataFrame umwandeln
df = pd.DataFrame(data)
df['created'] = pd.to_datetime(df['created'])

# Diagramm mit besserer Optik
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df['created'],
    y=df['temperature'],
    mode='lines',
    fill='tozeroy',
    fillcolor='rgba(255, 0, 0, 0.15)',  # blasses Rot
    line=dict(color='red', width=4.5),
    hoverinfo='x+y',
    name='Temperatur'
))

fig.update_layout(
    title="Temperaturverlauf",
    title_x=0.5,
    xaxis=dict(
        title="Zeit",
        tickformat="%H:%M",  # Uhrzeit im Format 8:00
        dtick=3600000.0,  # Tick alle 1 Stunde
        showgrid=False,   # vertikale Gitterlinien entfernen
        tickmode="auto"
    ),
    yaxis=dict(
        title="Temperatur (°C)",
        ticksuffix=" °C",
        showgrid=True,
        gridcolor="lightgrey",
        range=[15, 26]
    ),
    plot_bgcolor="white",
    font=dict(family="Arial", size=14),
    margin=dict(l=40, r=20, t=60, b=40)
)

# HTML-Datei speichern
output_path = Path(__file__).resolve().parent.parent / "templates" / "diagramme" / "temperatur_verlauf.html"
fig.write_html(str(output_path))
