from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from functools import wraps

from smartplant_api.views import views_blueprint
from smartplant_api.users import users_blueprint
from smartplant_api.plants import plants_blueprint
from smartplant_api.authorization import authorization_blueprint

app = Flask(__name__)
app.secret_key = 'super-geheim'

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
        if email == 'test@example.com' and password == 'test123':
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

@app.route('/api/plants/<int:plant_id>', methods=['GET', 'POST'])
def api_plant(plant_id):
    plant = next((p for p in PLANTS if p["id"] == plant_id), None)
    if not plant:
        return jsonify({"error": "not found"}), 404
    if request.method == 'POST':
        data = request.get_json() or {}
        plant['facts'] = data.get('facts', plant['facts'])
        plant['room'] = data.get('room', plant['room'])
        plant['target_temperature'] = data.get('target_temperature', plant['target_temperature'])
        plant['target_air_humidity'] = data.get('target_air_humidity', plant['target_air_humidity'])
        plant['target_ground_humidity'] = data.get('target_ground_humidity', plant['target_ground_humidity'])
    return jsonify(plant)

@app.route('/dashboard/<slug>')
@login_required
def dashboard(slug):
    room = next((r for r in ROOMS if slugify(r['name']) == slug), None)
    if not room:
        return "Zimmer nicht gefunden", 404
    plants = [p for p in PLANTS if p.get('room') == room['name']]
    return render_template('dashboard.html', room=room['name'], plants=plants)

# Plantendetail und Bearbeitung
@app.route('/pflanze/<slug>')
@login_required
def plant_detail(slug):
    plant = next((p for p in PLANTS if slugify(p['name']) == slug), None)
    if not plant:
        return "Pflanze nicht gefunden", 404
    return render_template('plant.html', plant=plant, rooms=ROOMS,
                           trivial=plant['name'], botanisch=plant['name'])

# Einstellungen
@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Hier kann später Registrierungslogik ergänzt werden
    return render_template('register.html')

@app.route('/debugtest')
def debugtest():
    return "DEBUG ROUTE OK"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
