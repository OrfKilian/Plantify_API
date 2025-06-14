from flask import Blueprint, request, jsonify, current_app
import mysql.connector

plants_blueprint = Blueprint('plants', __name__)

@plants_blueprint.route("/plants", methods=["POST"])
def add_plant():
    data = request.get_json()
    name = data.get("name")
    irrigation_cycle = data.get("irrigation_cycle")
    description = data.get("description")
    pot_id = data.get("pot_id")

    if not name or irrigation_cycle is None or not pot_id:
        return jsonify({"error": "Felder 'name', 'irrigation_cycle' und 'pot_id' sind erforderlich"}), 400

    try:
        connection = mysql.connector.connect(**current_app.config['DB_CONFIG'])
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO plant (name, irrigation_cycle, description, pot_id) VALUES (%s, %s, %s, %s)",
            (name, irrigation_cycle, description, pot_id)
        )
        connection.commit()
        return jsonify({"message": "Pflanze erfolgreich gespeichert"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
