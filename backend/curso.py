from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity, unset_jwt_cookies
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__) 
bcrypt = Bcrypt(app) 

# Configuración de la conexión a la base de datos
DB_NAME = "edugana_db"
DB_USER = "postgres"
DB_PASS = "System.2025*"
DB_HOST = "127.0.0.1" # o la IP del servidor
DB_PORT = "5432"
# ---------------------------------------------
# 🔌 Conexión a la base de datos
# ---------------------------------------------
def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT,
        cursor_factory=RealDictCursor
    )


# ---------------------------------------------
# 🟢 API: Registrar curso  (POST)
# ---------------------------------------------
@app.route('/api/cursos', methods=['POST'])
@jwt_required()  # requiere token
def registrar_curso():
    data = request.json

    required_fields = ["nombre_curso", "codigo", "nivel_grado",
                       "capacidad_max", "profesor_asignado"]

    # Validar campos obligatorios
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"El campo '{field}' es obligatorio"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        sql = """
            INSERT INTO cursos (nombre_curso, codigo, nivel_grado, capacidad_max, profesor_asignado)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_curso;
        """

        cur.execute(sql, (
            data["nombre_curso"],
            data["codigo"],
            data["nivel_grado"],
            data["capacidad_max"],
            data["profesor_asignado"]
        ))

        new_id = cur.fetchone()["id_curso"]

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "message": "Curso registrado exitosamente",
            "id_curso": new_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------
# 🔵 API: Listar cursos (GET)
# ---------------------------------------------
@app.route('/api/cursos', methods=['GET'])
@jwt_required()
def listar_cursos():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM cursos ORDER BY id_curso ASC;")
        cursos = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(cursos), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------
# 🟡 API: Editar curso (PUT)
# ---------------------------------------------
@app.route('/api/cursos/<int:id_curso>', methods=['PUT'])
@jwt_required()
def editar_curso(id_curso):
    data = request.json

    campos = ["nombre_curso", "codigo", "nivel_grado",
              "capacidad_max", "profesor_asignado"]

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        sql = """
            UPDATE cursos
            SET nombre_curso = %s,
                codigo = %s,
                nivel_grado = %s,
                capacidad_max = %s,
                profesor_asignado = %s
            WHERE id_curso = %s;
        """

        cur.execute(sql, (
            data.get("nombre_curso"),
            data.get("codigo"),
            data.get("nivel_grado"),
            data.get("capacidad_max"),
            data.get("profesor_asignado"),
            id_curso
        ))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Curso actualizado correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------
# 🔴 API: Eliminar curso (DELETE)
# ---------------------------------------------
@app.route('/api/cursos/<int:id_curso>', methods=['DELETE'])
@jwt_required()
def eliminar_curso(id_curso):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM cursos WHERE id_curso = %s;", (id_curso,))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Curso eliminado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
