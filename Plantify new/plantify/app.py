from flask import Flask, render_template, request, redirect, session, url_for, jsonify, Request

# expose form values via request.post(...)
if not hasattr(Request, "post"):
    Request.post = lambda self, key, default=None: self.form.get(key, default)
from functools import wraps
import os
import base64
from hashlib import pbkdf2_hmac
from email_validator import validate_email, EmailNotValidError
import requests
from typing import Optional


app = Flask(__name__)

# Use a fixed user account during development so the app works without a
# registration or login step. This allows testing the UI immediately.
TEST_USER = "admin@plantpot"
# The password for the fixed test account. The account is automatically
# created with this password if it does not already exist.
TEST_PASSWORD = "test123"
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    print(
        "WARNING: SECRET_KEY environment variable not set - using insecure "
        "development key",
        flush=True,
    )
    secret_key = 'dev-secret'
app.secret_key = secret_key

# Automatically sign in using the fixed test account if no user is currently
# stored in the session. If the account doesn't exist yet, it is created with
# the default password for convenience during local development.
_test_user_initialized = False

@app.before_request
def ensure_test_user():
    global _test_user_initialized
    if not _test_user_initialized:
        try:
            hashed = get_password_hash(TEST_USER)
            if not hashed:
                hashed = hash_password(TEST_PASSWORD)
                requests.get(
                    f"{API_BASE}/insert/insert-user",
                    params={"user_mail": TEST_USER, "password_hash": hashed},
                )
        except requests.RequestException:
            pass
        _test_user_initialized = True
    if 'user_id' not in session:
        session['user_id'] = TEST_USER

API_BASE = os.environ.get('API_URL', 'http://localhost:5001')

PLANT_OVERRIDES = {}

def fetch_rooms():
    user = session.get('user_id')
    if not user:
        return []
    try:
        r = requests.get(f"{API_BASE}/json/pots", params={"user_mail": user})
        if r.status_code == 200:
            return [
                {"name": p.get("pot_name", p.get("name", "")), "id": p.get("pot_id")}
                for p in r.json()
            ]
    except requests.RequestException:
        pass
    return []


def fetch_plants():
    user = session.get('user_id')
    if not user:
        return []
    try:
        r = requests.get(f"{API_BASE}/json/plants", params={"user_mail": user})
        if r.status_code == 200:
            plants = []
            for item in r.json():
                plant = {
                    "id": item.get("plant_id"),
                    "name": item.get("name"),
                    "facts": item.get("description", ""),
                    "room": item.get("pot_name"),
                    "target_temperature": item.get("target_temperature_celsius"),
                    "target_air_humidity": item.get("target_air_humidity_percent"),
                    "target_ground_humidity": item.get("target_soil_moisture_percent"),
                }
                if plant["id"] in PLANT_OVERRIDES:
                    plant.update(PLANT_OVERRIDES[plant["id"]])
                plants.append(plant)
            return plants
    except requests.RequestException:
        pass
    return []


@app.context_processor
def inject_sidebar_data():
    return dict(rooms=fetch_rooms(), plants=fetch_plants(), api_base=API_BASE)

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

def hash_password(password: str) -> str:
    """Hash a password using PBKDF2 with SHA-256."""
    salt = os.urandom(16)
    dk = pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return base64.b64encode(salt + dk).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    """Verify a password against the stored hash."""
    try:
        data = base64.b64decode(hashed.encode('utf-8'))
    except (TypeError, ValueError):
        return False
    salt, dk = data[:16], data[16:]
    new_dk = pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return new_dk == dk

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

def get_password_hash(email: str) -> Optional[str]:
    try:
        r = requests.get(f"{API_BASE}/json/password_hash", params={"user_mail": email})
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and data:
                return data[0].get("password_hash")
            if isinstance(data, dict):
                return data.get("password_hash")
    except requests.RequestException:
        pass
    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == TEST_USER and password == TEST_PASSWORD:
            session['user_id'] = email
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        hashed = get_password_hash(email)
        if hashed and check_password(password, hashed):
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
    rooms = fetch_rooms()
    plants = fetch_plants()
    room = next((r for r in rooms if slugify(r['name']) == slug), None)
    if not room:
        return "Zimmer nicht gefunden", 404
    room_plants = [p for p in plants if p.get('room') == room['name']]
    return render_template('dashboard.html', room=room['name'], room_slug=slug,
                           room_plants=room_plants)

# Seite zum Umbenennen der Zimmer
@app.route('/rooms')
@login_required
def rooms_page():
    rooms = fetch_rooms()
    room_entries = [{'name': r['name'], 'slug': slugify(r['name'])} for r in rooms]
    return render_template('rooms.html', rooms=room_entries)

# Plantendetail und Bearbeitung
@app.route('/pflanze/<slug>')
@login_required
def plant_detail(slug):
    plants = fetch_plants()
    rooms = fetch_rooms()
    plant = None
    plant_id_part = slug.rsplit('-', 1)[-1]
    if plant_id_part.isdigit():
        plant = next((p for p in plants if str(p['id']) == plant_id_part), None)
    if not plant:
        plant = next((p for p in plants if slugify(p['name']) == slug), None)
    if not plant:
        return "Pflanze nicht gefunden", 404
    return render_template('plant.html', plant=plant, rooms=rooms,
                           trivial=plant['name'], botanisch=plant['name'])

@app.route('/api/plant/<int:plant_id>', methods=['POST'])
@login_required
def update_plant_api(plant_id: int):
    data = request.get_json(silent=True) or {}
    if plant_id not in PLANT_OVERRIDES:
        PLANT_OVERRIDES[plant_id] = {}
    PLANT_OVERRIDES[plant_id].update(data)
    return jsonify({'success': True})

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
    new_email = request.post('new_email')
    current_email = session.get('user_id')
    if new_email and is_valid_email(new_email) and current_email:
        try:
            r = requests.get(
                f"{API_BASE}/update/update-user_mail",
                params={"user_mail_new": new_email, "user_mail": current_email},
            )
            if r.status_code == 200:
                session['user_id'] = new_email
                return redirect(url_for('settings', msg_email='success'))
        except requests.RequestException:
            pass
    return redirect(url_for('settings', msg_email='error'))


@app.route('/settings/change-password', methods=['POST'])
@login_required
def change_password():
    current_pw = request.post('current_password')
    new_pw = request.post('new_password')
    confirm_pw = request.post('confirm_password')
    current_email = session.get('user_id')
    hashed = get_password_hash(current_email) if current_email else None
    if not hashed or not check_password(current_pw, hashed):
        return redirect(url_for('settings', msg_pw='wrong'))
    if not new_pw or new_pw != confirm_pw:
        return redirect(url_for('settings', msg_pw='mismatch'))
    new_hash = hash_password(new_pw)
    try:
        r = requests.get(
            f"{API_BASE}/update/update-user_password",
            params={"password_hash": new_hash, "user_mail": current_email},
        )
        if r.status_code == 200:
            return redirect(url_for('settings', msg_pw='success'))
    except requests.RequestException:
        pass
    return redirect(url_for('settings', msg_pw='error'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.post('email')
        password = request.post('password')
        confirm = request.post('confirm_password')

        if not email or not password:
            return render_template('register.html', error='E-Mail und Passwort benötigt!')
        if not is_valid_email(email):
            return render_template('register.html', error='Ungültige E-Mail-Adresse!')
        if password != confirm:
            return render_template('register.html', error='Passwörter stimmen nicht überein!')
        if get_password_hash(email):
            return render_template('register.html', error='E-Mail existiert bereits!')

        hashed = hash_password(password)
        try:
            r = requests.get(
                f"{API_BASE}/insert/insert-user",
                params={"user_mail": email, "password_hash": hashed},
            )
            if r.status_code == 200:
                session['user_id'] = email
                return redirect(url_for('index'))
        except requests.RequestException:
            pass
        return render_template('register.html', error='Registrierung fehlgeschlagen!')

    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
