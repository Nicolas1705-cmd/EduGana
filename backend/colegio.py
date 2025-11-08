from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity, unset_jwt_cookies
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__) 
bcrypt = Bcrypt(app) 

# Configuración de la conexión a la base de datos
DB_NAME = "edugana_db"
DB_USER = "postgres"
DB_PASS = "System.2025*"
DB_HOST = "35.237.18.79" # o la IP del servidor
DB_PORT = "5432"
 

def get_db_connection():
    """
    Función para establecer la conexión a la base de datos PostgreSQL.
    """
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# 1. Método: LISTAR TODOS LOS COLEGIOS (GET) 📚
@app.route('/colegios', methods=['GET'])
def listar_colegios():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Error de conexión a la base de datos"}), 500

    try:
        cur = conn.cursor()
        
        # Seleccionar todas las columnas (excepto tal vez la contraseña, pero aquí no hay)
        cur.execute("""
            SELECT 
                id_colegio, nombre, codigo, direccion, distrito, provincia, departamento, 
                telefono, email, director, tipo_colegio, nivel_educativo, fecha_fundacion, 
                numero_aulas, capacidad_estudiantes, activo, fecha_registro
            FROM colegio
            ORDER BY id_colegio;
        """)
        
        # Obtener los nombres de las columnas para usarlos como claves del diccionario
        columns = [desc[0] for desc in cur.description]
        colegios = fetchall_to_dict(cur, columns)
        
        cur.close()
        
        return jsonify(colegios)

    except psycopg2.Error as e:
        print(f"Error de BD al listar colegios: {e}")
        return jsonify({"message": "Error al obtener la lista de colegios", "error": str(e)}), 500
    
    finally:
        conn.close()

# 2. Método: AGREGAR NUEVO COLEGIO (POST) ➕
@app.route('/colegios', methods=['POST'])
def agregar_colegio():
    data = request.get_json()
    
    # Lista de campos requeridos y opcionales (basados en tu esquema)
    required_fields = ['nombre', 'codigo', 'direccion', 'distrito', 'provincia', 'departamento']
    
    # Validación básica de datos
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Falta el campo requerido: {field}"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Error de conexión a la base de datos"}), 500

    try:
        cur = conn.cursor()
        
        # La consulta utiliza CURRENT_TIMESTAMP y 'true' como valores por defecto 
        # para fecha_registro y activo, así que no se requieren aquí.
        
        # Definición de la consulta SQL y los valores a insertar (usando %s para evitar inyección SQL)
        sql = """
            INSERT INTO colegio (
                nombre, codigo, direccion, distrito, provincia, departamento, 
                telefono, email, director, tipo_colegio, nivel_educativo, 
                fecha_fundacion, numero_aulas, capacidad_estudiantes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_colegio;
        """
        
        # Tupla de datos, usando .get() con None para campos opcionales
        values = (
            data['nombre'], 
            data['codigo'], 
            data['direccion'], 
            data['distrito'], 
            data['provincia'], 
            data['departamento'],
            data.get('telefono'), 
            data.get('email'), 
            data.get('director'), 
            data.get('tipo_colegio'), 
            data.get('nivel_educativo'), 
            data.get('fecha_fundacion'), # psycopg2 maneja el formato 'YYYY-MM-DD'
            data.get('numero_aulas'), 
            data.get('capacidad_estudiantes')
        )
        
        cur.execute(sql, values)
        new_id = cur.fetchone()[0] # Obtiene el ID generado por el trigger/secuencia
        
        conn.commit() # ¡Confirmar la transacción!
        cur.close()
        
        return jsonify({
            "message": "Colegio agregado exitosamente",
            "id_colegio": new_id,
            "data": data
        }), 201

    except psycopg2.Error as e:
        conn.rollback() # Revierte la transacción en caso de error
        print(f"Error de BD al agregar colegio: {e}")
        return jsonify({"message": "Error al agregar el colegio", "error": str(e)}), 500
    
    finally:
        conn.close()

# 3. Método: ELIMINAR COLEGIO (DELETE) 🗑️
@app.route('/colegios/<int:id_colegio>', methods=['DELETE'])
def eliminar_colegio(id_colegio):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Error de conexión a la base de datos"}), 500

    try:
        cur = conn.cursor()
        
        # Se recomienda usar un 'soft delete' (activo = false) en lugar de DELETE, 
        # pero para este ejemplo, usaremos DELETE.
        sql = "DELETE FROM colegio WHERE id_colegio = %s;"
        
        cur.execute(sql, (id_colegio,))
        rows_deleted = cur.rowcount
        
        conn.commit()
        cur.close()

        if rows_deleted == 0:
            return jsonify({"message": f"Colegio con ID {id_colegio} no encontrado"}), 404
        
        return jsonify({"message": f"Colegio con ID {id_colegio} eliminado exitosamente"}), 200

    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error de BD al eliminar colegio: {e}")
        return jsonify({"message": "Error al eliminar el colegio", "error": str(e)}), 500
    
    finally:
        conn.close()

# --- Ejecutar la aplicación (Solo para desarrollo) ---

if __name__ == '__main__':
    # Asegúrate de configurar tus variables de entorno antes de ejecutar
    # o usar tu configbd.py sin variables de entorno (como lo tenías al inicio)
    app.run(debug=True)