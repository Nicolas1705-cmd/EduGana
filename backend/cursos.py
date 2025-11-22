from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from configbd import get_db_connection  

def registrar_curso(data):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        sql = """
            INSERT INTO cursos 
            (nombre_curso, codigo, nivel_grado, capacidad_max, profesor_asignado, descripcion)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_curso;
        """

        cur.execute(sql, (
            data["nombre_curso"],
            data["codigo"],
            data["nivel_grado"],
            data["capacidad_max"],
            data["profesor_asignado"],
            data.get("descripcion", "")
        ))

        new_id = cur.fetchone()[0]
        conn.commit()

        cur.close()
        conn.close()

        return {"mensaje": "Curso registrado", "id_curso": new_id}

    except Exception as e:
        return {"error": str(e)}
