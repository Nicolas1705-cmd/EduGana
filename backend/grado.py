import configbd
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt 
import psycopg2
# ⚠️ Importa tu archivo de configuración de la base de datos
from configbd import get_db_connection

# Inicialización de la aplicación Flask
app = Flask(__name__)
# Opcional: Si usas Bcrypt para otra parte de tu API (e.g., usuarios)
bcrypt = Bcrypt(app) 


# ==============================================================================
# 1. MÉTODO LISTAR TODOS LOS GRADOS (GET /grados)
# ==============================================================================
@app.route('/grados', methods=['GET'])
def listar_grados():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Error de conexión a la base de datos"}), 500

    try:
        cur = conn.cursor()
        # Selecciona todos los campos de la tabla Grado
        cur.execute("SELECT id_grado, id_nombre, nivel_academico, activo, fecha_creacion, descripcion FROM Grado ORDER BY id_grado;")
        grados = cur.fetchall()
        
        # Mapea los resultados a una lista de diccionarios
        grados_list = []
        # Obtiene los nombres de las columnas para usarlos como claves
        column_names = [desc[0] for desc in cur.description] 
        
        for grado in grados:
            grados_list.append(dict(zip(column_names, grado)))
            
        cur.close()
        return jsonify(grados_list), 200

    except psycopg2.Error as e:
        return jsonify({"message": f"Error de base de datos al listar: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

# ==============================================================================
# 1.1 MÉTODO OBTENER GRADO POR ID (GET /grados/<id>)
# ==============================================================================
@app.route('/grados/<int:id_grado>', methods=['GET'])
def obtener_grado(id_grado):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Error de conexión a la base de datos"}), 500

    try:
        cur = conn.cursor()
        # Consulta SQL para obtener un grado específico
        sql = "SELECT id_grado, id_nombre, nivel_academico, activo, fecha_creacion, descripcion FROM Grado WHERE id_grado = %s;"
        cur.execute(sql, (id_grado,))
        grado = cur.fetchone()
        
        cur.close()
        
        if grado is None:
            return jsonify({"message": f"No se encontró Grado con ID {id_grado}"}), 404

        # Mapea el resultado a un diccionario
        column_names = [desc[0] for desc in cur.description]
        grado_dict = dict(zip(column_names, grado))
        
        return jsonify(grado_dict), 200

    except psycopg2.Error as e:
        return jsonify({"message": f"Error de base de datos al obtener: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


# ==============================================================================
# 2. MÉTODO AGREGAR UN GRADO (POST)
# ==============================================================================
@app.route('/grados', methods=['POST'])
def agregar_grado():
    data = request.get_json()
    
    # ⚠️ Validaciones básicas de los campos requeridos (según la tabla)
    if not data or 'id_nombre' not in data:
        return jsonify({"message": "Faltan datos requeridos (id_nombre)"}), 400

    # Los campos 'activo' y 'fecha_creacion' tienen valores por defecto en esta implementación,
    # pero puedes hacerlos obligatorios si es necesario.
    id_nombre = data['id_nombre']
    nivel_academico = data.get('nivel_academico') # Puede ser None si no se envía
    activo = data.get('activo', True) # Valor por defecto 'True' si no se envía
    descripcion = data.get('descripcion') # Puede ser None si no se envía

    # NOTA: 'fecha_creacion' se puede establecer a NOW() en la base de datos o aquí.
    # Usaremos el valor por defecto de la base de datos (si está configurado) 
    # o None para que el motor DB lo maneje.

    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Error de conexión a la base de datos"}), 500

    try:
        cur = conn.cursor()
        
        # Consulta SQL: Usamos %s como placeholders para evitar inyección SQL
        sql = """
        INSERT INTO Grado (id_nombre, nivel_academico, activo, descripcion) 
        VALUES (%s, %s, %s, %s) 
        RETURNING id_grado;
        """
        
        cur.execute(sql, (id_nombre, nivel_academico, activo, descripcion))
        
        # Obtiene el ID del nuevo registro insertado
        id_grado_nuevo = cur.fetchone()[0]
        
        conn.commit()
        cur.close()
        
        return jsonify({
            "message": "Grado agregado exitosamente", 
            "id_grado": id_grado_nuevo,
            "id_nombre": id_nombre
        }), 201

    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({"message": f"Error de base de datos al agregar: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

# Si quieres añadir la función de actualizar (PUT) completa:
# ==============================================================================
# 3. MÉTODO ACTUALIZAR UN GRADO (PUT /grados/<id>)
# ==============================================================================
@app.route('/grados/<int:id_grado>', methods=['PUT'])
def actualizar_grado(id_grado):
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "No se proporcionaron datos para actualizar"}), 400

    id_nombre = data.get('id_nombre')
    nivel_academico = data.get('nivel_academico')
    activo = data.get('activo')
    descripcion = data.get('descripcion')

    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Error de conexión a la base de datos"}), 500

    try:
        cur = conn.cursor()
        updates = []
        params = []

        # Construye la consulta dinámicamente
        if id_nombre is not None:
            updates.append("id_nombre = %s")
            params.append(id_nombre)
        if nivel_academico is not None:
            updates.append("nivel_academico = %s")
            params.append(nivel_academico)
        
        # Se necesita verificar explícitamente si 'activo' está en data porque podría ser False
        if 'activo' in data and activo is not None: 
            updates.append("activo = %s")
            params.append(activo)
            
        if descripcion is not None:
            updates.append("descripcion = %s")
            params.append(descripcion)
            
        if not updates:
            return jsonify({"message": "No se proporcionaron campos válidos para actualizar"}), 400

        # Une las actualizaciones y añade el ID al final de los parámetros
        sql = f"UPDATE Grado SET {', '.join(updates)} WHERE id_grado = %s;"
        params.append(id_grado)

        cur.execute(sql, tuple(params))
        rows_updated = cur.rowcount

        conn.commit()
        cur.close()

        if rows_updated > 0:
            return jsonify({"message": f"Grado con ID {id_grado} actualizado exitosamente"}), 200
        else:
            return jsonify({"message": f"No se encontró Grado con ID {id_grado} o no hubo cambios"}), 404

    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({"message": f"Error de base de datos al actualizar: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


# ==============================================================================
# 4. MÉTODO ELIMINAR UN GRADO (DELETE)
# ==============================================================================
@app.route('/grados/<int:id_grado>', methods=['DELETE'])
def eliminar_grado(id_grado):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Error de conexión a la base de datos"}), 500
    
    try:
        cur = conn.cursor()
        
        # Consulta SQL para eliminar un grado por su ID
        sql = "DELETE FROM Grado WHERE id_grado = %s;"
        cur.execute(sql, (id_grado,))
        
        # Revisa cuántas filas fueron afectadas
        rows_deleted = cur.rowcount

        conn.commit()
        cur.close()
        
        if rows_deleted > 0:
            return jsonify({"message": f"Grado con ID {id_grado} eliminado exitosamente"}), 200
        else:
            return jsonify({"message": f"No se encontró Grado con ID {id_grado}"}), 404

    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({"message": f"Error de base de datos al eliminar: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

# Esto es necesario para ejecutar la aplicación si el archivo es el principal
if __name__ == '__main__':
    # ⚠️ Usar 'debug=True' solo en desarrollo. ¡Cámbialo a False en producción!
    app.run(debug=True)