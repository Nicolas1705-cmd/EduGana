from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity, unset_jwt_cookies
import psycopg2

app = Flask(__name__)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Configuración de la conexión a la base de datos
DB_NAME = "CoinDB"
DB_USER = "postgres"
DB_PASS = "nico"
DB_HOST = "127.0.0.1" # o la IP del servidor
DB_PORT = "5432"

# Configuración de la clave secreta para JWT
app.config["JWT_SECRET_KEY"] = "super-secret-key-that-should-be-in-env-file"
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SAMESITE"] = "Strict"
app.config["JWT_COOKIE_SECURE"] = False  # Cambiar a True en producción para HTTPS

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

# app.py

# app.py

# ... (rest of your app's code)

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    phone_number = data.get('phone_number')
    role_id = data.get('role_id', 3)

    if not all([username, email, password]):
        return jsonify({'message': 'Nombre de usuario, email y contraseña son obligatorios'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500

    try:
        cursor = conn.cursor()
        
        # 💡 ¡CORRECCIÓN AQUÍ! Se elimina la línea conn.begin()
        
        # 1. Insertar en la tabla 'users'
        user_query = "INSERT INTO users (username, email, password_hash, phone_number, role_id) VALUES (%s, %s, %s, %s, %s) RETURNING user_id;"
        cursor.execute(user_query, (username, email, hashed_password, phone_number, role_id))
        
        new_user_id = cursor.fetchone()[0]
        
        # 2. Crear una cuenta en la tabla 'accounts'
        account_query = "INSERT INTO accounts (user_id, balance) VALUES (%s, %s);"
        cursor.execute(account_query, (new_user_id, 0.00))

        # 3. Crear un perfil en la tabla 'user_profiles'
        profile_query = "INSERT INTO user_profiles (user_id) VALUES (%s);"
        cursor.execute(profile_query, (new_user_id,))

        conn.commit()
        return jsonify({'message': 'Usuario, perfil y cuenta registrados con éxito!'}), 201
    
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({'message': 'El nombre de usuario, email o número de teléfono ya existen.'}), 409
    
    except Exception as e:
        conn.rollback()
        print(f'Error al registrar usuario: {e}')
        return jsonify({'message': 'Error interno del servidor'}), 500
    
    finally:
        cursor.close()
        conn.close()

# ... (código anterior)
# app.py

@app.route('/api/auth/login', methods=['POST'])
def login():
    auth = request.json
    email = auth.get('email')
    password = auth.get('password')

    if not email or not password:
        return jsonify({'message': 'Email y contraseña son obligatorios'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500

    try:
        cursor = conn.cursor()
        
        # 1. Obtener los datos del usuario por email
        query = "SELECT user_id, password_hash, role_id, status FROM users WHERE email = %s;"
        cursor.execute(query, (email,))
        user_data = cursor.fetchone()

        if not user_data:
            return jsonify({'message': 'Email o contraseña incorrectos'}), 401

        user_id, password_hash, role_id, status = user_data
        
        # 2. Verificar si la cuenta está deshabilitada
        if status == 'disabled':
            return jsonify({'message': 'Tu cuenta ha sido deshabilitada. Por favor, contacta con el soporte.'}), 401
        
        # 3. Verificar el password
        if bcrypt.check_password_hash(password_hash, password):
            # Generar el token JWT con el user_id como identidad
            access_token = create_access_token(identity=user_id)
            
            return jsonify({
                'token': access_token,
                'role_id': role_id
            }), 200
        
        return jsonify({'message': 'Email o contraseña incorrectos'}), 401
        
    except Exception as e:
        print(f"Error en el login: {e}")
        return jsonify({'message': 'Error interno del servidor'}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'Sesión cerrada con éxito. Por favor, borra tu token en el lado del cliente.'}), 200

# --- POST /api/admin/inject_coins: Permite al superusuario (Banco de Reserva) crear o retirar monedas del sistema. ---
# app.py

# ... (código anterior)

@app.route('/api/admin/inject_coins', methods=['POST'])
@jwt_required()
def inject_or_retire_coins():
    current_user_id = get_jwt_identity()
    
    data = request.json
    amount = data.get('amount')
    action = data.get('action')
    notes = data.get('notes', f'{action} de monedas por superadministrador')

    if not all([amount, action]):
        return jsonify({'message': 'Se requiere un monto y una acción (create/retire).'}), 400

    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({'message': 'El monto debe ser un número positivo.'}), 400

    if action not in ['create', 'retire']:
        return jsonify({'message': 'La acción debe ser "create" o "retire".'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500

    try:
        cursor = conn.cursor()
        
        # 1. Verificar el rol del usuario autenticado
        cursor.execute("SELECT role_id FROM users WHERE user_id = %s;", (str(current_user_id),))
        role_id = cursor.fetchone()[0]

        if role_id != 1:
            return jsonify({'message': 'Permiso denegado. Solo el superusuario puede realizar esta acción.'}), 403

        # 2. Obtener el account_id del usuario actual (superadministrador)
        cursor.execute("SELECT account_id, balance FROM accounts WHERE user_id = %s::uuid;", (current_user_id,))
        admin_account_info = cursor.fetchone()
        
        if not admin_account_info:
            return jsonify({'message': 'No se encontró la cuenta del administrador.'}), 404

        admin_account_id = admin_account_info[0]
        admin_balance = admin_account_info[1]
        
        # 💡 ¡CORRECCIÓN AQUÍ! Se ha eliminado la línea conn.begin()
        
        if action == 'retire':
            if admin_balance < amount:
                conn.rollback()
                return jsonify({'message': 'Fondos insuficientes en su cuenta para retirar esta cantidad.'}), 400
            
            cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s;", (amount, admin_account_id))
            
            transaction_query = "INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_type, status, notes) VALUES (%s, %s, %s, 'coin_retired', 'completed', %s);"
            cursor.execute(transaction_query, (admin_account_id, None, amount, notes))

        elif action == 'create':
            cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s;", (amount, admin_account_id))
            
            transaction_query = "INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_type, status, notes) VALUES (%s, %s, %s, 'coin_created', 'completed', %s);"
            cursor.execute(transaction_query, (None, admin_account_id, amount, notes))

        conn.commit()
        return jsonify({'message': f'{amount} monedas {action}das con éxito.'}), 200

    except psycopg2.errors.InsufficientPrivilege as e:
        conn.rollback()
        return jsonify({'message': 'Permisos de base de datos insuficientes.'}), 500

    except psycopg2.Error as err:
        conn.rollback()
        print(f"Error en la operación de monedas: {err}")
        return jsonify({'message': 'Error en la operación de monedas. Contacte al administrador.'}), 500
    
    except Exception as e:
        conn.rollback()
        print(f'Un error inesperado ocurrió: {str(e)}')
        return jsonify({'message': f'Un error inesperado ocurrió: {str(e)}'}), 500

    finally:
        if conn:
            cursor.close()
            conn.close()

# app.py

@app.route('/api/transactions/transfer', methods=['POST'])
@jwt_required()
def transfer_coins():
    current_user_id = get_jwt_identity()
    
    data = request.json
    to_user_id = data.get('to_user_id') # 💡 Se espera el user_id del destinatario
    amount = data.get('amount')
    notes = data.get('notes', 'Transferencia entre usuarios')

    if not all([to_user_id, amount]):
        return jsonify({'message': 'Se requiere el ID del usuario de destino y un monto.'}), 400
    
    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({'message': 'El monto debe ser un número positivo.'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500
    
    try:
        cursor = conn.cursor()
        
        # 1. Obtener la cuenta de origen del usuario autenticado y verificar el saldo
        from_account_query = "SELECT account_id, balance FROM accounts WHERE user_id = %s::uuid;"
        cursor.execute(from_account_query, (current_user_id,))
        from_account_info = cursor.fetchone()
        
        if not from_account_info:
            conn.rollback()
            return jsonify({'message': 'No se encontró la cuenta de origen para el usuario autenticado.'}), 404
            
        from_account_id = from_account_info[0]
        from_balance = from_account_info[1]

        # 2. Verificar que haya fondos suficientes
        if from_balance < amount:
            conn.rollback()
            return jsonify({'message': 'Fondos insuficientes en la cuenta de origen.'}), 400

        # 3. Obtener el account_id de destino a partir del to_user_id
        to_account_query = "SELECT account_id FROM accounts WHERE user_id = %s::uuid;"
        cursor.execute(to_account_query, (to_user_id,))
        to_account_data = cursor.fetchone()
        
        if not to_account_data:
            conn.rollback()
            return jsonify({'message': f'No se encontró una cuenta para el usuario con ID {to_user_id}.'}), 404
        
        to_account_id = to_account_data[0]

        # 4. Realizar la transferencia (mismo código de antes)
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s::uuid;", (amount, from_account_id))
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s::uuid;", (amount, to_account_id))
        
        transaction_query = "INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_type, status, notes) VALUES (%s::uuid, %s::uuid, %s, 'transfer', 'completed', %s);"
        cursor.execute(transaction_query, (from_account_id, to_account_id, amount, notes))

        conn.commit()
        return jsonify({'message': 'Transferencia realizada con éxito.'}), 200

    except Exception as e:
        conn.rollback()
        print(f'Un error inesperado ocurrió: {str(e)}')
        return jsonify({'message': f'Un error inesperado ocurrió: {str(e)}'}), 500
    
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    app.run(debug=True)