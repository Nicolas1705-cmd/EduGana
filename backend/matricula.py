from flask import Flask, request, jsonify
import psycopg2
# Importar la función de conexión desde donde la tengas definida
from configbd import get_db_connection 
# Asumo que tu archivo con get_db_connection se llama database_config.py
# Si la función está en el mismo archivo, puedes omitir la línea de importación.


# --- Rutas de la API ---

# @app.route('/matricula/registrar', methods=['POST'])
def registrar_matricula():
    """
    Ruta para registrar un nuevo alumno en la tabla matriculaalumno.
    Acepta datos JSON por método POST.
    """
    # 1. Obtener los datos del cuerpo de la petición (JSON)
    data = request.get_json()

    # 2. Validar que se recibieron datos
    if not data:
        return jsonify({"error": "Datos no recibidos. Asegúrate de enviar un JSON."}, 400)

    # 3. Extraer y validar campos obligatorios
    # Nota: Los nombres de las claves deben coincidir exactamente con los de tu JSON de entrada.
    try:
        nombre_completo = data['Nombre_Completo']
        documento_identidad = data['Documento_de_Identidad']
        nombre_padre_tutor = data['Nombre_del_Padre/Tutor']
        
        # Campos opcionales (usar .get para evitar KeyError)
        genero = data.get('Genero')
        telefono_contacto = data.get('Telefono_de_Contacto')
        correo_electronico = data.get('Correo_Electronico')
        colegio = data.get('Colegio')
        fecha_nacimiento = data.get('Fecha_de_Nacimiento')

    except KeyError as e:
        # Devuelve un error si falta un campo requerido
        return jsonify({"error": f"Falta el campo obligatorio: {e}"}, 400)

    # 4. Establecer conexión a la BD
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo establecer conexión con la base de datos."}, 500)

    # 5. Ejecutar la inserción
    try:
        cursor = conn.cursor()
        
        # Consulta SQL de inserción
        # Los nombres de las columnas en la consulta deben coincidir **exactamente** con la definición de tu tabla.
        # Se usan %s para evitar inyección SQL (parametrización).
        insert_query = """
        INSERT INTO public.matriculaalumno (
            "Nombre_Completo", "Genero", "Documento_de_Identidad", 
            "Nombre_del_Padre/Tutor", "Telefono_de_Contacto", "Correo_Electronico", 
            "Colegio", "Fecha_de_Nacimiento"
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        
        # Tupla de valores para la consulta
        valores = (
            nombre_completo, genero, documento_identidad, 
            nombre_padre_tutor, telefono_contacto, correo_electronico, 
            colegio, fecha_nacimiento
        )
        
        cursor.execute(insert_query, valores)
        
        # Confirmar los cambios en la BD
        conn.commit()

        # Respuesta de éxito
        return jsonify({
            "mensaje": "Alumno registrado exitosamente.",
            "documento": documento_identidad
        }), 201 # 201 Created

    except psycopg2.Error as db_error:
        # Revertir si hay error
        conn.rollback()
        print(f"Error de base de datos: {db_error}")
        return jsonify({
            "error": "Error al registrar en la base de datos.",
            "detalle": str(db_error)
        }), 500

    finally:
        # Cerrar el cursor y la conexión
        if cursor:
            cursor.close()
        if conn:
            conn.close()