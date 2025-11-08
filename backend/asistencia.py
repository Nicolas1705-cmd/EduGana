# asistencia.py
from flask import Flask, request, jsonify
import psycopg2.extras # Importamos para obtener resultados como diccionarios
from configbd import get_db_connection # ⬅️ Importación de tu archivo de configuración

app = Flask(__name__)

# ==========================================================================
# 🥇 MÉTODO LISTAR ASISTENCIAS (GET)
# URL: /api/asistencias
# ==========================================================================
@app.route('/api/asistencias', methods=['GET'])
def listar_asistencias():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500

    cur = None
    try:
        # Usamos RealDictCursor para que cada fila se devuelva como un diccionario (JSON)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) 
        cur.execute("SELECT * FROM asistencia ORDER BY id_asistencia DESC;")
        asistencias = cur.fetchall()
        
        return jsonify(asistencias), 200

    except psycopg2.Error as e:
        return jsonify({"mensaje": "Error al listar asistencias", "error": str(e)}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()


# ==========================================================================
# 🥈 MÉTODO AGREGAR ASISTENCIA (POST)
# URL: /api/asistencias
# ==========================================================================
@app.route('/api/asistencias', methods=['POST'])
def agregar_asistencia():
    # Obtener el cuerpo de la solicitud en formato JSON
    data = request.get_json() 

    # Validación básica de datos
    if not data or not all(key in data for key in ['id_usuario', 'fecha', 'hora_entrada', 'estado']):
        return jsonify({"mensaje": "Datos incompletos o mal formados"}), 400

    # Extraer campos
    id_usuario = data.get('id_usuario')
    fecha = data.get('fecha')
    hora_entrada = data.get('hora_entrada')
    # hora_salida puede ser NULL, lo obtenemos si existe, sino usamos None (que PostgreSQL maneja como NULL)
    hora_salida = data.get('hora_salida') 
    estado = data.get('estado')

    conn = get_db_connection()
    if conn is None:
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500

    cur = None
    try:
        cur = conn.cursor()
        query = """
        INSERT INTO asistencia (id_usuario, fecha, hora_entrada, hora_salida, estado) 
        VALUES (%s, %s, %s, %s, %s) RETURNING id_asistencia;
        """
        # Ejecutamos la consulta. psycopg2 se encarga de formatear correctamente los valores
        cur.execute(query, (id_usuario, fecha, hora_entrada, hora_salida, estado))
        
        # Obtener el ID del registro recién insertado
        id_asistencia = cur.fetchone()[0]
        conn.commit()

        return jsonify({
            "mensaje": "Asistencia agregada exitosamente", 
            "id_asistencia": id_asistencia
        }), 201 # 201 Created

    except psycopg2.Error as e:
        conn.rollback() # Deshacer la transacción si falla
        return jsonify({"mensaje": "Error al agregar asistencia", "error": str(e)}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()


# ==========================================================================
# 🥉 MÉTODO ELIMINAR ASISTENCIA (DELETE)
# URL: /api/asistencias/<id_asistencia>
# ==========================================================================
@app.route('/api/asistencias/<int:id_asistencia>', methods=['DELETE'])
def eliminar_asistencia(id_asistencia):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500

    cur = None
    try:
        cur = conn.cursor()
        query = "DELETE FROM asistencia WHERE id_asistencia = %s;"
        cur.execute(query, (id_asistencia,))
        
        # Verificar si se eliminó alguna fila
        if cur.rowcount == 0:
            conn.rollback()
            return jsonify({"mensaje": f"No se encontró asistencia con ID {id_asistencia} para eliminar"}), 404
            
        conn.commit()
        return jsonify({"mensaje": f"Asistencia con ID {id_asistencia} eliminada exitosamente"}), 200

    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({"mensaje": "Error al eliminar asistencia", "error": str(e)}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()


if __name__ == '__main__':
    # Usar modo debug solo para desarrollo.
    app.run(debug=True)