from flask import Blueprint, jsonify, current_app, request
import mysql.connector
from datetime import datetime, timedelta

def get_db_cursor():
    connection = mysql.connector.connect(**current_app.config['DB_CONFIG'])
    cursor = connection.cursor(dictionary=True)
    return connection, cursor

def _generate_dummy_measurements(pot_id: int):
    """Return a list of measurements for a single day.

    The values roughly match those used in the example plot so that the
    frontend can display a realistic looking graph without a database."""
    base_time = datetime(2025, 6, 22, 8)
    temperatures = [
        21.3, 21.5, 22.8, 23.2, 24.1, 24.7,
        25.0, 24.3, 23.7, 22.9, 22.1, 21.5
    ]
    data = []
    for i, temp in enumerate(temperatures):
        timestamp = base_time + timedelta(hours=i)
        data.append({
            "created": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": temp,
            "air_humidity": 40.0 + i * 0.5,
            "ground_humidity": 35.5 + i * 0.3,
            "HoS": 6.0,
            "pot_id": pot_id
        })
    return data


def fetch_query_results(query, pot_id, fetchone=False):
    # Immer Dummy-Daten zurückgeben – unabhängig vom Testmodus
    measurements = _generate_dummy_measurements(pot_id)
    return jsonify(measurements[-1] if fetchone else measurements)

views_blueprint = Blueprint('views', __name__)

@views_blueprint.route("/ping")
def ping():
    return jsonify({"message": "API läuft"})

@views_blueprint.route("/latest-today", methods=["GET"])
def get_latest_today():
    pot_id = request.args.get('pot_id')
    query = "SELECT * FROM viw_LatestValuePerPot WHERE pot_id = %s"
    return fetch_query_results(query, pot_id)

@views_blueprint.route("/all-today", methods=["GET"])
def get_all_today():
    pot_id = request.args.get('pot_id')
    query = "SELECT * FROM viw_AllValues_Today WHERE pot_id = %s"
    return fetch_query_results(query, pot_id)

@views_blueprint.route("/sunlight-30days", methods=["GET"])
def get_sunlight_30days():
    pot_id = request.args.get('pot_id')
    query = "SELECT * FROM viw_SunlightPerDay_last30Days WHERE pot_id = %s"
    return fetch_query_results(query, pot_id)

@views_blueprint.route("/average-month", methods=["GET"])
def get_average_month():
    pot_id = request.args.get('pot_id')
    query = "SELECT * FROM viw_AverageMeasurements_MTD WHERE pot_id = %s"
    return fetch_query_results(query, pot_id)

@views_blueprint.route('/latest-value', methods=['GET'])
def get_latest_value():
    pot_id = request.args.get('pot_id')
    query = '''
        SELECT created, temperature, air_humidity, ground_humidity
        FROM viw_LatestValuePerPot
        WHERE pot_id = %s
    '''
    return fetch_query_results(query, pot_id, fetchone=True)
