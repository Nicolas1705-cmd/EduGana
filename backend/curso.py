from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
from configbd import get_db_connection


def registrar_inscripcion():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON data"}), 400

    nombre_completo = data.get('nombre_completo')
    nombre_curso = data.get('nombre_curso')

    # Validación correcta
    if not all([nombre_completo, nombre_curso]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        insert_query = sql.SQL("""
            INSERT INTO Curso (nombre_completo, nombre_curso)
            VALUES (%s, %s)
            RETURNING id_inscripcion;
        """)

        cur.execute(insert_query, (nombre_completo, nombre_curso))
        new_id = cur.fetchone()
        conn.commit()
        cur.close()

        return jsonify({
            "message": "Inscripción registrada exitosamente.",
            "id_inscripcion": new_id["id_inscripcion"],
            "datos_registrados": data
        }), 201

    except psycopg2.OperationalError:
        return jsonify({"error": "Error de conexión con la base de datos"}), 500

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"error": "Error SQL", "detail": str(e)}), 500

    finally:
        if conn:
            conn.close()
