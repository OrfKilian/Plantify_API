from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from functools import wraps

from smartplant_api.views import views_blueprint
from smartplant_api.users import users_blueprint
from smartplant_api.plants import plants_blueprint
from smartplant_api.authorization import authorization_blueprint

app = Flask(__name__)
app.secret_key = 'super-geheim'

# Simple credential storage for demonstration purposes
USER_CREDENTIALS = {
    'email': 'test@example.com',
    'password': 'test123'
}

# Datenbankkonfiguration für die SmartPlant-API
app.config['DB_CONFIG'] = {
    "host": "192.168.178.162",
    "user": "admin",
    "password": "thws2025",
    "database": "smartplantpot",
}

# SmartPlant-API Blueprints einbinden
app.register_blueprint(views_blueprint, url_prefix='/api')
app.register_blueprint(users_blueprint, url_prefix='/api')
app.register_blueprint(plants_blueprint, url_prefix='/api')
app.register_blueprint(authorization_blueprint, url_prefix='/api')

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

def slugify(value: str) -> str:
    return value.lower().replace(" ", "-")

# Generate a unique slug for a plant by appending its id to the
# slugified name. This allows multiple plants with the same name to
# exist and be addressed individually.
def plant_slug(plant: dict) -> str:
    return f"{slugify(plant['name'])}-{plant['id']}"

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
        if email == USER_CREDENTIALS['email'] and password == USER_CREDENTIALS['password']:
            session['user_id'] = email
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        return render_template('login.html', error='Falsche Login-Daten!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')  # Nach dem Logout zur Login-Seite weiterleiten

# API für Sidebar und Dashboard
@app.route('/api/items')
def api_items():
    return jsonify({"rooms": ROOMS, "plants": PLANTS})

# Endpoint to update room names
@app.route('/api/rooms/<slug>', methods=['POST'])
def update_room(slug):
    room = next((r for r in ROOMS if slugify(r['name']) == slug), None)
    if not room:
        return jsonify({"error": "not found"}), 404
    data = request.get_json() or {}
    new_name = data.get('name')
    if new_name:
        old_name = room['name']
        room['name'] = new_name
        for plant in PLANTS:
            if plant.get('room') == old_name:
                plant['room'] = new_name
    return jsonify(room)

@app.route('/api/plants/<int:plant_id>', methods=['GET', 'POST'])
def api_plant(plant_id):
    plant = next((p for p in PLANTS if p["id"] == plant_id), None)
    if not plant:
        return jsonify({"error": "not found"}), 404
    if request.method == 'POST':
        data = request.get_json() or {}
        if 'name' in data and data['name']:
            plant['name'] = data['name']
        plant['facts'] = data.get('facts', plant['facts'])
        room_val = data.get('room', plant['room'])
        plant['room'] = room_val if room_val else None
        plant['target_temperature'] = data.get('target_temperature', plant['target_temperature'])
        plant['target_air_humidity'] = data.get('target_air_humidity', plant['target_air_humidity'])
        plant['target_ground_humidity'] = data.get('target_ground_humidity', plant['target_ground_humidity'])
    return jsonify(plant)

@app.route('/api/plants/<int:plant_id>/room', methods=['DELETE'])
def remove_plant_room(plant_id):
    """Remove plant from its assigned room."""
    plant = next((p for p in PLANTS if p["id"] == plant_id), None)
    if not plant:
        return jsonify({"error": "not found"}), 404
    plant['room'] = None
    return jsonify({"message": "Pflanze aus Zimmer entfernt", "plant": plant})

@app.route('/dashboard/<slug>')
@login_required
def dashboard(slug):
    room = next((r for r in ROOMS if slugify(r['name']) == slug), None)
    if not room:
        return "Zimmer nicht gefunden", 404
    plants = [p for p in PLANTS if p.get('room') == room['name']]
    return render_template('dashboard.html', room=room['name'], room_slug=slug, plants=plants)

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
    if new_email:
        USER_CREDENTIALS['email'] = new_email
        session['user_id'] = new_email
        return redirect(url_for('settings', msg_email='success'))
    return redirect(url_for('settings', msg_email='error'))


@app.route('/settings/change-password', methods=['POST'])
@login_required
def change_password():
    current_pw = request.form.get('current_password')
    new_pw = request.form.get('new_password')
    confirm_pw = request.form.get('confirm_password')
    if current_pw != USER_CREDENTIALS['password']:
        return redirect(url_for('settings', msg_pw='wrong'))
    if not new_pw or new_pw != confirm_pw:
        return redirect(url_for('settings', msg_pw='mismatch'))
    USER_CREDENTIALS['password'] = new_pw
    return redirect(url_for('settings', msg_pw='success'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Hier kann später Registrierungslogik ergänzt werden
    return render_template('register.html')

# ----- Diagramme Routes -----
@app.route('/diagramme/temperatur')
@login_required
def diagramm_temperatur():
    """Zeigt den Beispielgraphen für den Temperaturverlauf."""
    return render_template('diagramme/temperatur_verlauf.html')

@app.route('/debugtest')
def debugtest():
    return "DEBUG ROUTE OK"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
