from flask import Flask, request, jsonify
import mysql.connector
import bcrypt
import datetime
from functools import wraps
import jwt

# --- Configuración de la aplicación y la base de datos ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'una_clave_secreta_fuerte'  # ¡Cámbiala en producción!

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
            try:
                token = request.headers['Authorization'].split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Formato de token no válido'}), 401

        if not token:
            return jsonify({'message': 'Token de autenticación faltante'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user_id = data['user_id']
            current_role_id = data['role_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token ha expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token no es válido'}), 401
        except Exception as e:
            return jsonify({'message': f'Error de autenticación: {e}'}), 401

        return f(current_user_id, current_role_id, *args, **kwargs)
    return decorated

def roles_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated_function(current_user_id, current_role_id, *args, **kwargs):
            if current_role_id not in allowed_roles:
                return jsonify({'message': 'Acceso no autorizado'}), 403
            return f(current_user_id, current_role_id, *args, **kwargs)
        return decorated_function
    return decorator

# --- Endpoints de la API ---

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    phone_number = data.get('phone_number')
    role_id = data.get('role_id', 3)  # Por defecto, rol de estudiante (3)

    if not all([username, email, password]):
        return jsonify({'message': 'Nombre de usuario, email y contraseña son obligatorios'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # 1. Insertar en la tabla 'users'
            user_query = "INSERT INTO users (username, email, password_hash, phone_number, role_id) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(user_query, (username, email, hashed_password, phone_number, role_id))
            new_user_id = cursor.lastrowid
            
            # 2. Crear una cuenta en la tabla 'accounts' con saldo 0
            account_query = "INSERT INTO accounts (user_id, balance) VALUES (%s, %s)"
            cursor.execute(account_query, (new_user_id, 0.00))

            # 3. Crear un perfil en la tabla 'user_profiles'
            profile_query = "INSERT INTO user_profiles (user_id) VALUES (%s)"
            cursor.execute(profile_query, (new_user_id,))

            conn.commit()
            return jsonify({'message': 'Usuario, perfil y cuenta registrados con éxito!'}), 201
        except mysql.connector.Error as err:
            conn.rollback()
            if err.errno == 1062: # Error de duplicado
                return jsonify({'message': 'El usuario, email o número de teléfono ya existen.'}), 409
            return jsonify({'message': f'Error al registrar usuario: {err.msg}'}), 500
        finally:
            cursor.close()
            conn.close()
    return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500

@app.route('/api/auth/login', methods=['POST'])
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
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                }, app.config['SECRET_KEY'], algorithm="HS256")
                return jsonify({'token': token, 'role_id': user['role_id']}), 200
            
            return jsonify({'message': 'Credenciales incorrectas'}), 401
        except mysql.connector.Error as err:
            return jsonify({'message': f'Error en el login: {err.msg}'}), 500
        finally:
            cursor.close()
            conn.close()
    return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500

# --- Nuevas APIs consolidadas para el perfil de usuario ---

# GET /api/users/<user_id> - Obtiene la información completa del usuario (perfil y cuenta)
@app.route('/api/users/<int:user_id>', methods=['GET'])
@token_required
def get_user_details(current_user_id, current_role_id, user_id):
    """
    Obtiene el perfil completo y los datos de la cuenta de un usuario específico.
    Solo el usuario dueño o un rol de administrador puede ver estos datos.
    """
    # Verificación de permisos para que un usuario solo pueda ver su propio perfil
    # a menos que tenga un rol de admin o superadmin.
    if current_user_id != user_id and current_role_id not in [1, 2]:
        return jsonify({'message': 'No tienes permiso para ver este perfil'}), 403

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Consulta para obtener los datos del usuario, perfil y cuenta en una sola llamada.
        # Se usa LEFT JOIN por si un usuario no tiene datos de perfil o cuenta por algún error.
        query = """
        SELECT
            u.user_id, u.username, u.email, u.phone_number, u.role_id,
            up.first_name, up.last_name, up.birth_date, up.profile_picture_url,
            a.balance
        FROM users u
        LEFT JOIN user_profiles up ON u.user_id = up.user_id
        LEFT JOIN accounts a ON u.user_id = a.user_id
        WHERE u.user_id = %s
        """
        cursor.execute(query, (user_id,))
        user_data = cursor.fetchone()

        if user_data:
            return jsonify(user_data), 200
        return jsonify({'message': 'Usuario no encontrado'}), 404

    except mysql.connector.Error as err:
        return jsonify({'message': f'Error al obtener los datos del usuario: {err.msg}'}), 500
    finally:
        cursor.close()
        conn.close()

# PUT /api/users/<user_id> - Actualiza la información de perfil
@app.route('/api/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user_profile(current_user_id, current_role_id, user_id):
    """
    Actualiza la información de perfil de un usuario.
    Solo el usuario dueño o un rol de administrador puede actualizar.
    """
    # Permisos
    if current_user_id != user_id and current_role_id not in [1, 2]:
        return jsonify({'message': 'No tienes permiso para actualizar este perfil'}), 403

    data = request.json
    
    # Listas para guardar las actualizaciones de cada tabla
    user_updates = []
    user_params = []
    profile_updates = []
    profile_params = []

    # Construir las actualizaciones para la tabla 'users'
    if 'username' in data:
        user_updates.append("username = %s")
        user_params.append(data['username'])
    if 'phone_number' in data:
        user_updates.append("phone_number = %s")
        user_params.append(data['phone_number'])

    # Construir las actualizaciones para la tabla 'user_profiles'
    if 'first_name' in data:
        profile_updates.append("first_name = %s")
        profile_params.append(data['first_name'])
    if 'last_name' in data:
        profile_updates.append("last_name = %s")
        profile_params.append(data['last_name'])
    if 'profile_picture_url' in data:
        profile_updates.append("profile_picture_url = %s")
        profile_params.append(data['profile_picture_url'])
        
    # Verificar si hay algo para actualizar
    if not user_updates and not profile_updates:
        return jsonify({'message': 'No se proporcionaron campos para actualizar'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500

    cursor = conn.cursor()
    try:
        conn.start_transaction()
        rows_affected = 0
        
        # Ejecutar la consulta para la tabla 'users' si hay campos a actualizar
        if user_updates:
            user_query = "UPDATE users SET " + ", ".join(user_updates) + " WHERE user_id = %s"
            user_params.append(user_id)
            cursor.execute(user_query, tuple(user_params))
            rows_affected += cursor.rowcount
        
        # Ejecutar la consulta para la tabla 'user_profiles' si hay campos a actualizar
        if profile_updates:
            profile_query = "UPDATE user_profiles SET " + ", ".join(profile_updates) + " WHERE user_id = %s"
            profile_params.append(user_id)
            cursor.execute(profile_query, tuple(profile_params))
            rows_affected += cursor.rowcount

        conn.commit()
        
        if rows_affected == 0:
            return jsonify({'message': 'Usuario no encontrado o sin cambios'}), 404

        return jsonify({'message': 'Perfil actualizado con éxito!'}), 200

    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'message': f'Error al actualizar el perfil: {err.msg}'}), 500
    finally:
        cursor.close()
        conn.close()

# Endpoint para listar todos los usuarios (solo para administradores)
@app.route('/api/users', methods=['GET'])
@roles_required([1, 2])
def list_all_users(current_user_id, current_role_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT user_id, username, email, phone_number, role_id FROM users"
            cursor.execute(query)
            users = cursor.fetchall()
            return jsonify(users), 200
        finally:
            cursor.close()
            conn.close()
    return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500

# --- GET /api/accounts/<account_id>: Obtiene el saldo y el estado de una cuenta. ---
@app.route('/api/accounts/<int:account_id>', methods=['GET'])
@token_required
def get_user_account(current_user_id, current_role_id, account_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Primero, obtén el user_id de la cuenta solicitada
        cursor.execute("SELECT user_id FROM accounts WHERE account_id = %s", (account_id,))
        account_info = cursor.fetchone()

        if not account_info:
            return jsonify({'message': 'Cuenta no encontrada'}), 404

        requested_user_id = account_info['user_id']
        
        # Validación de permisos: Solo el dueño de la cuenta, un admin o superusuario pueden acceder.
        if current_user_id != requested_user_id and current_role_id not in [1, 2]:
            return jsonify({'message': 'No tienes permiso para ver esta cuenta'}), 403

        # Si el permiso es válido, obtén los detalles completos de la cuenta
        cursor.execute("SELECT * FROM accounts WHERE account_id = %s", (account_id,))
        account_details = cursor.fetchone()
        
        return jsonify(account_details), 200

    except mysql.connector.Error as err:
        return jsonify({'message': f'Error al obtener la cuenta: {err.msg}'}), 500
    finally:
        cursor.close()
        conn.close()

# --- POST /api/transactions/transfer: Permite a un usuario transferir monedas a otro.  ---
@app.route('/api/transactions/transfer', methods=['POST'])
@token_required
def transfer_coins(current_user_id, current_role_id):
    data = request.json
    from_account_id = data.get('from_account_id')
    to_account_id = data.get('to_account_id')
    amount = data.get('amount')
    notes = data.get('notes', 'Transferencia entre usuarios')

    if not all([from_account_id, to_account_id, amount]):
        return jsonify({'message': 'Se requieren from_account_id, to_account_id y amount.'}), 400
    
    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({'message': 'El monto debe ser un número positivo.'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500
    
    cursor = conn.cursor()
    
    try:
        # 1. Verificar que la cuenta de origen pertenezca al usuario autenticado
        cursor.execute("SELECT user_id, balance FROM accounts WHERE account_id = %s", (from_account_id,))
        from_account_info = cursor.fetchone()
        
        if not from_account_info:
            return jsonify({'message': 'La cuenta de origen no existe.'}), 404
            
        from_user_id = from_account_info[0]
        from_balance = from_account_info[1]
        
        if from_user_id != current_user_id:
            return jsonify({'message': 'No tienes permiso para transferir desde esta cuenta.'}), 403

        # 2. Verificar que la cuenta de destino exista
        cursor.execute("SELECT account_id FROM accounts WHERE account_id = %s", (to_account_id,))
        to_account_exists = cursor.fetchone()
        
        if not to_account_exists:
            return jsonify({'message': 'La cuenta de destino no existe.'}), 404

        # 3. Verificar que haya fondos suficientes
        if from_balance < amount:
            return jsonify({'message': 'Fondos insuficientes en la cuenta de origen.'}), 400

        # 4. Realizar la transferencia (operaciones atómicas)
        
        # A. Restar el monto de la cuenta de origen
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, from_account_id))
        
        # B. Sumar el monto a la cuenta de destino
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, to_account_id))
        
        # C. Registrar la transacción en la tabla 'transactions'
        transaction_query = "INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_type, status, notes) VALUES (%s, %s, %s, 'transfer', 'completed', %s)"
        cursor.execute(transaction_query, (from_account_id, to_account_id, amount, notes))

        conn.commit()
        return jsonify({'message': 'Transferencia realizada con éxito.'}), 200

    except mysql.connector.Error as err:
        conn.rollback() # Revierte todos los cambios si hay un error
        return jsonify({'message': f'Error en la transferencia: {err.msg}'}), 500
    finally:
        cursor.close()
        conn.close()

# --- GET /api/transactions/history/<account_id>: Muestra el historial de transacciones de una cuenta específica. ---
@app.route('/api/transactions/history/<int:account_id>', methods=['GET'])
@token_required
def get_transaction_history(current_user_id, current_role_id, account_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Primero, verifica la propiedad de la cuenta para seguridad
        cursor.execute("SELECT user_id FROM accounts WHERE account_id = %s", (account_id,))
        account_info = cursor.fetchone()

        if not account_info:
            return jsonify({'message': 'Cuenta no encontrada'}), 404

        requested_user_id = account_info['user_id']

        # Validación de permisos
        if current_user_id != requested_user_id and current_role_id not in [1, 2]:
            return jsonify({'message': 'No tienes permiso para ver este historial'}), 403

        # Obtener el historial de transacciones para la cuenta
        query = """
            SELECT
                transaction_id,
                from_account_id,
                to_account_id,
                amount,
                transaction_type,
                status,
                notes,
                created_at
            FROM transactions
            WHERE from_account_id = %s OR to_account_id = %s
            ORDER BY created_at DESC
        """
        cursor.execute(query, (account_id, account_id))
        transactions = cursor.fetchall()
        
        return jsonify(transactions), 200

    except mysql.connector.Error as err:
        return jsonify({'message': f'Error al obtener el historial de transacciones: {err.msg}'}), 500
    finally:
        cursor.close()
        conn.close()

# --- * POST /api/loans: Permite a los usuarios solicitar un préstamo o a los administradores otorgarlo. ---
@app.route('/api/loans/request', methods=['POST'])
@roles_required([3])  # Solo rol de estudiante (3)
def request_loan(current_user_id, current_role_id):
    data = request.json
    amount = data.get('amount')
    reason = data.get('reason', 'Préstamo solicitado por estudiante')

    # Tasa de interés predeterminada (cambiada a 10.0)
    interest_rate = 10.0
    # Fecha de vencimiento, 30 días después
    due_date = datetime.datetime.now() + datetime.timedelta(days=30)

    # Validación del monto
    if not amount or not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({'message': 'Se requiere un monto válido.'}), 400

    # Conexión a la base de datos
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500

    cursor = conn.cursor()
    try:
        # Obtener información de la cuenta del usuario
        cursor.execute("SELECT account_id FROM accounts WHERE user_id = %s", (current_user_id,))
        account_info = cursor.fetchone()

        if not account_info:
            return jsonify({'message': 'No se encontró la cuenta del usuario.'}), 404

        borrower_account_id = account_info[0]

        # Consulta para insertar el préstamo
        loan_query = """
            INSERT INTO loans (lender_account_id, borrower_account_id, amount, interest_rate, due_date, status, reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(loan_query, (None, borrower_account_id, amount, interest_rate, due_date, 'pending', reason))

        # Confirmar la transacción
        conn.commit()
        return jsonify({'message': 'Solicitud de préstamo enviada para aprobación.'}), 201

    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'message': f'Error al procesar la solicitud de préstamo: {err.msg}'}), 500

    finally:
        cursor.close()
        conn.close()

# --- POST /api/loans/evaluate: verificar la elegibilidad de una solicitud de préstamo pendiente. Si el usuario es apto, la API puede aprobarlo o rechazarlo. ---
# --- Endpoint de la API ---
@app.route('/api/loans/evaluate', methods=['POST'])
@roles_required([1, 2]) # Solo para superadmin (1) y admin (2)
def evaluate_loan_request(current_user_id, current_role_id):
    data = request.json
    loan_id = data.get('loan_id')
    action = data.get('action') # 'approve' o 'reject'
    rejection_reason = data.get('rejection_reason', 'Motivo no especificado.')

    if not loan_id or action not in ['approve', 'reject']:
        return jsonify({'message': 'Se requiere loan_id y una acción ("approve" o "reject").'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500

    cursor = conn.cursor()
    try:
        conn.start_transaction()
        
        # Obtener los detalles de la solicitud de préstamo
        cursor.execute("SELECT borrower_account_id, amount, status FROM loans WHERE loan_id = %s", (loan_id,))
        loan = cursor.fetchone()

        if not loan:
            return jsonify({'message': 'Solicitud de préstamo no encontrada.'}), 404
        
        borrower_account_id, loan_amount, loan_status = loan

        if loan_status != 'pending':
            return jsonify({'message': f'El préstamo ya ha sido {loan_status}.'}), 400

        if action == 'approve':
            # --- Lógica de VERIFICACIÓN de elegibilidad antes de aprobar ---
            eligibility_query = "SELECT loan_id FROM loans WHERE borrower_account_id = %s AND status IN ('approved', 'partially_paid', 'overdue')"
            cursor.execute(eligibility_query, (borrower_account_id,))
            
            existing_loan = cursor.fetchone()
            if existing_loan:
                # Si el usuario ya tiene un préstamo activo, se rechaza la nueva solicitud
                rejection_reason_auto = 'El solicitante ya tiene un préstamo activo o parcialmente pagado.'
                
                # 1. Actualizar el estado del préstamo a rechazado
                cursor.execute("UPDATE loans SET status = 'rejected' WHERE loan_id = %s", (loan_id,))
                
                # 2. Registrar el rechazo en la tabla `loan_rejections`
                rejection_query = "INSERT INTO loan_rejections (loan_id, rejected_by_user_id, reason) VALUES (%s, %s, %s)"
                cursor.execute(rejection_query, (loan_id, current_user_id, rejection_reason_auto))
                
                conn.commit()
                return jsonify({'message': rejection_reason_auto}), 400

            # --- Lógica de APROBACIÓN (si el usuario es elegible) ---
            
            # Obtener el account_id del administrador para usarlo como 'from_account_id' y 'lender_account_id'
            cursor.execute("SELECT account_id FROM accounts WHERE user_id = %s", (current_user_id,))
            lender_account_id = cursor.fetchone()[0]

            # 1. Actualizar el estado del préstamo y el `lender_account_id`
            cursor.execute("UPDATE loans SET status = 'approved', lender_account_id = %s WHERE loan_id = %s", (lender_account_id, loan_id))
            
            # 2. Aumentar el saldo del usuario (prestatario)
            cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (loan_amount, borrower_account_id))
            
            # 3. Registrar la transacción en la tabla 'transactions'
            transaction_query = "INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_type, status, notes) VALUES (%s, %s, %s, 'loan_approved', 'completed', 'Préstamo aprobado')"
            cursor.execute(transaction_query, (lender_account_id, borrower_account_id, loan_amount))

            conn.commit()
            return jsonify({'message': 'Préstamo aprobado y fondos transferidos con éxito.'}), 200

        elif action == 'reject':
            # Lógica de rechazo:
            # 1. Actualizar el estado del préstamo
            cursor.execute("UPDATE loans SET status = 'rejected' WHERE loan_id = %s", (loan_id,))

            # 2. Registrar el rechazo en la nueva tabla `loan_rejections`
            rejection_query = "INSERT INTO loan_rejections (loan_id, rejected_by_user_id, reason) VALUES (%s, %s, %s)"
            cursor.execute(rejection_query, (loan_id, current_user_id, rejection_reason))

            conn.commit()
            return jsonify({'message': 'Préstamo rechazado con éxito.'}), 200

    except mysql.connector.Error as err:
        conn.rollback() # Revierte todos los cambios si hay un error
        return jsonify({'message': f'Error al evaluar la solicitud de préstamo: {err.msg}'}), 500
    finally:
        cursor.close()
        conn.close()

# --- GET /api/loans/<loan_id>: Obtiene detalles de un préstamo. ---
@app.route('/api/loans/<int:loan_id>', methods=['GET'])
@token_required
def get_loan_details(current_user_id, current_role_id, loan_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        # Tu consulta SQL que trae todos los campos
        query = "SELECT loan_id, lender_account_id, borrower_account_id, amount, interest_rate, due_date, status, reason, created_at FROM loans WHERE loan_id = %s"
        cursor.execute(query, (loan_id,))
        loan = cursor.fetchone()

        if not loan:
            return jsonify({'message': 'Préstamo no encontrado'}), 404

        # ... (código de validación de permisos)

        # --- Lógica de cálculo corregida ---
        principal_amount = float(loan['amount'])
        interest_rate = float(loan['interest_rate'])
        
        # Corrección: Convertir la fecha de la base de datos a un objeto datetime
        # Si la base de datos devuelve un string como "Tue, 26 Aug 2025 20:05:24 GMT"
        # Usa strptime con el formato correcto.
        if isinstance(loan['created_at'], str):
            created_at = datetime.datetime.strptime(loan['created_at'], "%a, %d %b %Y %H:%M:%S GMT")
        else:
            # Si el conector devuelve un objeto datetime, no se necesita conversión
            created_at = loan['created_at']

        # Calcular los días transcurridos
        days_passed = (datetime.datetime.now() - created_at).days
        
        # ... (resto de tu lógica de cálculo)
        total_interest = (principal_amount * interest_rate / 100) * (days_passed / 365.0)
        total_debt = principal_amount + total_interest

        # Obtener el total de pagos realizados para este préstamo
        payment_query = "SELECT SUM(amount_paid) as total_paid FROM loan_payments WHERE loan_id = %s"
        cursor.execute(payment_query, (loan_id,))
        total_paid_result = cursor.fetchone()
        
        # Asegurarse de que el total de pagos es un float antes de la operación
        total_paid_so_far = float(total_paid_result['total_paid']) if total_paid_result and total_paid_result['total_paid'] else 0.0
        
        # Agregar los nuevos campos al objeto de respuesta
        loan['total_debt'] = round(total_debt, 2)
        loan['total_paid'] = round(total_paid_so_far, 2)
        loan['remaining_debt'] = round(total_debt - total_paid_so_far, 2)

        return jsonify(loan), 200

    except Exception as e:
        return jsonify({'message': f'Un error inesperado ocurrió: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

# --- POST /api/loans/repay: Permite a los usuarios pagar una parte o la totalidad de su préstamo. ---
# --- Endpoint de la API ---
@app.route('/api/loans/repay', methods=['POST'])
@token_required
def repay_loan(current_user_id, current_role_id):
    data = request.json
    loan_id = data.get('loan_id')
    amount_paid = data.get('amount_paid')

    if not all([loan_id, amount_paid]):
        return jsonify({'message': 'Se requiere el loan_id y el monto a pagar.'}), 400

    if not isinstance(amount_paid, (int, float)) or amount_paid <= 0:
        return jsonify({'message': 'El monto a pagar debe ser un número positivo.'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Fallo en la conexión a la base de datos'}), 500

    cursor = conn.cursor()
    
    try:
        conn.start_transaction()
        
        # 1. Obtener los detalles del préstamo y del prestatario
        loan_query = "SELECT borrower_account_id, amount, status FROM loans WHERE loan_id = %s"
        cursor.execute(loan_query, (loan_id,))
        loan = cursor.fetchone()

        if not loan:
            return jsonify({'message': 'Préstamo no encontrado.'}), 404
        
        borrower_account_id, loan_amount, loan_status = loan

        if loan_status not in ['approved', 'partially_paid', 'overdue']:
            return jsonify({'message': 'Este préstamo no está activo para pagos.'}), 400

        # Obtener el user_id del prestatario
        cursor.execute("SELECT user_id, balance FROM accounts WHERE account_id = %s", (borrower_account_id,))
        borrower_info = cursor.fetchone()
        
        if borrower_info[0] != current_user_id:
            return jsonify({'message': 'No tienes permiso para pagar este préstamo.'}), 403

        # Convertir a float para las operaciones
        borrower_balance = float(borrower_info[1])

        # 2. Verificar si hay fondos suficientes
        if borrower_balance < amount_paid:
            return jsonify({'message': 'Fondos insuficientes en su cuenta para realizar el pago.'}), 400

        # 3. Calcular el monto total pagado hasta ahora
        # La consulta debe usar 'amount_paid' si esa es la columna en tu tabla
        cursor.execute("SELECT SUM(amount_paid) FROM loan_payments WHERE loan_id = %s", (loan_id,))
        total_paid_so_far = cursor.fetchone()[0] or 0.0

        new_total_paid = float(total_paid_so_far) + amount_paid
        
        # Convertir loan_amount a float para que la resta sea compatible
        remaining_balance = float(loan_amount) - new_total_paid

        # 4. Actualizar saldos y registrar el pago
        
        # A. Restar el monto del saldo del prestatario
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount_paid, borrower_account_id))
        
        # B. Registrar el pago en la tabla 'loan_payments'
        payment_query = "INSERT INTO loan_payments (loan_id, amount_paid, status) VALUES (%s, %s, 'completed')"
        cursor.execute(payment_query, (loan_id, amount_paid))

        # 5. Actualizar el estado del préstamo
        if new_total_paid >= float(loan_amount):
            loan_status = 'fully_paid'
            cursor.execute("UPDATE loans SET status = 'fully_paid' WHERE loan_id = %s", (loan_id,))
            message = 'Préstamo pagado en su totalidad. ¡Felicidades!'
        else:
            loan_status = 'partially_paid'
            cursor.execute("UPDATE loans SET status = 'partially_paid' WHERE loan_id = %s", (loan_id,))
            message = f'Pago parcial de préstamo exitoso. Saldo restante: {remaining_balance:.2f}'
        
        conn.commit()
        return jsonify({'message': message, 'new_loan_status': loan_status, 'remaining_balance': remaining_balance}), 200

    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'message': f'Error al procesar el pago del préstamo: {err.msg}'}), 500
    finally:
        cursor.close()
        conn.close()

# --- POST /api/admin/inject_coins: Permite al superusuario (Banco de Reserva) crear o retirar monedas del sistema. ---
@app.route('/api/admin/inject_coins', methods=['POST'])
@roles_required([1])  # Solo para superadministrador (1)
def inject_or_retire_coins(current_user_id, current_role_id):
    data = request.json
    amount = data.get('amount')
    action = data.get('action') # 'create' o 'retire'
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

    cursor = conn.cursor()
    try:
        conn.start_transaction()
        
        # Obtener el account_id del usuario actual (superadministrador)
        cursor.execute("SELECT account_id, balance FROM accounts WHERE user_id = %s", (current_user_id,))
        admin_account_info = cursor.fetchone()
        
        if not admin_account_info:
            return jsonify({'message': 'No se encontró la cuenta del administrador.'}), 404

        admin_account_id = admin_account_info[0]
        admin_balance = admin_account_info[1]
        
        # Lógica para 'retire'
        if action == 'retire':
            if admin_balance < amount:
                return jsonify({'message': 'Fondos insuficientes en su cuenta para retirar esta cantidad.'}), 400
            
            # Restar del saldo del administrador
            cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_id = %s", (amount, admin_account_id))
            
            # Registrar la transacción de retiro
            transaction_query = "INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_type, status, notes) VALUES (%s, %s, %s, 'coin_retired', 'completed', %s)"
            cursor.execute(transaction_query, (admin_account_id, None, amount, notes))

        # Lógica para 'create'
        elif action == 'create':
            # Aumentar el saldo del administrador
            cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_id = %s", (amount, admin_account_id))
            
            # Registrar la transacción de creación
            transaction_query = "INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_type, status, notes) VALUES (%s, %s, %s, 'coin_created', 'completed', %s)"
            cursor.execute(transaction_query, (None, admin_account_id, amount, notes))

        conn.commit()
        return jsonify({'message': f'{amount} monedas {action}das con éxito.'}), 200

    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'message': f'Error en la operación de monedas: {err.msg}'}), 500
    except Exception as e:
        conn.rollback()
        return jsonify({'message': f'Un error inesperado ocurrió: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
