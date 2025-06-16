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

# Dummy-Daten für Sidebar
# Angepasste Töpfe für die Sidebar
POTS = [
    {"name": "Wohnzimmer"},
    {"name": "Badezimmer"},
    {"name": "Balkon"}
]

PLANTS = [
    {"name": "Tomate"},
    {"name": "Orchidee"},
    {"name": "Monstera"},
    {"name": "Strelitzie"},
    {"name": "Orchidee 2"},
]

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

# API für Sidebar
@app.route('/api/items')
def api_items():
    return jsonify({"pots": POTS, "plants": PLANTS})

# Item-Detailseite (Platzhalter)
@app.route('/pflanze/<name>')
@login_required
def plant_detail(name):
    # Dummy-Werte für Ansicht
    return render_template('plant.html', trivial=name.title(), botanisch=name.title())

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
