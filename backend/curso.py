from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from configbd import get_db_connection  




# ======================================
# API: REGISTRAR CURSO (POST)
# ======================================
def registrar_curso():
    data = request.json

    campos_obligatorios = [
        "nombre_curso", "codigo", "nivel_grado",
        "capacidad_max", "profesor_asignado"
    ]

    # Validar obligatorios
    for campo in campos_obligatorios:
        if campo not in data or str(data[campo]).strip() == "":
            return jsonify({"error": f"El campo '{campo}' es obligatorio."}), 400

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

        return jsonify({"mensaje": "Curso registrado correctamente", "id_curso": new_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500