from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde el frontend

# ============================
# CREDENCIALES
# ============================
DB_NAME = "edugana_db"
DB_USER = "postgres"
DB_PASS = "System.2025*"
DB_HOST = "172.60.15.207"
DB_PORT = "5432"

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
def registrar_asistencia():
    data = request.get_json()

    estudiante_id = data.get("estudiante_id")
    nombre_estudiante = data.get("nombre_estudiante")
    fecha = data.get("fecha")
    asistencia = data.get("asistencia")  # True/False o "Presente"/"Ausente"
    hora_entrada = data.get("hora_entrada")
    observaciones = data.get("observaciones")

    # Convertir string a boolean si es necesario
    if isinstance(asistencia, str):
        asistencia = asistencia.lower() in ['presente', 'true', '1']

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
def obtener_asistencias():
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT 
                id,
                estudiante_id,
                nombre_estudiante,
                fecha,
                CASE 
                    WHEN asistencia = true THEN 'Presente'
                    ELSE 'Ausente'
                END as asistencia,
                hora_entrada,
                observaciones
            FROM asistencias 
            ORDER BY fecha DESC, hora_entrada DESC
        """)
        data = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
#   📌 3. Obtener por estudiante
# ======================================================
@app.route("/asistencias/estudiante/<int:estudiante_id>", methods=["GET"])
def asistencias_por_estudiante(estudiante_id):
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT 
                id,
                estudiante_id,
                nombre_estudiante,
                fecha,
                CASE 
                    WHEN asistencia = true THEN 'Presente'
                    ELSE 'Ausente'
                END as asistencia,
                hora_entrada,
                observaciones
            FROM asistencias 
            WHERE estudiante_id = %s
            ORDER BY fecha DESC
        """, (estudiante_id,))
        data = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
#   📌 4. Obtener por fecha
# ======================================================
@app.route("/asistencias/fecha/<fecha>", methods=["GET"])
def asistencias_por_fecha(fecha):
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT 
                id,
                estudiante_id,
                nombre_estudiante,
                fecha,
                CASE 
                    WHEN asistencia = true THEN 'Presente'
                    ELSE 'Ausente'
                END as asistencia,
                hora_entrada,
                observaciones
            FROM asistencias 
            WHERE fecha = %s
            ORDER BY hora_entrada
        """, (fecha,))
        data = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
#   📌 5. Obtener estadísticas
# ======================================================
@app.route("/asistencias/estadisticas", methods=["GET"])
def obtener_estadisticas():
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN asistencia = true THEN 1 END) as presentes,
                COUNT(CASE WHEN asistencia = false THEN 1 END) as ausentes
            FROM asistencias
        """)
        stats = cur.fetchone()
        
        cur.close()
        conn.close()

        return jsonify(stats), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
#   📌 6. Actualizar asistencia
# ======================================================
@app.route("/asistencias/<int:id>", methods=["PUT"])
def actualizar_asistencia(id):
    data = request.get_json()
    
    asistencia = data.get("asistencia")
    observaciones = data.get("observaciones")
    
    # Convertir string a boolean si es necesario
    if isinstance(asistencia, str):
        asistencia = asistencia.lower() in ['presente', 'true', '1']
    
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE asistencias 
            SET asistencia = %s, observaciones = %s
            WHERE id = %s
        """, (asistencia, observaciones, id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"msg": "Asistencia actualizada exitosamente"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
#   📌 7. Eliminar asistencia
# ======================================================
@app.route("/asistencias/<int:id>", methods=["DELETE"])
def eliminar_asistencia(id):
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        cur.execute("DELETE FROM asistencias WHERE id = %s", (id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"msg": "Asistencia eliminada exitosamente"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
#   RUN SERVER
# ======================================================
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)