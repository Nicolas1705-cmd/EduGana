from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2 import pool

app = Flask(__name__)
CORS(app)  # Habilitar CORS

# Configuración de conexión directa a PostgreSQL - Base de datos alumnos
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'alumnos',
    'user': 'postgres',
    'password': 'System.2025*'
}

# Pool de conexiones
connection_pool = None

try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, **DB_CONFIG)
    print("✅ Conexión exitosa a base de datos: alumnos")
except Exception as e:
    print(f"❌ Error al conectar: {e}")

def get_db_connection():
    if connection_pool is None:
        return None
    try:
        return connection_pool.getconn()
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def release_connection(conn):
    if conn and connection_pool:
        connection_pool.putconn(conn)

# --- 1️⃣ Agregar alumno ---
@app.route('/alumnos', methods=['POST'])
def agregar_alumno():
    data = request.get_json()

    if data is None:
        return jsonify({"error": "⚠️ No se recibió JSON válido"}), 400

    required_fields = ['id_colegio', 'fecha_nacimiento', 'nombre', 'apellido', 'correo', 'telefono', 'nombre_apoderado', 'dni_apoderado']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({
            "error": "⚠️ Faltan campos requeridos",
            "campos_faltantes": missing_fields
        }), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "❌ Error de conexión a la base de datos"}), 500

    cur = None
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Alumnos (id_colegio, fecha_nacimiento, nombre, apellido, correo, telefono, nombre_apoderado, dni_apoderado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_alumno;
        """, (
            data['id_colegio'],
            data['fecha_nacimiento'],
            data['nombre'],
            data['apellido'],
            data['correo'],
            data['telefono'],
            data['nombre_apoderado'],
            data['dni_apoderado']
        ))

        new_id = cur.fetchone()[0]
        conn.commit()
        
        print(f"✅ Alumno {new_id} registrado: {data['nombre']} {data['apellido']}")

        return jsonify({
            "message": "✅ Alumno registrado correctamente",
            "id_alumno": new_id,
            "nombre_completo": f"{data['nombre']} {data['apellido']}"
        }), 201

    except psycopg2.IntegrityError as e:
        if conn:
            conn.rollback()
        print(f"⚠️ Error de integridad: {e}")
        return jsonify({"error": "⚠️ Error de validación de datos (posible correo duplicado)"}), 400
    
    except psycopg2.DatabaseError as e:
        if conn:
            conn.rollback()
        print(f"❌ Error de base de datos: {e}")
        return jsonify({"error": "❌ Error en la base de datos"}), 500
    
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error inesperado: {e}")
        return jsonify({"error": f"❌ Error al registrar alumno: {str(e)}"}), 500
    
    finally:
        if cur:
            cur.close()
        release_connection(conn)


# --- 2️⃣ Eliminar alumno ---
@app.route('/alumnos/<int:id_alumno>', methods=['DELETE'])
def eliminar_alumno(id_alumno):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "❌ Error de conexión a la base de datos"}), 500

    cur = None
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM Alumnos WHERE id_alumno = %s RETURNING id_alumno, nombre, apellido;", (id_alumno,))
        result = cur.fetchone()
        conn.commit()

        if result:
            print(f"✅ Alumno {result[0]} eliminado: {result[1]} {result[2]}")
            return jsonify({
                "message": "✅ Alumno eliminado correctamente",
                "id_alumno": result[0],
                "nombre_completo": f"{result[1]} {result[2]}"
            }), 200
        else:
            return jsonify({"error": f"⚠️ Alumno con ID {id_alumno} no encontrado"}), 404

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error: {e}")
        return jsonify({"error": f"❌ Error al eliminar alumno: {str(e)}"}), 500
    
    finally:
        if cur:
            cur.close()
        release_connection(conn)


# --- 3️⃣ Listar alumnos ---
@app.route('/alumnos', methods=['GET'])
def listar_alumnos():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "❌ Error de conexión a la base de datos"}), 500

    cur = None
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id_alumno, id_colegio, fecha_nacimiento, nombre, apellido, correo, telefono, nombre_apoderado, dni_apoderado
            FROM Alumnos
            ORDER BY id_alumno;
        """)

        rows = cur.fetchall()

        alumnos = []
        for r in rows:
            alumnos.append({
                "id_alumno": r[0],
                "id_colegio": r[1],
                "fecha_nacimiento": str(r[2]) if r[2] else None,
                "nombre": r[3],
                "apellido": r[4],
                "correo": r[5],
                "telefono": r[6],
                "nombre_apoderado": r[7],
                "dni_apoderado": r[8]
            })

        print(f"📋 {len(alumnos)} alumnos encontrados")
        return jsonify({
            "total": len(alumnos),
            "alumnos": alumnos
        }), 200

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": f"❌ Error al listar alumnos: {str(e)}"}), 500
    
    finally:
        if cur:
            cur.close()
        release_connection(conn)


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SERVIDOR API ALUMNOS")
    print("="*60)
    print(f"📍 URL: http://localhost:5002")
    print(f"📊 Base de datos: {DB_CONFIG['database']}")
    print(f"🔌 PostgreSQL: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print("\n📚 ENDPOINTS DISPONIBLES:")
    print("   POST   /alumnos          - Registrar nuevo alumno")
    print("   GET    /alumnos          - Listar todos los alumnos")
    print("   DELETE /alumnos/<id>     - Eliminar alumno por ID")
    print("="*60 + "\n")
    
    if connection_pool is None:
        print("⚠️  ADVERTENCIA: No hay conexión a la base de datos\n")
    
    app.run(debug=True, port=5002, host='0.0.0.0')