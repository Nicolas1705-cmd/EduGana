# app.py

from flask import Flask, jsonify, request
from flask_cors import CORS 
# Aunque no los uses en este endpoint, los mantengo por tu código original
from flask_bcrypt import Bcrypt 
from flask_jwt_extended import JWTManager, create_access_token 

import psycopg2
from psycopg2.extras import RealDictCursor

import random
from datetime import datetime

# Asume que configbd.py está en el mismo directorio
from configbd import get_db_connection 


# --- CONFIGURACIÓN DE FLASK ---
app = Flask(__name__)
# Habilitar CORS para permitir la conexión desde el frontend
CORS(app) 

# Inicializar componentes (necesarios si usas otros endpoints de auth)
app.config["JWT_SECRET_KEY"] = "super-secreto-cambiar-en-produccion" 
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# --- FUNCIÓN DE UTILIDAD (Simulación de ID) ---
def generar_id_colegio():
    """Genera un ID único para el colegio (simulación si no usas SERIAL en DB)."""
    year = datetime.now().year
    random_num = random.randint(1000, 9999)
    return f"CLG-{year}-{random_num}"

# --- FUNCIÓN DE REGISTRO CORREGIDA ---
def registrar_colegio():
    
    data = request.get_json()

    # 1. Validar campos requeridos
    campos_requeridos = [
        "codigo_modular_r", "nombre_colegio", "tipo_gestion", 
        "direccion_comple", "departamento", "provincia", 
        "distrito", "email_institucion", "nombre_director"
    ]

    campos_faltantes = [c for c in campos_requeridos if not data.get(c)]

    if campos_faltantes:
        return jsonify({
            "error": "Faltan campos obligatorios",
            "detalles": f"Los campos requeridos son: {', '.join(campos_faltantes)}."
        }), 400

    # 2. Generar ID en el backend
    new_id = generar_id_colegio() 

    conn = None # Inicializar conexión a None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

        cur = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            INSERT INTO colegios (
                id_colegio, codigo_modular_r, nombre_colegio, tipo_gestion,
                direccion_comple, departamento, provincia, distrito,
                telefono, email_institucion, nombre_director
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id_colegio;
        """

        # Preparamos los valores.
        valores = (
            new_id,
            data.get("codigo_modular_r"),
            data.get("nombre_colegio"),
            data.get("tipo_gestion"),
            data.get("direccion_comple"),
            data.get("departamento"),
            data.get("provincia"),
            data.get("distrito"),
            data.get("telefono") or None, # String vacío se convierte a NULL
            data.get("email_institucion"),
            data.get("nombre_director")
        )

        cur.execute(query, valores)
        nuevo = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "mensaje": "Colegio registrado exitosamente",
            "id_colegio": nuevo["id_colegio"]
        }), 201

    except psycopg2.IntegrityError as e:
        # Manejar error de duplicidad (ej. código modular/RUC ya existe)
        if conn:
            conn.rollback()
            conn.close()
        print("❌ Error de integridad de DB:", e)
        return jsonify({"error": "Error: El Código Modular/RUC o ID ya existe."}), 409
    
    except Exception as e:
        # Error general
        if conn:
            conn.close()
        print("❌ Error general al registrar:", e)
        return jsonify({"error": "Error interno del servidor", "detalles": str(e)}), 500

# --- MAPEO DE LA RUTA CORREGIDO (APIS) ---
app.add_url_rule(
    '/colegios',             # La URL debe coincidir con URL_BACKEND en JS
    view_func=registrar_colegio, # Usamos la función corregida
    methods=['POST']         # Debe ser POST para recibir datos
)

# --- EJECUCIÓN DEL SERVIDOR ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)