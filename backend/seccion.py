# asistencia.py
from flask import Flask, request, jsonify
import psycopg2.extras # Importamos para obtener resultados como diccionarios
from configbd import get_db_connection # ⬅️ Importación de tu archivo de configuración

def bienvenido():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500

    cur = None
    try:
        # Usamos RealDictCursor para que cada fila se devuelva como un diccionario (JSON)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) 
        cur.execute("SELECT * FROM asistencias ")
        asistencias = cur.fetchall()
        
        return jsonify(asistencias), 200

    except psycopg2.Error as e:
        return jsonify({"mensaje": "Error al listar asistencias", "error": str(e)}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()




