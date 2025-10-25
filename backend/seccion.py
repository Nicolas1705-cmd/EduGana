# seccion.py
from flask import Flask, request, jsonify
# Importa la función de conexión de tu archivo de configuración
# ASUME que el archivo es db_config.py y tiene la función get_db_connection
from configbd import get_db_connection

app = Flask(__name__)

# NOTA: Debes importar o registrar esta Blueprint/ruta en tu archivo principal (e.g., app.py)

# --------------------------------------------------------------------------
# 1. MÉTODO: LISTAR TODAS LAS SECCIONES (GET)
# --------------------------------------------------------------------------
@app.route('/secciones', methods=['GET'])
def listar_secciones():
    """
    Lista todos los registros de la tabla 'seccion'.
    """
    secciones = []
    try:
        # Usa el gestor de contexto para asegurar que la conexión se cierre
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Ejecuta la consulta
                cur.execute("SELECT ID, seccion, grado FROM public.seccion;")
                
                # Obtiene los nombres de las columnas para crear diccionarios
                col_names = [desc[0] for desc in cur.description]
                
                # Obtiene todos los resultados
                registros = cur.fetchall()
                
                # Convierte la lista de tuplas a una lista de diccionarios
                for registro in registros:
                    secciones.append(dict(zip(col_names, registro)))
        
        # Retorna la lista como JSON
        return jsonify(secciones), 200

    except Exception as e:
        # Manejo de errores genérico (p.ej., error de BD)
        print(f"Error al listar secciones: {e}")
        return jsonify({"mensaje": f"Error interno del servidor: {e}"}), 500

# --------------------------------------------------------------------------
# 2. MÉTODO: AGREGAR UNA NUEVA SECCIÓN (POST)
# --------------------------------------------------------------------------
@app.route('/secciones', methods=['POST'])
def agregar_seccion():
    """
    Agrega un nuevo registro a la tabla 'seccion' a partir de datos JSON.
    """
    # 1. Obtener datos JSON
    data = request.get_json()
    seccion = data.get('seccion')
    idGrado = data.get('idGrado')

    # 2. Validar datos requeridos
    if not seccion or not idGrado:
        return jsonify({"mensaje": "Faltan campos requeridos: 'seccion' y 'idGrado'."}), 400

    try:
        # 3. Conexión y Transacción
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # La consulta usa %s para prevenir inyección SQL (parametrización)
                # RETURNING ID para obtener el ID generado (asumiendo que es SERIAL)
                cur.execute("""
                    INSERT INTO seccion (seccion, "idGrado") 
                    VALUES (%s, %s) 
                    RETURNING ID;
                """, (seccion, idGrado))
                
                # Obtener el ID de la sección recién insertada
                nuevo_id = cur.fetchone()[0]
                
                # Confirmar los cambios
                conn.commit()
        
        return jsonify({
            "mensaje": "Sección agregada con éxito", 
            "ID": nuevo_id,
            "seccion": seccion,
            "idGrado": idGrado
        }), 201 # 201 Created

    except Exception as e:
        print(f"Error al agregar sección: {e}")
        return jsonify({"mensaje": f"Error al insertar en la base de datos: {e}"}), 500

# --------------------------------------------------------------------------
# 3. MÉTODO: ELIMINAR UNA SECCIÓN POR ID (DELETE)
# --------------------------------------------------------------------------
@app.route('/secciones/<int:seccion_id>', methods=['DELETE'])
def eliminar_seccion(seccion_id):
    """
    Elimina un registro de la tabla 'seccion' por su ID.
    """
    try:
        # Conexión y Transacción
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Ejecutar la eliminación
                cur.execute("DELETE FROM seccion WHERE ID = %s;", (seccion_id,))
                
                # Obtener el número de filas afectadas
                filas_afectadas = cur.rowcount
                
                # Confirmar los cambios
                conn.commit()

        if filas_afectadas == 0:
            # Si no se eliminó ninguna fila, el ID no existe
            return jsonify({"mensaje": f"Sección con ID {seccion_id} no encontrada."}), 404
        
        return jsonify({"mensaje": f"Sección con ID {seccion_id} eliminada con éxito."}), 200

    except Exception as e:
        print(f"Error al eliminar sección: {e}")
        return jsonify({"mensaje": f"Error al eliminar de la base de datos: {e}"}), 500


# Si ejecutas este archivo directamente, correrá el servidor
if __name__ == '__main__':
    # Usar un puerto y host apropiados para el desarrollo
    # Considera usar un archivo principal (app.py) para correr Flask en producción
    app.run(debug=True, port=5001)