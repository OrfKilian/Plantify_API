

from flask import Blueprint, request, jsonify, current_app
import mysql.connector

authorization_blueprint = Blueprint('authorization', __name__)

@authorization_blueprint.route("/authorize-pot", methods=["POST"])
def authorize_pot():
    data = request.get_json()
    user_id = data.get("user_id")
    pot_id = data.get("pot_id")

    if not user_id or not pot_id:
        return jsonify({"error": "user_id und pot_id sind erforderlich"}), 400

    try:
        connection = mysql.connector.connect(**current_app.config['DB_CONFIG'])
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO pot_user (user_id, pot_id) VALUES (%s, %s)",
            (user_id, pot_id)
        )
        connection.commit()
        return jsonify({"message": f"Berechtigung für user_id={user_id} auf pot_id={pot_id} erfolgreich vergeben"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
