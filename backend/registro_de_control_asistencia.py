from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# ============================
# CONFIG BASE DE DATOS
# ============================
DB_NAME = "edugana_db"
DB_USER = "postgres"
DB_PASS = "System.2025*"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"

def get_db():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT,
        cursor_factory=RealDictCursor
    )

# ============================
# POST: REGISTRAR ASISTENCIA
# ============================
@app.route("/api/asistencia/manual", methods=["POST"])
def registrar_asistencia():
    try:
        data = request.get_json()

        estudiante_id = data.get("dni")
        nombre_estudiante = f"{data.get('nombres', '')} {data.get('apellidos', '')}".strip()
        fecha = data.get("fecha")
        asistencia = data.get("estado_asistencia")
        hora_entrada = data.get("hora_entrada")
        observaciones = data.get("observacion")
        colegio = data.get("colegio")

        if not estudiante_id or not nombre_estudiante or not fecha or not asistencia:
            return jsonify({"mensaje": "Faltan campos obligatorios"}), 400

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO asistencias (
                estudiante_id, nombre_estudiante, fecha,
                asistencia, hora_entrada, observaciones, colegio
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            estudiante_id, nombre_estudiante, fecha,
            asistencia, hora_entrada, observaciones, colegio
        ))

        conn.commit()
        new_id = cur.fetchone()["id"]

        cur.close()
        conn.close()

        return jsonify({
            "mensaje": "Asistencia registrada correctamente",
            "id_registro": new_id
        }), 201

    except Exception as e:
        print("Error:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500

# ============================
# GET: LISTAR ASISTENCIAS
# ============================
@app.route("/api/asistencias", methods=["GET"])
def obtener_asistencias():
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM asistencias ORDER BY fecha DESC;")
        asistencia = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(asistencia), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500

# ============================
# RUN
# ============================
if __name__ == "__main__":
    app.run(debug=True)
