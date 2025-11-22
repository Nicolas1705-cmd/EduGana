# app.py (SOLUCIONADO para GET)
import random
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS 
import psycopg2
from psycopg2.extras import RealDictCursor

# Asume que configbd.py y get_db_connection están correctamente definidos
from configbd import get_db_connection 


# --- CONFIGURACIÓN DE FLASK ---
app = Flask(__name__)
# Habilitar CORS es crucial si el HTML y Flask están en diferentes puertos/hosts
CORS(app) 

# --- FUNCIÓN DE UTILIDAD (Generación de ID) ---
def generar_id_colegio():
    """Genera un ID único para el colegio (simulación)."""
    year = datetime.now().year
    random_num = random.randint(1000, 9999)
    return f"CLG-{year}-{random_num}"

# --- FUNCIÓN DE REGISTRO ADAPTADA A GET ---
def registrar_colegio():
    
    # 1. OBTENER LOS DATOS DE LA URL (query parameters)
    # ESTO EVITA EL ERROR 415, YA QUE NO ESPERA JSON EN EL CUERPO
    data = request.args

    # 2. Validar campos requeridos
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

    new_id = generar_id_colegio() 
    conn = None 
    
    try:
        conn = get_db_connection()
        # ... (Tu lógica de conexión a DB) ...

        cur = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            INSERT INTO colegios (
                id_colegio, codigo_modular_r, nombre_colegio, tipo_gestion,
                direccion_comple, departamento, provincia, distrito,
                telefono, email_institucion, nombre_director
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_colegio;
        """

        # Preparamos los valores directamente desde request.args
        valores = (
            new_id,
            data.get("codigo_modular_r"),
            data.get("nombre_colegio"),
            data.get("tipo_gestion"),
            data.get("direccion_comple"),
            data.get("departamento"),
            data.get("provincia"),
            data.get("distrito"),
            data.get("telefono") or None, 
            data.get("email_institucion"),
            data.get("nombre_director")
        )

        cur.execute(query, valores)
        nuevo = cur.fetchone()
        conn.commit()

        return jsonify({
            "mensaje": "Colegio registrado exitosamente usando GET",
            "id_colegio": nuevo["id_colegio"]
        }), 201

    except psycopg2.IntegrityError as e:
        if conn: conn.rollback(); conn.close()
        return jsonify({"error": "Error: El Código Modular/RUC o ID ya existe."}), 409
    
    except Exception as e:
        if conn: conn.close()
        print("❌ Error general al registrar:", e)
        return jsonify({"error": "Error interno del servidor", "detalles": str(e)}), 500

# --- MAPEO DE LA RUTA (APIS) ---
# ESTO ES CRUCIAL: El método mapeado DEBE ser GET
app.add_url_rule(
    '/addColegio',             
    view_func=registrar_colegio, 
    methods=['GET']         
)

# --- EJECUCIÓN DEL SERVIDOR ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)