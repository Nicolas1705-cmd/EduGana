from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
# Asegúrate de que 'configbd' esté accesible y contenga la función 'get_db_connection'
from configbd import get_db_connection 


def obtener_asistencias():
    """
    Consulta y devuelve todas las asistencias registradas en la base de datos,
    ordenadas por fecha y hora de entrada de forma descendente.
    """
    try:
        # 1. Obtener la conexión a la base de datos
        conn = get_db_connection()
        # Usamos RealDictCursor para obtener resultados como diccionarios, 
        # lo que facilita la conversión a JSON.
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 2. Ejecutar la consulta SQL
        cur.execute("""
            SELECT 
                id,
                estudiante_id,
                nombre_estudiante,
                fecha,
                -- Usamos CASE para mostrar 'Presente' o 'Ausente' en lugar de true/false
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


