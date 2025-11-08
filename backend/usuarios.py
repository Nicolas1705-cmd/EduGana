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

@app.route('/usuarios', methods=['POST'])
def add_user():
    """
    Agrega un nuevo usuario a la tabla 'usuarios'.
    Requiere 'dni', 'correo', 'password', 'nombres' y 'apellidos'.
    """
    data = request.get_json()
    dni = data.get('dni')
    correo = data.get('correo')
    password = data.get('password') # Recibimos la password en claro
    nombres = data.get('nombres')
    apellidos = data.get('apellidos')
    telefono = data.get('telefono') # Opcional

    required_fields = [dni, correo, password, nombres, apellidos]
    if not all(required_fields):
        return jsonify({"message": "Faltan campos obligatorios: dni, correo, password, nombres, apellidos."}), 400

    # 1. Hashear la contraseña
    try:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    except Exception as e:
        print(f"Error al hashear la contraseña: {e}")
        return jsonify({"message": "Error al procesar la contraseña."}), 500

    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Error interno del servidor (BD).", "code": 500}), 500
    
    cursor = conn.cursor()
    try:
        insert_query = """
            INSERT INTO usuarios (dni, correo, contrasena_hash, nombres, apellidos, telefono) 
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """
        # El valor de teléfono será None si no se proporciona en el JSON
        cursor.execute(insert_query, (dni, correo, hashed_password, nombres, apellidos, telefono))
        
        # Obtener el ID del nuevo registro
        new_id = cursor.fetchone()[0]
        
        conn.commit()
        
        return jsonify({
            "message": "Usuario registrado exitosamente.", 
            "id": new_id,
            "correo": correo
        }), 201

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({"message": "El DNI o correo ya está registrado."}), 409

    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error de base de datos durante el registro: {e}")
        return jsonify({"message": "Error interno del servidor al registrar usuario.", "details": str(e)}), 500
        
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route('/usuarios', methods=['GET'])
def list_users():
    """Lista todos los usuarios (solo datos seguros)."""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Error interno del servidor (BD).", "code": 500}), 500
    
    # Usamos RealDictCursor para obtener resultados como diccionarios
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # EXCLUIR 'contrasena_hash' por seguridad.
        select_query = """
            SELECT id, dni, correo, nombres, apellidos, telefono, fecha_creacion, activo 
            FROM usuarios;
        """
        cursor.execute(select_query)
        usuarios = cursor.fetchall()
        
        return jsonify(usuarios), 200

    except psycopg2.Error as e:
        print(f"Error de base de datos durante la consulta: {e}")
        return jsonify({"message": "Error interno del servidor al listar usuarios."}), 500
        
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route('/usuarios/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Obtiene un solo usuario por ID (solo datos seguros)."""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Error interno del servidor (BD).", "code": 500}), 500
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        select_query = """
            SELECT id, dni, correo, nombres, apellidos, telefono, fecha_creacion, activo 
            FROM usuarios WHERE id = %s;
        """
        cursor.execute(select_query, (user_id,))
        usuario = cursor.fetchone()
        
        if usuario:
            return jsonify(usuario), 200
        else:
            return jsonify({"message": f"Usuario con ID {user_id} no encontrado."}), 404

    except psycopg2.Error as e:
        print(f"Error de base de datos al obtener usuario: {e}")
        return jsonify({"message": "Error interno del servidor."}), 500
        
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route('/usuarios/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Elimina un usuario por su ID."""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Error interno del servidor (BD).", "code": 500}), 500
    
    cursor = conn.cursor()
    try:
        delete_query = "DELETE FROM usuarios WHERE id = %s;"
        cursor.execute(delete_query, (user_id,))
        
        # rowcount indica el número de filas afectadas
        if cursor.rowcount == 0:
            conn.rollback()
            return jsonify({"message": f"Usuario con ID {user_id} no encontrado para eliminar."}), 404
            
        conn.commit()
        return jsonify({"message": f"Usuario con ID {user_id} eliminado exitosamente."}), 200

    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error de base de datos al eliminar: {e}")
        return jsonify({"message": "Error interno del servidor al eliminar usuario."}), 500
        
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)