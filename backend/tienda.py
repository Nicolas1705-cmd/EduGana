from flask import request, jsonify
from flask_bcrypt import Bcrypt
from configbd import get_db_connection

bcrypt = Bcrypt()


##############################
# AGREGAR TIENDA
##############################

def agregar_tienda():
    """
    REGISTRAR UNA TIENDA
    JSON esperado:
    {
        "nombretienda": "",
        "correoelectronico": "",
        "contrasena": "",
        "telefono": "",
        "ruc": "",
        "regimen": "",
        "departamento": "",
        "provincia": "",
        "distrito": "",
        "categoria": "",
        "logo": "",
        "pais": "",
        "terminos": true
    }
    """
    try:
        data = request.json

        campos_obligatorios = [
            "nombretienda", "correoelectronico", "contrasena", "telefono",
            "ruc", "regimen", "departamento", "provincia", "distrito",
            "categoria", "pais", "terminos"
        ]

        for campo in campos_obligatorios:
            if campo not in data:
                return jsonify({"error": f"El campo '{campo}' es obligatorio"}), 400

        # encriptar contraseña
        hashed_pass = bcrypt.generate_password_hash(data["contrasena"]).decode("utf-8")

        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Error conectando a la BD"}), 500

        cursor = conn.cursor()

        query = """
            INSERT INTO tiendas (
                nombretienda, correoelectronico, contrasena, telefono,
                ruc, regimen, departamento, provincia, distrito,
                categoria, logo, pais, terminos
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """

        cursor.execute(query, (
            data["nombretienda"],
            data["correoelectronico"],
            hashed_pass,
            data["telefono"],
            data["ruc"],
            data["regimen"],
            data["departamento"],
            data["provincia"],
            data["distrito"],
            data["categoria"],
            data.get("logo"),
            data["pais"],
            data["terminos"]
        ))

        nuevo_id = cursor.fetchone()[0]
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "mensaje": "Tienda registrada exitosamente",
            "id_tienda": nuevo_id
        }), 201

    except Exception as e:
        import traceback
        print("Error:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500



##############################
# LISTAR TIENDAS
##############################

def listar_tiendas():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Error conectando a la BD"}), 500

        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nombretienda, correoelectronico, telefono, ruc,
                   regimen, departamento, provincia, distrito,
                   categoria, logo, pais, terminos
            FROM tiendas
            ORDER BY id DESC
        """)

        filas = cursor.fetchall()

        cursor.close()
        conn.close()

        tiendas = []
        for t in filas:
            tiendas.append({
                "id": t[0],
                "nombretienda": t[1],
                "correoelectronico": t[2],
                "telefono": t[3],
                "ruc": t[4],
                "regimen": t[5],
                "departamento": t[6],
                "provincia": t[7],
                "distrito": t[8],
                "categoria": t[9],
                "logo": t[10],
                "pais": t[11],
                "terminos": t[12]
            })

        return jsonify({
            "success": True,
            "total": len(tiendas),
            "tiendas": tiendas
        }), 200

    except Exception as e:
        import traceback
        print("Error:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500



##############################
# OBTENER TIENDA POR ID
##############################

def obtener_tienda(id_tienda):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Error conectando a la BD"}), 500

        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nombretienda, correoelectronico, telefono, ruc,
                   regimen, departamento, provincia, distrito,
                   categoria, logo, pais, terminos
            FROM tiendas
            WHERE id = %s
        """, (id_tienda,))

        t = cursor.fetchone()

        cursor.close()
        conn.close()

        if not t:
            return jsonify({"error": f"No existe tienda con ID {id_tienda}"}), 404

        return jsonify({
            "success": True,
            "tienda": {
                "id": t[0],
                "nombretienda": t[1],
                "correoelectronico": t[2],
                "telefono": t[3],
                "ruc": t[4],
                "regimen": t[5],
                "departamento": t[6],
                "provincia": t[7],
                "distrito": t[8],
                "categoria": t[9],
                "logo": t[10],
                "pais": t[11],
                "terminos": t[12]
            }
        }), 200

    except Exception as e:
        import traceback
        print("Error:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500



##############################
# ACTUALIZAR TIENDA
##############################

def actualizar_tienda(id_tienda):
    try:
        data = request.json

        campos = [
            "nombretienda", "correoelectronico", "telefono", "ruc",
            "regimen", "departamento", "provincia", "distrito",
            "categoria", "logo", "pais"
        ]

        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Error conectando a la BD"}), 500

        cursor = conn.cursor()

        set_sql = []
        params = []

        for campo in campos:
            if campo in data:
                set_sql.append(f"{campo} = %s")
                params.append(data[campo])

        if "contrasena" in data:
            nueva_pass = bcrypt.generate_password_hash(data["contrasena"]).decode("utf-8")
            set_sql.append("contrasena = %s")
            params.append(nueva_pass)

        if not set_sql:
            return jsonify({"error": "No hay campos para actualizar"}), 400

        params.append(id_tienda)

        query = f"UPDATE tiendas SET {', '.join(set_sql)} WHERE id = %s"

        cursor.execute(query, tuple(params))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "mensaje": "Tienda actualizada correctamente"
        }), 200

    except Exception as e:
        import traceback
        print("Error:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500



##############################
# ELIMINAR TIENDA
##############################

def eliminar_tienda(id_tienda):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Error conectando a la BD"}), 500

        cursor = conn.cursor()

        cursor.execute("SELECT id FROM tiendas WHERE id = %s", (id_tienda,))
        existe = cursor.fetchone()

        if not existe:
            return jsonify({"error": f"No existe tienda con ID {id_tienda}"}), 404

        cursor.execute("DELETE FROM tiendas WHERE id = %s", (id_tienda,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"success": True, "mensaje": "Tienda eliminada"}), 200

    except Exception as e:
        import traceback
        print("Error:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500
