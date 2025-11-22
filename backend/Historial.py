from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from configbd import get_db_connection 


# ======================================================
#   📌 Obtener historial completo
# ======================================================
def obtener_asistencias():
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT 
                id,
                estudiante_id,
                nombre_estudiante,
                fecha,
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

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
