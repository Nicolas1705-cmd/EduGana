import json
from flask import Flask, request, jsonify # Importamos Flask aquí
from psycopg2 import Error
from configbd import get_db_connection # Solo necesitamos la función de conexión

# Importamos Bcrypt y lo inicializamos más abajo
from flask_bcrypt import Bcrypt 


# ---------------------------------------------------------------------
# 1. INICIALIZACIÓN DE LA APLICACIÓN
# ---------------------------------------------------------------------
app = Flask(__name__)
# Inicializa Bcrypt con la aplicación
# Si necesitas usar bcrypt más adelante (ej. en una ruta de registro), 
# inicialízalo aquí o configúralo con un patrón de factoría.
bcrypt = Bcrypt(app)


# ---------------------------------------------------------------------
# Definición de las Rutas de la API para la gestión de Cursos (CRUD Básico)
# ---------------------------------------------------------------------

@app.route('/cursos', methods=['POST'])
def agregar_curso():
    """
    Ruta para agregar un nuevo curso a la base de datos.
    Recibe los datos del curso en formato JSON.
    """
    if not request.is_json:
        return jsonify({"mensaje": "El cuerpo de la solicitud debe ser JSON"}), 400

    datos = request.get_json()

    # Mapeo de campos basado en la definición de la tabla Curso:
    # Codigo_Curso, Descripcion, Duracion_horas, Nivel, profesor_nombre,
    # profesor_email, fecha_inicio, fecha_fin, cupo_maximo, modalidad, NombreCurso

    required_fields = [
        "Codigo_Curso", "Descripcion", "Duracion_horas", "Nivel",
        "profesor_nombre", "profesor_email", "fecha_inicio", "fecha_fin",
        "cupo_maximo", "modalidad", "NombreCurso"
    ]

    # Validación básica de campos
    if not all(field in datos for field in required_fields):
        missing = [field for field in required_fields if field not in datos]
        return jsonify({
            "error": "Faltan campos obligatorios",
            "campos_faltantes": missing
        }), 400

    conn = get_db_connection()
    if conn is None:
        # El error de conexión ya se imprime en db_config.py
        return jsonify({"mensaje": "Error interno del servidor al conectar con la DB"}), 500

    try:
        cur = conn.cursor()

        # La consulta INSERT
        # Asegúrate de que los tipos de datos en Python coincidan con los de PostgreSQL
        # Duracion_horas es TIMESTAMP WITHOUT TIME ZONE (se maneja mejor con strings o datetime objects)
        # cupo_maximo es INTEGER

        query = """
        INSERT INTO "Curso" (
            Codigo_Curso, Descripcion, Duracion_horas, Nivel,
            profesor_nombre, profesor_email, fecha_inicio, fecha_fin,
            cupo_maximo, modalidad, NombreCurso
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        values = (
            datos['Codigo_Curso'],
            datos['Descripcion'],
            datos['Duracion_horas'], # Asegúrate que esto sea un formato válido de TIMESTAMP o string 'HH:MM:SS'
            datos['Nivel'],
            datos['profesor_nombre'],
            datos['profesor_email'],
            datos['fecha_inicio'], # Usar formato 'YYYY-MM-DD' o similar
            datos['fecha_fin'],    # Usar formato 'YYYY-MM-DD' o similar
            datos['cupo_maximo'],
            datos['modalidad'],
            datos['NombreCurso']
        )

        # NOTA: En la línea anterior, faltaba un valor en 'values'. La lista tiene 11 campos,
        # pero tus datos de entrada solo tienen 10. Corregí la lista de 'values' para que tenga
        # 11 elementos, usando datos['NombreCurso']
        
        cur.execute(query, values)
        conn.commit()
        return jsonify({"mensaje": "Curso agregado exitosamente", "codigo": datos['Codigo_Curso']}), 201

    except Error as e:
        conn.rollback()
        # Puedes imprimir el error SQL para depuración
        print(f"Error al insertar el curso: {e}")
        return jsonify({"error": f"Error al interactuar con la DB: {str(e)}"}), 500
    finally:
        if conn:
            cur.close()
            conn.close()


@app.route('/cursos', methods=['GET'])
def listar_cursos():
    """
    Ruta para obtener la lista de todos los cursos.
    """
    conn = get_db_connection()
    if conn is None:
        return jsonify({"mensaje": "Error interno del servidor al conectar con la DB"}), 500

    try:
        cur = conn.cursor()
        cur.execute('SELECT * FROM "Curso";')
        cursos_data = cur.fetchall()

        # Obtener los nombres de las columnas para crear una lista de diccionarios
        column_names = [desc[0] for desc in cur.description]
        cursos = [
            dict(zip(column_names, row))
            for row in cursos_data
        ]

        if not cursos:
            return jsonify({"mensaje": "No se encontraron cursos"}), 200

        return jsonify(cursos), 200

    except Error as e:
        print(f"Error al listar cursos: {e}")
        return jsonify({"error": f"Error al interactuar con la DB: {str(e)}"}), 500
    finally:
        if conn:
            cur.close()
            conn.close()


@app.route('/cursos/<string:codigo>', methods=['DELETE'])
def eliminar_curso(codigo):
    """
    Ruta para eliminar un curso por su Codigo_Curso.
    """
    conn = get_db_connection()
    if conn is None:
        return jsonify({"mensaje": "Error interno del servidor al conectar con la DB"}), 500

    try:
        cur = conn.cursor()
        # Utilizamos el campo Codigo_Curso como clave para la eliminación
        cur.execute('DELETE FROM "Curso" WHERE Codigo_Curso = %s;', (codigo,))
        
        filas_afectadas = cur.rowcount
        conn.commit()

        if filas_afectadas == 0:
            return jsonify({"mensaje": f"No se encontró un curso con el código {codigo}"}), 404
        
        return jsonify({"mensaje": f"Curso con código {codigo} eliminado exitosamente"}), 200

    except Error as e:
        conn.rollback()
        print(f"Error al eliminar el curso: {e}")
        return jsonify({"error": f"Error al interactuar con la DB: {str(e)}"}), 500
    finally:
        if conn:
            cur.close()
            conn.close()


# ---------------------------------------------------------------------
# Ejecución de la Aplicación Flask
# ---------------------------------------------------------------------
if __name__ == '__main__':
    # Para ejecutar la aplicación, debes asegurarte de que las variables de entorno
    # (DB_HOST, DB_USER, DB_PASS, etc.) estén configuradas previamente.
    print("Iniciando la aplicación Flask...")
    # NOTA IMPORTANTE: Cambia debug=True a debug=False en producción
    app.run(debug=True)
