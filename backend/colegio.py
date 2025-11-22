from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import psycopg2
from configbd import get_db_connection
from psycopg2.extras import RealDictCursor


def registrar_colegio():

    data = request.get_json()

    campos_requeridos = [
        "id_colegio",
        "codigo_modular_r",
        "nombre_colegio",
        "tipo_gestion",
        "direccion_comple",
        "departamento",
        "provincia",
        "distrito",
        "telefono",
        "email_institucion",
        "nombre_director"
    ]

    campos_faltantes = [c for c in campos_requeridos if c not in data]

    if campos_faltantes:
        return jsonify({
            "error": f"Faltan campos obligatorios: {', '.join(campos_faltantes)}"
        }), 400

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

        cur = conn.cursor()

        query = """
            INSERT INTO colegios (
                id_colegio,
                codigo_modular_r,
                nombre_colegio,
                tipo_gestion,
                direccion_comple,
                departamento,
                provincia,
                distrito,
                telefono,
                email_institucion,
                nombre_director
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id_colegio;
        """

        valores = (
            data["id_colegio"],
            data["codigo_modular_r"],
            data["nombre_colegio"],
            data["tipo_gestion"],
            data["direccion_comple"],
            data["departamento"],
            data["provincia"],
            data["distrito"],
            data["telefono"],
            data["email_institucion"],
            data["nombre_director"]
        )

        cur.execute(query, valores)
        nuevo_id = cur.fetchone()["id_colegio"]

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            "mensaje": "Colegio registrado exitosamente",
            "id_colegio": nuevo_id
        }), 201

    except Exception as e:
        print("❌ Error al insertar:", e)
        return jsonify({"error": "Error al registrar el colegio"}), 500
