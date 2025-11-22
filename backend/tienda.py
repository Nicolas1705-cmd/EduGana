from flask import request, jsonify
import psycopg2
from configbd import get_db_connection


# @app.route('/tienda/registrar', methods=['POST'])
def registrar_tienda():
    """
    Ruta para registrar una nueva tienda en la tabla tiendas.
    Acepta datos JSON por método POST.
    """

    # 1. Obtener datos del cuerpo (JSON)
    data = request.get_json()

    # 2. Validar datos
    if not data:
        return jsonify({"error": "Datos no recibidos. Asegúrate de enviar un JSON válido."}), 400

    # 3. Extraer campos obligatorios EXACTOS como tu tabla
    try:
        nombretienda = data["nombretienda"]
        correoelectronico = data["correoelectronico"]
        contrasena = data["contrasena"]
        telefono = data["telefono"]
        ruc = data["ruc"]
        regimen = data["regimen"]
        departamento = data["departamento"]
        provincia = data["provincia"]
        distrito = data["distrito"]
        categoria = data["categoria"]
        pais = data["pais"]
        terminos = data["terminos"]   # boolean obligatorio

        # Campo opcional
        logo = data.get("logo")  # text opcional

    except KeyError as e:
        return jsonify({"error": f"Falta el campo obligatorio: {e}"}), 400

    # 4. Conexión BD
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo establecer conexión con la base de datos."}), 500

    # 5. Insertar en BD
    try:
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO public.tiendas (
            nombretienda, correoelectronico, contrasena, telefono,
            ruc, regimen, departamento, provincia, distrito,
            categoria, logo, pais, terminos
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """

        valores = (
            nombretienda, correoelectronico, contrasena, telefono,
            ruc, regimen, departamento, provincia, distrito,
            categoria, logo, pais, terminos
        )

        cursor.execute(insert_query, valores)
        nuevo_id = cursor.fetchone()[0]

        conn.commit()

        return jsonify({
            "mensaje": "Tienda registrada exitosamente.",
            "id_tienda": nuevo_id
        }), 201

    except psycopg2.Error as db_error:
        conn.rollback()
        print(f"Error de base de datos: {db_error}")
        return jsonify({
            "error": "Error al registrar la tienda.",
            "detalle": str(db_error)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
