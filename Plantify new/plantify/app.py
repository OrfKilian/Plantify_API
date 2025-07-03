from flask import Flask, render_template, request, redirect, session, url_for, jsonify, Response
from functools import wraps
import os
import bcrypt
import requests
from email_validator import validate_email, EmailNotValidError


app = Flask(__name__)
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    if os.environ.get('FLASK_ENV') == 'development':
        secret_key = 'dev-secret'
    else:
        raise RuntimeError('SECRET_KEY environment variable not set')
app.secret_key = secret_key

# Base URL for the external Smartplant API used for graph rendering
API_BASE = os.environ.get('SMARTPLANT_API_BASE', 'http://localhost:5001')

# Simple credential storage for demonstration purposes
# Mapping of email to hashed password
USERS = {
    'test@example.com': bcrypt.hashpw(b'test123', bcrypt.gensalt()).decode('utf-8')
}
# Dummy-Daten für Dashboard und Pflanzen
ROOMS = [
    {"name": "Wohnzimmer"},
    {"name": "Badezimmer"},
    {"name": "Balkon"}
]

PLANTS = [
    {
        "id": 1,
        "name": "Tomate",
        "facts": "",
        "room": None,
        "target_temperature": 22,
        "target_air_humidity": 50,
        "target_ground_humidity": 40,
    },
    {
        "id": 2,
        "name": "Orchidee",
        "facts": "",
        "room": None,
        "target_temperature": 22,
        "target_air_humidity": 50,
        "target_ground_humidity": 40,
    },
    {
        "id": 3,
        "name": "Monstera",
        "facts": "",
        "room": None,
        "target_temperature": 22,
        "target_air_humidity": 50,
        "target_ground_humidity": 40,
    },
    {
        "id": 4,
        "name": "Strelitzie",
        "facts": "",
        "room": None,
        "target_temperature": 22,
        "target_air_humidity": 50,
        "target_ground_humidity": 40,
    },
    {
        "id": 5,
        "name": "Orchidee 2",
        "facts": "",
        "room": None,
        "target_temperature": 22,
        "target_air_humidity": 50,
        "target_ground_humidity": 40,
    },
]

@app.context_processor
def inject_sidebar_data():
    return dict(rooms=ROOMS, plants=PLANTS)

def slugify(value: str) -> str:
    return value.lower().replace(" ", "-")

def is_valid_email(email: str) -> bool:
    """Validate an email address using the email-validator package."""
    if not email:
        return False
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

# --- Login-Decorator für geschützte Seiten ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed = USERS.get(email)
        if hashed and bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')):
            session['user_id'] = email
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        return render_template('login.html', error='Falsche Login-Daten!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')  # Nach dem Logout zur Login-Seite weiterleiten


@app.route('/dashboard/<slug>')
@login_required
def dashboard(slug):
    room = next((r for r in ROOMS if slugify(r['name']) == slug), None)
    if not room:
        return "Zimmer nicht gefunden", 404
    room_plants = [p for p in PLANTS if p.get('room') == room['name']]
    return render_template('dashboard.html', room=room['name'], room_slug=slug,
                           room_plants=room_plants)

# Seite zum Umbenennen der Zimmer
@app.route('/rooms')
@login_required
def rooms_page():
    room_entries = [{'name': r['name'], 'slug': slugify(r['name'])} for r in ROOMS]
    return render_template('rooms.html', rooms=room_entries)

# Plantendetail und Bearbeitung
@app.route('/pflanze/<slug>')
@login_required
def plant_detail(slug):
    # Slugs are generated as '<name>-<id>' to allow duplicate plant names.
    plant = None
    plant_id_part = slug.rsplit('-', 1)[-1]
    if plant_id_part.isdigit():
        plant = next((p for p in PLANTS if str(p['id']) == plant_id_part), None)
    if not plant:  # Fallback for old slugs without id
        plant = next((p for p in PLANTS if slugify(p['name']) == slug), None)
    if not plant:
        return "Pflanze nicht gefunden", 404
    return render_template('plant.html', plant=plant, rooms=ROOMS,
                           trivial=plant['name'], botanisch=plant['name'])

@app.route('/api/plant/<int:plant_id>', methods=['POST'])
@login_required
def update_plant_api(plant_id: int):
    """Update plant data in the in-memory list."""
    data = request.get_json(silent=True) or {}
    plant = next((p for p in PLANTS if p['id'] == plant_id), None)
    if not plant:
        return jsonify({'error': 'Plant not found'}), 404
    allowed = {
        'facts',
        'name',
        'room',
        'target_temperature',
        'target_air_humidity',
        'target_ground_humidity',
    }
    for key in allowed:
        if key in data:
            plant[key] = data[key]
    return jsonify({'success': True})


# Proxy endpoint to retrieve plotly graphs from the external API
@app.route('/plots/<plot_name>')
@login_required
def proxy_plot(plot_name: str):
    pot_id = request.args.get('pot_id', 1)
    try:
        resp = requests.get(f"{API_BASE}/plots/{plot_name}", params={'pot_id': pot_id}, timeout=5)
        resp.raise_for_status()
    except requests.RequestException:
        return "Fehler beim Laden des Diagramms", 502
    return Response(resp.content, content_type=resp.headers.get('Content-Type', 'text/html'))

# Einstellungen
@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html',
                           msg_pw=request.args.get('msg_pw'),
                           msg_email=request.args.get('msg_email'))


@app.route('/settings/change-email', methods=['POST'])
@login_required
def change_email():
    new_email = request.form.get('new_email')
    current_email = session.get('user_id')
    if new_email and is_valid_email(new_email) and current_email in USERS:
        USERS[new_email] = USERS.pop(current_email)
        session['user_id'] = new_email
        return redirect(url_for('settings', msg_email='success'))
    return redirect(url_for('settings', msg_email='error'))


@app.route('/settings/change-password', methods=['POST'])
@login_required
def change_password():
    current_pw = request.form.get('current_password')
    new_pw = request.form.get('new_password')
    confirm_pw = request.form.get('confirm_password')
    current_email = session.get('user_id')
    hashed = USERS.get(current_email)
    if not hashed or not bcrypt.checkpw(current_pw.encode('utf-8'), hashed.encode('utf-8')):
        return redirect(url_for('settings', msg_pw='wrong'))
    if not new_pw or new_pw != confirm_pw:
        return redirect(url_for('settings', msg_pw='mismatch'))
    USERS[current_email] = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    return redirect(url_for('settings', msg_pw='success'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if not email or not password:
            return render_template('register.html', error='E-Mail und Passwort benötigt!')
        if not is_valid_email(email):
            return render_template('register.html', error='Ungültige E-Mail-Adresse!')
        if password != confirm:
            return render_template('register.html', error='Passwörter stimmen nicht überein!')
        if email in USERS:
            return render_template('register.html', error='E-Mail existiert bereits!')

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        USERS[email] = hashed
        session['user_id'] = email
        return redirect(url_for('index'))

    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
