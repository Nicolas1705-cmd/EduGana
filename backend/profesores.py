from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
import psycopg2
from psycopg2.extras import RealDictCursor
from configbd import get_db_connection 



def listar_profesores():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "No se pudo conectar a la base de datos"}), 500

    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                id_profesor,
                dni,
                nombre_completo,
                fecha_nacimiento,
                genero,
                email_personal,
                telefono,
                direccion_residencia,
                titulo_especialidad,
            FROM profesores
            ORDER BY id_profesor ASC;
        """)

        data = cur.fetchall()
        return jsonify(data), 200

    except Exception as e:
        print("ERROR BD:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()




def agregar_profesor():
    data = request.get_json()

    required = [
        "dni", "nombre_completo", "fecha_nacimiento",
        "genero", "email_personal", "telefono",
        "direccion_residencia", "titulo_especialidad"
    ]

    for field in required:
        if field not in data:
            return jsonify({"message": f"Falta el campo obligatorio: {field}"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "No se pudo conectar a la base de datos"}), 500

    try:
        cur = conn.cursor()

        sql = """
            INSERT INTO profesores (
                dni, nombre_completo, fecha_nacimiento,
                genero, email_personal, telefono,
                direccion_residencia, titulo_especialidad,
                id_colegio_asignado
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id_profesor;
        """

        values = (
            data["dni"],
            data["nombre_completo"],
            data["fecha_nacimiento"],
            data["genero"],
            data["email_personal"],
            data["telefono"],
            data["direccion_residencia"],
            data["titulo_especialidad"],
            data.get("id_colegio_asignado")  # puede ser null
        )

        cur.execute(sql, values)
        new_id = cur.fetchone()["id_profesor"]

        conn.commit()

        return jsonify({"message": "Profesor registrado", "id": new_id}), 201

    except Exception as e:
        conn.rollback()
        print("ERROR INSERT:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()
