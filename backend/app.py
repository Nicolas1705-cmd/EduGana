from flask import Flask, request, jsonify
import mysql.connector
import bcrypt
import datetime
from functools import wraps
import jwt

# --- Configuración de la aplicación y la base de datos ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'una_clave_secreta_fuerte'  # ¡Cámbiala en producción!

# Conexión directa a MySQL
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='coinbd'
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error de conexión a la base de datos: {err}")
        return None

# --- Decorador para autenticación y roles ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token de autenticación faltante'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user_id = data['user_id']
            current_role_id = data['role_id']
        except:
            return jsonify({'message': 'Token no es válido o ha expirado'}), 401

        return f(current_user_id, current_role_id, *args, **kwargs)

    return decorated

# --- Endpoints de la API ---

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    phone_number = data.get('phone_number')
    role_id = data.get('role_id', 3)  # Por defecto, rol de estudiante (3)

    if not all([username, email, password, phone_number]):
        return jsonify({'message': 'Nombre de usuario, email, phone_number y contraseña son obligatorios'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = "INSERT INTO users (username, email, password_hash, phone_number, role_id) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (username, email, hashed_password, phone_number, role_id))
            conn.commit()
            return jsonify({'message': 'Usuario registrado con éxito!'}), 201
        except mysql.connector.Error as err:
            return jsonify({'message': f'Error al registrar usuario: {err.msg}'}), 500
        finally:
            cursor.close()
            conn.close()
    return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    auth = request.json
    email = auth.get('email')
    password = auth.get('password')

    if not email or not password:
        return jsonify({'message': 'Email y contraseña son obligatorios'}), 400

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT user_id, password_hash, role_id FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()

            if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                token = jwt.encode({
                    'user_id': user['user_id'],
                    'role_id': user['role_id'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # ¡Aquí está la corrección!
                }, app.config['SECRET_KEY'], algorithm="HS256")
                return jsonify({'token': token}), 200
            
            return jsonify({'message': 'Credenciales incorrectas'}), 401
        except mysql.connector.Error as err:
            return jsonify({'message': f'Error en el login: {err.msg}'}), 500
        finally:
            cursor.close()
            conn.close()
    return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500

# --- Endpoint para obtener el perfil completo del usuario ---
@app.route('/api/profile', methods=['GET'])
@token_required
def get_user_profile(current_user_id, current_role_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            # 1. Obtener la información principal del usuario y su saldo
            user_info_query = """
                SELECT u.username, u.email, up.first_name, up.last_name, a.balance
                FROM users u
                LEFT JOIN user_profiles up ON u.user_id = up.user_id
                LEFT JOIN accounts a ON u.user_id = a.user_id
                WHERE u.user_id = %s
            """
            cursor.execute(user_info_query, (current_user_id,))
            user_data = cursor.fetchone()
            
            if not user_data:
                return jsonify({'message': 'Perfil de usuario no encontrado'}), 404

            # 2. Obtener el progreso del usuario
            progress_query = """
                SELECT v.title AS video_title, up.score, up.is_completed, up.completion_date
                FROM user_progress up
                JOIN videos v ON up.video_id = v.video_id
                WHERE up.user_id = %s
            """
            cursor.execute(progress_query, (current_user_id,))
            user_progress = cursor.fetchall()

            # 3. Obtener las recompensas del usuario
            rewards_query = """
                SELECT v.title AS video_title, r.amount, r.claimed, r.claimed_at
                FROM rewards r
                JOIN videos v ON r.video_id = v.video_id
                WHERE r.user_id = %s
            """
            cursor.execute(rewards_query, (current_user_id,))
            user_rewards = cursor.fetchall()
            
            # 4. Obtener las transacciones del usuario
            transactions_query = """
                SELECT t.amount, t.transaction_type, t.notes, t.created_at
                FROM transactions t
                JOIN accounts from_acc ON t.from_account_id = from_acc.account_id
                JOIN accounts to_acc ON t.to_account_id = to_acc.account_id
                WHERE from_acc.user_id = %s OR to_acc.user_id = %s
                ORDER BY t.created_at DESC
            """
            cursor.execute(transactions_query, (current_user_id, current_user_id))
            user_transactions = cursor.fetchall()

            # 5. Combinar toda la información en una sola respuesta
            profile_data = {
                "profile": user_data,
                "progress": user_progress,
                "rewards": user_rewards,
                "transactions": user_transactions
            }
            
            return jsonify(profile_data), 200

        except mysql.connector.Error as err:
            return jsonify({'message': f'Error en la base de datos: {err.msg}'}), 500
        finally:
            cursor.close()
            conn.close()
    return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500

@app.route('/api/users/<int:user_id>/disable', methods=['PUT'])
@token_required
def disable_user(current_user_id, current_role_id, user_id):
    # Verificación de rol: solo el Superusuario (role_id=1) puede inhabilitar usuarios
    if current_role_id != 1:
        return jsonify({'message': 'No tienes permisos para realizar esta acción'}), 403

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Consulta para inhabilitar al usuario (status = 0)
            query = "UPDATE users SET status = 0 WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({'message': 'Usuario no encontrado o ya inhabilitado'}), 404
            
            return jsonify({'message': f'Usuario con ID {user_id} inhabilitado con éxito'}), 200

        except mysql.connector.Error as err:
            return jsonify({'message': f'Error al inhabilitar usuario: {err.msg}'}), 500
        finally:
            cursor.close()
            conn.close()
    return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500

# --- Endpoint para que un Superusuario Edite Roles ---
@app.route('/api/users/<int:user_id>/role', methods=['PUT'])
@token_required
def update_user_role(current_user_id, current_role_id, user_id):
    # Verificar si el usuario actual es un Superusuario (role_id=1)
    if current_role_id != 1:
        return jsonify({'message': 'Acceso denegado. No tienes permisos de Superusuario.'}), 403

    # Evitar que un Superusuario cambie su propio rol
    if current_user_id == user_id:
        return jsonify({'message': 'No puedes cambiar tu propio rol.'}), 403

    data = request.json
    new_role_id = data.get('role_id')
    
    if not new_role_id:
        return jsonify({'message': 'El campo role_id es obligatorio.'}), 400

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Primero, verifica que el usuario a editar exista
            cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
            if cursor.fetchone() is None:
                return jsonify({'message': 'Usuario no encontrado.'}), 404

            # Luego, actualiza el rol del usuario
            query = "UPDATE users SET role_id = %s WHERE user_id = %s"
            cursor.execute(query, (new_role_id, user_id))
            conn.commit()

            return jsonify({'message': f'Rol del usuario {user_id} actualizado a {new_role_id}.'}), 200

        except mysql.connector.Error as err:
            return jsonify({'message': f'Error en la base de datos: {err.msg}'}), 500
        finally:
            cursor.close()
            conn.close()
    return jsonify({'message': 'Fallo en la conexión a la base de datos.'}), 500

# --- Endpoint para que un usuario Edite su Información de Contacto ---
@app.route('/api/users/<int:user_id>/contact', methods=['PUT'])
@token_required
def update_user_contact(current_user_id, current_role_id, user_id):
    # Verificar que el usuario solo pueda editar su propia información
    if current_user_id != user_id:
        return jsonify({'message': 'No tienes permisos para editar la información de otro usuario.'}), 403

    data = request.json
    email = data.get('email')
    phone_number = data.get('phone_number')

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            updates = []
            params = []
            
            if email:
                updates.append("email = %s")
                params.append(email)
            if phone_number:
                updates.append("phone_number = %s")
                params.append(phone_number)

            if not updates:
                return jsonify({'message': 'No se proporcionaron datos para actualizar.'}), 400

            query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s"
            params.append(user_id)
            
            cursor.execute(query, tuple(params))
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({'message': 'Usuario no encontrado o datos idénticos.'}), 404
            
            return jsonify({'message': f'Información de contacto del usuario {user_id} actualizada con éxito.'}), 200

        except mysql.connector.Error as err:
            return jsonify({'message': f'Error en la base de datos: {err.msg}'}), 500
        finally:
            cursor.close()
            conn.close()
    return jsonify({'message': 'Fallo en la conexión a la base de datos.'}), 500

# --- Endpoint para que un usuario Edite su Contraseña ---
@app.route('/api/users/<int:user_id>/password', methods=['PUT'])
@token_required
def update_password(current_user_id, current_role_id, user_id):
    if current_user_id != user_id:
        return jsonify({'message': 'No tienes permisos para cambiar la contraseña de este usuario'}), 403

    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not all([current_password, new_password]):
        return jsonify({'message': 'La contraseña actual y la nueva son obligatorias'}), 400

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT password_hash FROM users WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            user_data = cursor.fetchone()

            if not user_data:
                return jsonify({'message': 'Usuario no encontrado'}), 404

            stored_password_hash = user_data['password_hash']

            if not bcrypt.checkpw(current_password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                return jsonify({'message': 'La contraseña actual es incorrecta'}), 401
            
            new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

            update_query = "UPDATE users SET password_hash = %s WHERE user_id = %s"
            cursor.execute(update_query, (new_password_hash, user_id))
            conn.commit()

            return jsonify({'message': 'Contraseña actualizada con éxito'}), 200

        except mysql.connector.Error as err:
            return jsonify({'message': f'Error al actualizar la contraseña: {err.msg}'}), 500
        finally:
            cursor.close()
            conn.close()
    return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500

# --- Nuevo Endpoint para Inyectar Monedas ---
@app.route('/api/admin/inject_coins', methods=['POST'])
@token_required
def inject_coins(current_user_id, current_role_id):
    # Solo el Superusuario (role_id=1) puede inyectar monedas
    if current_role_id != 1:
        return jsonify({'message': 'Acceso denegado. No tienes permisos de Superusuario.'}), 403

    data = request.json
    user_id_to_update = data.get('user_id')
    amount_to_inject = data.get('amount')
    
    # Validar que los datos necesarios existan
    if not user_id_to_update or not amount_to_inject:
        return jsonify({'message': 'El user_id y el monto son obligatorios.'}), 400
    
    try:
        amount_to_inject = float(amount_to_inject)
        if amount_to_inject <= 0:
            return jsonify({'message': 'El monto a inyectar debe ser un valor positivo.'}), 400
    except (ValueError, TypeError):
        return jsonify({'message': 'El monto a inyectar debe ser un número válido.'}), 400
        
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Primero, obtener el account_id del usuario a actualizar
            cursor.execute("SELECT account_id FROM accounts WHERE user_id = %s", (user_id_to_update,))
            account = cursor.fetchone()
            if not account:
                return jsonify({'message': 'Cuenta de usuario no encontrada.'}), 404
            
            target_account_id = account[0]

            # 1. Actualizar el balance en la tabla 'accounts'
            update_balance_query = "UPDATE accounts SET balance = balance + %s WHERE account_id = %s"
            cursor.execute(update_balance_query, (amount_to_inject, target_account_id))
            
            # 2. Registrar la transacción en la tabla 'transactions'
            # Se asume que tienes un account_id para el 'sistema' o 'administrador'
            admin_account_query = "SELECT account_id FROM accounts WHERE user_id = %s"
            cursor.execute(admin_account_query, (current_user_id,))
            admin_account = cursor.fetchone()
            
            if not admin_account:
                return jsonify({'message': 'Cuenta de administrador no encontrada.'}), 500

            transaction_query = """
                INSERT INTO transactions 
                (from_account_id, to_account_id, amount, transaction_type, status, notes, created_at) 
                VALUES (%s, %s, %s, 'injection', 'completed', 'Inyección de capital por admin', NOW())
            """
            cursor.execute(transaction_query, (admin_account[0], target_account_id, amount_to_inject))

            conn.commit()
            
            return jsonify({'message': f'Se inyectaron {amount_to_inject} monedas al usuario {user_id_to_update} con éxito.'}), 200

        except mysql.connector.Error as err:
            conn.rollback()  # Deshace cualquier cambio si algo falla
            return jsonify({'message': f'Error en la base de datos: {err.msg}'}), 500
        finally:
            cursor.close()
            conn.close()
    return jsonify({'message': 'Fallo en la conexión a la base de datos.'}), 500
 


if __name__ == '__main__':
    app.run(debug=True)