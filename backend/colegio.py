from flask import Flask, jsonify, request

from flask_bcrypt import Bcrypt

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

DB_NAME = "edugana_db"

DB_USER = "postgres"

DB_PASS = "System.2025*"

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
  