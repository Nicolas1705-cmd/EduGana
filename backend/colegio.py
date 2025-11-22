from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import psycopg2
from configbd import get_db_connection
from psycopg2.extras import RealDictCursor


def registrar_colegio():

    data = request.get_json()

    # Ahora SOLO id_colegio es obligatorio
    campos_requeridos = ["id_colegio"]

    campos_faltantes = [c for c in campos_requeridos if c not in data]

    if campos_faltantes:
        return jsonify({
            "error": f"Faltan campos obligatorios: {', '.join(campos_faltantes)}"
        }), 400

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Todos los demás campos ahora pueden ser NULL
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
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
            RETURNING id_colegio;
        """

        valores = (
            data.get("id_colegio"),
            data.get("codigo_modular_r"),
            data.get("nombre_colegio"),
            data.get("tipo_gestion"),
            data.get("direccion_comple"),
            data.get("departamento"),
            data.get("provincia"),
            data.get("distrito"),
            data.get("telefono"),
            data.get("email_institucion"),
            data.get("nombre_director")
        )

        cur.execute(query, valores)
        nuevo = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "mensaje": "Colegio registrado exitosamente",
            "id_colegio": nuevo["id_colegio"]
        }), 201

    except Exception as e:
        print("❌ Error al insertar:", e)
        return jsonify({"error": "Error al registrar el colegio"}), 500
