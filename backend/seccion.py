# seccion.py (Versión CORREGIDA para INSERT con método GET)

from flask import request, jsonify # Importamos 'request' para leer los parámetros GET
# Nota: psycopg2.extras.RealDictCursor no es necesario para un INSERT, pero se mantiene si se usa en otro lado
import psycopg2.extras 
from configbd import get_db_connection
import psycopg2 # Necesario para manejar errores específicos de PostgreSQL

def addSeccion():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500

    cur = None
    try:
        # 1. Obtener los datos de los parámetros de consulta de la URL (request.args)
        # El frontend envía 'session_id' y 'description'. Mapeamos a las columnas de la BD.
        idseccion_str = request.args.get('session_id')
        nombre_seccion = request.args.get('description')
        
        # 2. Validación de datos
        if not idseccion_str or not nombre_seccion:
            return jsonify({
                "mensaje": "Datos incompletos. Se esperan 'session_id' y 'description' en los parámetros GET."
            }), 400
        
        # Convertir idseccion a entero (si es necesario)
        try:
            idseccion = int(idseccion_str)
        except ValueError:
            return jsonify({"mensaje": "El ID de la sección (session_id) debe ser un número entero válido."}), 400

        # Usamos un cursor simple ya que solo haremos un INSERT
        cur = conn.cursor()
        
        # 3. Ejecutar la sentencia INSERT
        # La primera columna es 'idseccion' (integer) y la segunda es 'seccion' (character varying)
        insert_query = """
        INSERT INTO seccion (idseccion, seccion) 
        VALUES (%s, %s);
        """
        cur.execute(insert_query, (idseccion, nombre_seccion))
        
        conn.commit() # Confirmar la transacción
        
        # 4. Retornar una respuesta de éxito (200 OK es típico para GET)
        return jsonify({
            "mensaje": f"Sección registrada correctamente por GET: ID={idseccion}, Nombre='{nombre_seccion}'"
        }), 200 

    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({
            "mensaje": f"Error de integridad: El ID de la sección ({idseccion}) probablemente ya existe o viola una restricción.",
            "error": "IntegrityError"
        }), 400
    except psycopg2.Error as e:
        conn.rollback() # Revertir la transacción si hay un error en la BD
        return jsonify({"mensaje": "Error al registrar la sección en la base de datos", "error": str(e)}), 500
    except Exception as e:
        return jsonify({"mensaje": "Error interno del servidor", "error": str(e)}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()