from flask import Flask, jsonify, request

from flask_bcrypt import Bcrypt
<<<<<<< HEAD
import psycopg2

app = Flask(__name__)
bcrypt = Bcrypt(app)

# -----------------------------
# CONFIGURACIÓN DE BASE DE DATOS
# -----------------------------
=======

from flask_jwt_extended import JWTManager, jwt_required, create_access_token

import psycopg2

from psycopg2.extras import RealDictCursor


from flask_cors import CORS 

app = Flask(__name__)
# ... otras configuraciones

CORS(app) # Permite peticiones desde cualquier origen (necesario para el frontend)

bcrypt = Bcrypt(app)



# ============================================

# CONFIGURACIÓN BASE DE DATOS

# ============================================

>>>>>>> 23c887774217ac5201af5b1bfdb84778578374d4
DB_NAME = "edugana_db"

DB_USER = "postgres"

DB_PASS = "System.2025*"
<<<<<<< HEAD
DB_HOST = "127.0.0.1"
DB_PORT = "5432"

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )

# ----------------------------------------
# 1️⃣ CREAR (REGISTRAR) CURSO - POST
# ----------------------------------------
@app.route('/cursos', methods=['POST'])
def crear_curso():
    data = request.json
    nombre = data.get("nombre_curso")
    codigo = data.get("codigo")
    nivel = data.get("nivel_grado")
    capacidad = data.get("capacidad_max")
    profesor = data.get("profesor_asignado")
    fecha = data.get("fecha_registro")

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        sql = """
            INSERT INTO cursos (nombre_curso, codigo, nivel_grado, capacidad_max, profesor_asignado, fecha_registro)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_curso;
        """

        cur.execute(sql, (nombre, codigo, nivel, capacidad, profesor, fecha))
        new_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"mensaje": "Curso registrado correctamente", "id": new_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------------------
# 2️⃣ LISTAR CURSOS - GET
# ----------------------------------------
@app.route('/cursos', methods=['GET'])
def listar_cursos():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM cursos ORDER BY id_curso ASC;")
        rows = cur.fetchall()

        columnas = [desc[0] for desc in cur.description]
        cursos = [dict(zip(columnas, row)) for row in rows]

        cur.close()
        conn.close()

        return jsonify(cursos), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------------------
# 3️⃣ ACTUALIZAR CURSO - PUT
# ----------------------------------------
@app.route('/cursos/<int:id_curso>', methods=['PUT'])
def actualizar_curso(id_curso):
    data = request.json

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        sql = """
            UPDATE cursos
            SET nombre_curso=%s, codigo=%s, nivel_grado=%s,
                capacidad_max=%s, profesor_asignado=%s, fecha_registro=%s
            WHERE id_curso=%s;
        """

        cur.execute(sql, (
            data.get("nombre_curso"),
            data.get("codigo"),
            data.get("nivel_grado"),
            data.get("capacidad_max"),
            data.get("profesor_asignado"),
            data.get("fecha_registro"),
            id_curso
        ))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"mensaje": "Curso actualizado correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------------------
# 4️⃣ ELIMINAR CURSO - DELETE
# ----------------------------------------
@app.route('/cursos/<int:id_curso>', methods=['DELETE'])
def eliminar_curso(id_curso):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM cursos WHERE id_curso=%s;", (id_curso,))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"mensaje": "Curso eliminado correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Ejecutar servidor
if __name__ == '__main__':
    app.run(debug=True)
=======

DB_HOST = "127.0.0.1"

DB_PORT = "5432"



# ============================================

# FUNCIÓN DE CONEXIÓN

# ============================================

def get_db_connection():

  try:

    conn = psycopg2.connect(

      dbname=DB_NAME,

      user=DB_USER,

      password=DB_PASS,

      host=DB_HOST,

      port=DB_PORT,

      cursor_factory=RealDictCursor

    )

    return conn

  except psycopg2.Error as e:

    print("❌ Error de conexión:", e)

    return None





# ============================================

# ENDPOINT PARA REGISTRAR COLEGIOS

# ============================================

@app.route("/colegios", methods=["POST"])

def registrar_colegio():

  data = request.get_json()



  campos_requeridos = [

    "codigo_modular_r",

    "nombre_colegio",

    "tipo_gestion",

    "direccion_comple",

    "departamento",

    "provincia",

    "distrito",

    "telefono",

    "email_institucion",

    "nombre_director"

  ]



  # Verificar campos faltantes

  campos_faltantes = [c for c in campos_requeridos if c not in data]

  if campos_faltantes:

    return jsonify({

      "error": f"Faltan campos obligatorios: {', '.join(campos_faltantes)}"

    }), 400



  try:

    conn = get_db_connection()

    if conn is None:

      return jsonify({"error": "No se pudo conectar a la base de datos"}), 500



    cur = conn.cursor()



    query = """

      INSERT INTO colegios (

        codigo_modular_r,

        nombre_colegio,

        tipo_gestion,

        direccion_comple,

        departamento,

        provincia,

        distrito,

        telefono,

        email_institucion,

        nombre_director

      )

      VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)

      RETURNING id_colegio;

    """



    valores = (

      data["codigo_modular_r"],

      data["nombre_colegio"],

      data["tipo_gestion"],

      data["direccion_comple"],

      data["departamento"],

      data["provincia"],

      data["distrito"],

      data["telefono"],

      data["email_institucion"],

      data["nombre_director"]

    )



    cur.execute(query, valores)

    nuevo_id = cur.fetchone()["id_colegio"]

    conn.commit()



    cur.close()

    conn.close()



    return jsonify({

      "mensaje": "Colegio registrado exitosamente",

      "id_colegio": nuevo_id

    }), 201



  except Exception as e:

    print("❌ Error al insertar:", e)

    return jsonify({"error": "Error al registrar el colegio"}), 500





# ============================================

# INICIO DE LA APP

# ============================================

if __name__ == "__main__":

  app.run(debug=True)
  
>>>>>>> 23c887774217ac5201af5b1bfdb84778578374d4
