from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from configbd import get_db_connection

# Nombre de la tabla
TABLE_NAME = "public.registro_asistencia"

# ============================
# POST: REGISTRAR ASISTENCIA
# ============================
def registrar_asistencia():
    """Registra una nueva asistencia en la base de datos según el esquema de la imagen."""
    try:
        data = request.get_json()

        # Los campos de la tabla en la imagen son: dni, fecha, hora, estado_asistencia, id_registro
        
        # Campos de entrada necesarios
        id_registro = data.get("id_registro") # Asumimos que la aplicación provee el ID
        dni = data.get("dni")
        fecha = data.get("fecha")
        hora = data.get("hora") # Unificamos hora_entrada/salida en solo 'hora'
        estado_asistencia = data.get("estado_asistencia")

        # Eliminamos: nombres, apellidos, hora_entrada, hora_salida, observacion
        
        # Validar campos obligatorios (NOT NULL en la imagen: dni, fecha, estado_asistencia)
        # NOTA: Incluyo id_registro en la validación si la aplicación debe proporcionarlo
        if not id_registro or not dni or not fecha or not estado_asistencia:
            return jsonify({"mensaje": "Faltan campos obligatorios (id_registro, dni, fecha, estado_asistencia)"}), 400

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # La consulta solo incluye las 5 columnas presentes en la imagen
        cur.execute(f"""
            INSERT INTO {TABLE_NAME} (
                id_registro, dni, fecha, hora, estado_asistencia
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_registro;
        """, (
            id_registro, dni, fecha, hora, estado_asistencia
        ))
        
        conn.commit()
        # Obtener el id_registro retornado
        new_id = cur.fetchone()["id_registro"] 

        cur.close()
        conn.close()

        return jsonify({
            "mensaje": "Asistencia registrada correctamente",
            "id_registro": new_id
        }), 201

    except Exception as e:
        print(f"Error al registrar asistencia: {e}")
        return jsonify({"mensaje": "Error interno del servidor"}), 500

# ============================
# GET: LISTAR ASISTENCIAS
# ============================

def obtener_asistencias():
    """Devuelve la lista completa de asistencias."""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor) 

        # El nombre de la tabla sigue siendo el mismo, pero los datos devueltos serán diferentes
        cur.execute(f"SELECT * FROM {TABLE_NAME} ORDER BY fecha DESC, hora DESC;")
        asistencias = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(asistencias), 200

    except Exception as e:
        print(f"Error al obtener asistencias: {e}")
        return jsonify({"mensaje": "Error interno del servidor al obtener asistencias"}), 500