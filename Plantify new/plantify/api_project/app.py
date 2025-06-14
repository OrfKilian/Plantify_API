from flask import Flask
from flask_cors import CORS
from smartplant_api.views import views_blueprint
from smartplant_api.users import users_blueprint
from smartplant_api.plants import plants_blueprint
from smartplant_api.authorization import authorization_blueprint

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database configuration
app.config['DB_CONFIG'] = {
    "host": "192.168.178.162",
    "user": "admin",
    "password": "thws2025",
    "database": "smartplantpot",
}

# Register blueprints
app.register_blueprint(views_blueprint, url_prefix='/api')
app.register_blueprint(users_blueprint, url_prefix='/api')
app.register_blueprint(plants_blueprint, url_prefix='/api')
app.register_blueprint(authorization_blueprint, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Using port 5001 for API 