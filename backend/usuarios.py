from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    create_access_token, JWTManager,
    jwt_required, get_jwt_identity
)
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
bcrypt = Bcrypt(app)

# ============================
# CREDENCIALES (LAS TUYAS)
# ============================
DB_NAME = "edugana_db"
DB_USER = "postgres"
DB_PASS = "System.2025*"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"

# JWT
app.config["JWT_SECRET_KEY"] = "cambia-este-secret"
jwt = JWTManager(app)

# ----------------------------
# Conexión a PostgreSQL
# ----------------------------
def get_conn():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )

# ======================================================
#   📌 1. Registrar asistencia
# ======================================================
@app.route("/asistencias", methods=["POST"])
@jwt_required()
def registrar_asistencia():
    data = request.get_json()

    estudiante_id = data.get("estudiante_id")
    nombre_estudiante = data.get("nombre_estudiante")
    fecha = data.get("fecha")
    asistencia = data.get("asistencia")
    hora_entrada = data.get("hora_entrada")
    observaciones = data.get("observaciones")

    try:
        conn = get_conn()
        cur = conn.cursor()

        query = """
            INSERT INTO asistencias (
                estudiante_id, nombre_estudiante, fecha,
                asistencia, hora_entrada, observaciones
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        cur.execute(query, (
            estudiante_id, nombre_estudiante, fecha,
            asistencia, hora_entrada, observaciones
        ))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"msg": "Asistencia registrada exitosamente"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
#   📌 2. Obtener historial completo
# ======================================================
@app.route("/asistencias", methods=["GET"])
@jwt_required()
def obtener_asistencias():
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT * FROM asistencias ORDER BY fecha DESC;")
        data = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
#   📌 3. Historial por estudiante
# ======================================================
@app.route("/asistencias/estudiante/<int:estudiante_id>", methods=["GET"])
@jwt_required()
def asistencias_por_estudiante(estudiante_id):
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT * FROM asistencias WHERE estudiante_id = %s ORDER BY fecha DESC;", (estudiante_id,))
        data = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
#   📌 4. Historial por fecha
# ======================================================
@app.route("/asistencias/fecha/<fecha>", methods=["GET"])
@jwt_required()
def asistencias_por_fecha(fecha):
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT * FROM asistencias WHERE fecha = %s;", (fecha,))
        data = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
#   📌 5. Actualizar asistencia
# ======================================================
@app.route("/asistencias/<int:id>", methods=["PUT"])
@jwt_required()
def actualizar_asistencia(id):
    data = request.get_json()

    try:
        conn = get_conn()
        cur = conn.cursor()

        query = """
            UPDATE asistencias SET
            estudiante_id=%s,
            nombre_estudiante=%s,
            fecha=%s,
            asistencia=%s,
            hora_entrada=%s,
            observaciones=%s
            WHERE id=%s
        """

        cur.execute(query, (
            data.get("estudiante_id"),
            data.get("nombre_estudiante"),
            data.get("fecha"),
            data.get("asistencia"),
            data.get("hora_entrada"),
            data.get("observaciones"),
            id
        ))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"msg": "Asistencia actualizada"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
#   📌 6. Eliminar asistencia
# ======================================================
@app.route("/asistencias/<int:id>", methods=["DELETE"])
@jwt_required()
def eliminar_asistencia(id):
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("DELETE FROM asistencias WHERE id = %s;", (id,))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"msg": "Asistencia eliminada"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ======================================================
#   RUN SERVER
# ======================================================
if __name__ == "__main__":
    app.run(debug=True)
