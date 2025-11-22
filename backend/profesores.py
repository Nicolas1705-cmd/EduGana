from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
import psycopg2
from psycopg2.extras import RealDictCursor

# =====================================
# APP + CONFIG
# =====================================

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Configuración JWT
app.config["JWT_SECRET_KEY"] = "super-secret-key"
jwt = JWTManager(app)

# Configuración BD (TU SERVIDOR REAL)
DB_NAME = "edugana_db"
DB_USER = "postgres"
DB_PASS = "System.2025*"
DB_HOST = "35.237.18.79"
DB_PORT = "5432"


def get_db_connection():
    try:
        return psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT,
            cursor_factory=RealDictCursor
        )
    except Exception as e:
        print("ERROR DE CONEXIÓN:", e)
        return None


# =====================================
# UTILIDAD
# =====================================

def fetchall_to_dict(cursor):
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


# =====================================
# 1. GET — LISTAR PROFESORES
# =====================================

@app.route('/profesores', methods=['GET'])
def listar_profesores():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "No se pudo conectar a la base de datos"}), 500

    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                id_profesor,
                dni,
                nombre_completo,
                fecha_nacimiento,
                genero,
                email_personal,
                telefono,
                direccion_residencia,
                titulo_especialidad,
                id_colegio_asignado
            FROM profesores
            ORDER BY id_profesor ASC;
        """)

        data = cur.fetchall()
        return jsonify(data), 200

    except Exception as e:
        print("ERROR BD:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()


# =====================================
# 2. POST — REGISTRAR PROFESOR
# =====================================

@app.route('/profesores', methods=['POST'])
def agregar_profesor():
    data = request.get_json()

    required = [
        "dni", "nombre_completo", "fecha_nacimiento",
        "genero", "email_personal", "telefono",
        "direccion_residencia", "titulo_especialidad"
    ]

    for field in required:
        if field not in data:
            return jsonify({"message": f"Falta el campo obligatorio: {field}"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "No se pudo conectar a la base de datos"}), 500

    try:
        cur = conn.cursor()

        sql = """
            INSERT INTO profesores (
                dni, nombre_completo, fecha_nacimiento,
                genero, email_personal, telefono,
                direccion_residencia, titulo_especialidad,
                id_colegio_asignado
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id_profesor;
        """

        values = (
            data["dni"],
            data["nombre_completo"],
            data["fecha_nacimiento"],
            data["genero"],
            data["email_personal"],
            data["telefono"],
            data["direccion_residencia"],
            data["titulo_especialidad"],
            data.get("id_colegio_asignado")  # puede ser null
        )

        cur.execute(sql, values)
        new_id = cur.fetchone()["id_profesor"]

        conn.commit()

        return jsonify({"message": "Profesor registrado", "id": new_id}), 201

    except Exception as e:
        conn.rollback()
        print("ERROR INSERT:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()


# =====================================
# 3. DELETE — ELIMINAR PROFESOR
# =====================================

@app.route('/profesores/<int:id_profesor>', methods=['DELETE'])
def eliminar_profesor(id_profesor):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "No se pudo conectar a la BD"}), 500

    try:
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM profesores WHERE id_profesor = %s RETURNING id_profesor;",
            (id_profesor,)
        )
        result = cur.fetchone()

        conn.commit()

        if result is None:
            return jsonify({"message": "Profesor no encontrado"}), 404

        return jsonify({"message": "Profesor eliminado correctamente"}), 200

    except Exception as e:
        conn.rollback()
        print("ERROR DELETE:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()


# =====================================
# SERVIDOR
# =====================================

if __name__ == '__main__':
    print("🔥 Servidor ejecutándose en http://localhost:5000")
    app.run(debug=True)
