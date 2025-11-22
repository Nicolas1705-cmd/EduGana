from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from configbd import get_db_connection



app = Flask(__name__)

@app.route("/api/grado1", methods=["POST"])
def registrar_grado():
    data = request.json

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        sql = """
            INSERT INTO grado (nombre_grado, nivel, capacidad, estado)
            VALUES (%s, %s, %s, %s)
            RETURNING id_grado;
        """

        cur.execute(sql, (
            data["nombre_grado"],
            data.get("nivel", None),
            data.get("capacidad", 0),
            data.get("estado", True)
        ))

        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"mensaje": "Grado registrado", "id": new_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
