

from flask import Blueprint, request, jsonify, current_app
import bcrypt
import mysql.connector

users_blueprint = Blueprint('users', __name__)

@users_blueprint.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "E-Mail und Passwort erforderlich"}), 400

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        connection = mysql.connector.connect(**current_app.config['DB_CONFIG'])
        cursor = connection.cursor()
        # Prüfen, ob E-Mail schon existiert
        cursor.execute("SELECT * FROM User WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"error": "E-Mail bereits vergeben"}), 409
        # Einfügen
        cursor.execute(
            "INSERT INTO User (email, password_hash) VALUES (%s, %s)",
            (email, password_hash)
        )
        connection.commit()
        return jsonify({"message": "Benutzer erfolgreich angelegt"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
