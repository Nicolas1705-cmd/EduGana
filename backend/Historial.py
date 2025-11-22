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
            -- Ordenar por fecha más reciente primero, y luego por hora de entrada más reciente
            ORDER BY fecha DESC, hora_entrada DESC
        """)
        # 3. Obtener todos los resultados
        data = cur.fetchall()

        # 4. Cerrar cursor y conexión
        cur.close()
        conn.close()

        # 5. Devolver los datos como una respuesta JSON con código 200 (OK)
        return jsonify(data), 200

    except Exception as e:
        # 6. Manejar errores de conexión o consulta
        print(f"Error al obtener asistencias: {e}")
        return jsonify({"error": "Error interno del servidor", "detalle": str(e)}), 500

# --- Rutas de la API ---

def historial_asistencias():
    """
    Ruta para acceder al historial de asistencias.
    """
    return obtener_asistencias()

# --- Ejecución de la Aplicación ---

if __name__ == '__main__':
    # Ejecuta la aplicación en modo debug para desarrollo
    app.run(debug=True, port=5000)