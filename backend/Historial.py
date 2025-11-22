from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde el frontend

# ============================
# CREDENCIALES (LAS TUYAS)
# ============================
DB_NAME = "edugana_db"
DB_USER = "postgres"
DB_PASS = "System.2025*"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"

# ============================
# CREDENCIALES COMPAÑERO
# ============================
DB_NAME_COMP = "edugana_db"  # PIDE ESTE DATO
DB_USER_COMP = "postgres"
DB_PASS_COMP = "System.2025*"   # PIDE ESTE DATO
DB_HOST_COMP = "127.0.0.1"        # PIDE LA IP DE SU COMPUTADORA
DB_PORT_COMP = "5432"

# ----------------------------
# Conexión a PostgreSQL (TU BASE DE DATOS)
# ----------------------------
def get_conn():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )

# ----------------------------
# Conexión a PostgreSQL del compañero
# ----------------------------
def get_conn_companero():
    return psycopg2.connect(
        dbname=DB_NAME_COMP,
        user=DB_USER_COMP,
        password=DB_PASS_COMP,
        host=DB_HOST_COMP,
        port=DB_PORT_COMP
    )

# ======================================================
#   📌 1. Registrar asistencia (SIN TOKEN)
# ======================================================
@app.route("/asistencias", methods=["POST"])
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
#   📌 2. Obtener historial completo (SIN TOKEN)
# ======================================================
@app.route("/asistencias", methods=["GET"])
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
#   📌 3. Obtener por estudiante (SIN TOKEN)
# ======================================================
@app.route("/asistencias/estudiante/<int:estudiante_id>", methods=["GET"])
def asistencias_por_estudiante(estudiante_id):
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT * FROM asistencias WHERE estudiante_id = %s;", (estudiante_id,))
        data = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
#   📌 4. Obtener por fecha (SIN TOKEN)
# ======================================================
@app.route("/asistencias/fecha/<fecha>", methods=["GET"])
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
#   📌 5. Obtener asistencias del compañero
# ======================================================
@app.route("/asistencias/companero", methods=["GET"])
def obtener_asistencias_companero():
    try:
        conn = get_conn_companero()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT 
                id_registro,
                dni as estudiante_id,
                CONCAT(nombres, ' ', apellidos) as nombre_estudiante,
                fecha,
                estado_asistencia as asistencia,
                hora_entrada,
                hora_salida,
                observacion as observaciones
            FROM registro_asistencia 
            ORDER BY fecha DESC, hora_entrada DESC
        """)
        data = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
#   📌 6. Obtener historial COMBINADO (ambas bases de datos)
# ======================================================
@app.route("/asistencias/todas", methods=["GET"])
def obtener_todas_asistencias():
    try:
        # Obtener de tu base de datos LOCAL
        conn1 = get_conn()
        cur1 = conn1.cursor(cursor_factory=RealDictCursor)
        cur1.execute("SELECT * FROM asistencias ORDER BY fecha DESC")
        data_local = cur1.fetchall()
        cur1.close()
        conn1.close()

        # Agregar origen a cada registro
        for registro in data_local:
            registro['origen'] = 'local'

        # Obtener de la base de datos del COMPAÑERO
        try:
            conn2 = get_conn_companero()
            cur2 = conn2.cursor(cursor_factory=RealDictCursor)
            cur2.execute("""
                SELECT 
                    id_registro,
                    dni as estudiante_id,
                    CONCAT(nombres, ' ', apellidos) as nombre_estudiante,
                    fecha,
                    estado_asistencia as asistencia,
                    hora_entrada,
                    hora_salida,
                    observacion as observaciones
                FROM registro_asistencia 
                ORDER BY fecha DESC
            """)
            data_companero = cur2.fetchall()
            cur2.close()
            conn2.close()

            # Agregar origen a cada registro
            for registro in data_companero:
                registro['origen'] = 'companero'

        except Exception as e:
            print(f"Error al conectar con compañero: {e}")
            data_companero = []

        # Combinar ambos resultados
        todos_registros = data_local + data_companero
        
        # Ordenar por fecha (más reciente primero)
        todos_registros.sort(key=lambda x: x['fecha'], reverse=True)

        resultado = {
            "registros": todos_registros,
            "total": len(todos_registros),
            "local": len(data_local),
            "companero": len(data_companero)
        }

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
#   📌 7. Obtener estadísticas combinadas
# ======================================================
@app.route("/asistencias/estadisticas", methods=["GET"])
def obtener_estadisticas():
    try:
        # Estadísticas locales
        conn1 = get_conn()
        cur1 = conn1.cursor(cursor_factory=RealDictCursor)
        cur1.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN asistencia = 'Presente' THEN 1 END) as presentes,
                COUNT(CASE WHEN asistencia = 'Ausente' THEN 1 END) as ausentes,
                COUNT(CASE WHEN asistencia = 'Tardanza' THEN 1 END) as tardanzas
            FROM asistencias
        """)
        stats_local = cur1.fetchone()
        cur1.close()
        conn1.close()

        # Estadísticas del compañero
        try:
            conn2 = get_conn_companero()
            cur2 = conn2.cursor(cursor_factory=RealDictCursor)
            cur2.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN estado_asistencia = 'Presente' THEN 1 END) as presentes,
                    COUNT(CASE WHEN estado_asistencia = 'Ausente' THEN 1 END) as ausentes,
                    COUNT(CASE WHEN estado_asistencia = 'Tardanza' THEN 1 END) as tardanzas
                FROM registro_asistencia
            """)
            stats_companero = cur2.fetchone()
            cur2.close()
            conn2.close()
        except:
            stats_companero = {"total": 0, "presentes": 0, "ausentes": 0, "tardanzas": 0}

        # Combinar estadísticas
        resultado = {
            "local": stats_local,
            "companero": stats_companero,
            "total_general": {
                "total": stats_local['total'] + stats_companero['total'],
                "presentes": stats_local['presentes'] + stats_companero['presentes'],
                "ausentes": stats_local['ausentes'] + stats_companero['ausentes'],
                "tardanzas": stats_local['tardanzas'] + stats_companero['tardanzas']
            }
        }

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
#   RUN SERVER
# ======================================================
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)