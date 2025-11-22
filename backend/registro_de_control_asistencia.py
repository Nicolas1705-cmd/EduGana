from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from configbd import get_db_connection

# ============================
# POST: REGISTRAR ASISTENCIA
# ============================
def registrar_asistencia():
    try:
        data = request.get_json()

        # Los campos de la tabla son: dni, nombres, apellidos, fecha, hora_entrada, hora_salida, estado_asistencia, observacion

        dni = data.get("dni")
        nombres = data.get("nombres")  # Usamos 'nombres' directamente
        apellidos = data.get("apellidos")  # Usamos 'apellidos' directamente
        fecha = data.get("fecha")
        estado_asistencia = data.get("estado_asistencia")
        hora_entrada = data.get("hora_entrada")
        # hora_salida se deja como NULL por defecto si no se proporciona
        hora_salida = data.get("hora_salida")
        observacion = data.get("observacion") # Cambiamos 'observaciones' a 'observacion'

        # Validamos los campos NOT NULL de la tabla
        # La tabla exige: id_registro (autoincremental, no lo pedimos), dni, nombres, apellidos, fecha, estado_asistencia
        if not dni or not nombres or not apellidos or not fecha or not estado_asistencia:
            return jsonify({"mensaje": "Faltan campos obligatorios (dni, nombres, apellidos, fecha, estado_asistencia)"}), 400

        conn = get_db_connection()
        # Nota: Usar RealDictCursor aquí permite que fetchone() devuelva un diccionario, lo cual simplifica la obtención del id_registro.
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 1. Cambiamos el nombre de la tabla de 'asistencias' a 'registro_asistencia'
        # 2. Cambiamos los nombres de las columnas a los de la tabla 'registro_asistencia'
        # 3. Ajustamos el número de %s (8 columnas en total, ya que id_registro es clave primaria y probablemente autoincremental/serial, no lo incluimos aquí)
        cur.execute("""
            INSERT INTO public.registro_asistencia (
                dni, nombres, apellidos, fecha,
                hora_entrada, hora_salida, estado_asistencia, observacion
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_registro;
        """, (
            dni, nombres, apellidos, fecha,
            hora_entrada, hora_salida, estado_asistencia, observacion
        ))
        
        conn.commit()
        # 4. Cambiamos 'id' por 'id_registro' al obtener el ID devuelto
        new_id = cur.fetchone()["id_registro"] 


        cur.close()
        conn.close()

        return jsonify({
            "mensaje": "Asistencia registrada correctamente",
            "id_registro": new_id
        }), 201

    except Exception as e:
        print("Error:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500


# ============================
# GET: LISTAR ASISTENCIAS
# ============================

def obtener_asistencias():
    try:
        # Usamos RealDictCursor para que los resultados se devuelvan como una lista de diccionarios (JSON más limpio)
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor) 

        # Cambiamos el nombre de la tabla de 'asistencias' a 'public.registro_asistencia'
        cur.execute("SELECT * FROM public.registro_asistencia ORDER BY fecha DESC;")
        asistencia = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(asistencia), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"mensaje": "Error interno del servidor"}), 500