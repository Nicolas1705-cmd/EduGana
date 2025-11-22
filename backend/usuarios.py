from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    create_access_token, JWTManager,
    jwt_required, get_jwt_identity
)
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
bcrypt = Bcrypt(app)

# ============================
<<<<<<< HEAD
# CREDENCIALES (LAS TUYAS)
=======
# CONFIG JWT
# ============================
app.config["JWT_SECRET_KEY"] = "super-secret-key-2025"
jwt = JWTManager(app)

# ============================
# CREDENCIALES DE BASE DE DATOS
>>>>>>> df0d89b149c9061aa3af6f53bd50c4254491a377
# ============================
DB_NAME = "edugana_db"
DB_USER = "postgres"
DB_PASS = "System.2025*"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"

<<<<<<< HEAD
# JWT
app.config["JWT_SECRET_KEY"] = "cambia-este-secret"
jwt = JWTManager(app)

# ----------------------------
# Conexión a PostgreSQL
# ----------------------------
def get_conn():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )

# ======================================================
#   📌 1. Registrar asistencia
# ======================================================
@app.route("/asistencias", methods=["POST"])
@jwt_required()
def registrar_asistencia():
    data = request.get_json()

    estudiante_id = data.get("estudiante_id")
    nombre_estudiante = data.get("nombre_estudiante")
    fecha = data.get("fecha")
    asistencia = data.get("asistencia")
    hora_entrada = data.get("hora_entrada")
    observaciones = data.get("observaciones")

    try:
        conn = get_conn()
        cur = conn.cursor()

        query = """
            INSERT INTO asistencias (
                estudiante_id, nombre_estudiante, fecha,
                asistencia, hora_entrada, observaciones
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        cur.execute(query, (
            estudiante_id, nombre_estudiante, fecha,
            asistencia, hora_entrada, observaciones
        ))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"msg": "Asistencia registrada exitosamente"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
#   📌 2. Obtener historial completo
# ======================================================
@app.route("/asistencias", methods=["GET"])
@jwt_required()
def obtener_asistencias():
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT * FROM asistencias ORDER BY fecha DESC;")
        data = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
#   📌 3. Historial por estudiante
# ======================================================
@app.route("/asistencias/estudiante/<int:estudiante_id>", methods=["GET"])
@jwt_required()
def asistencias_por_estudiante(estudiante_id):
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT * FROM asistencias WHERE estudiante_id = %s ORDER BY fecha DESC;", (estudiante_id,))
        data = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
#   📌 4. Historial por fecha
# ======================================================
@app.route("/asistencias/fecha/<fecha>", methods=["GET"])
@jwt_required()
def asistencias_por_fecha(fecha):
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT * FROM asistencias WHERE fecha = %s;", (fecha,))
        data = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
#   📌 5. Actualizar asistencia
# ======================================================
@app.route("/asistencias/<int:id>", methods=["PUT"])
@jwt_required()
def actualizar_asistencia(id):
    data = request.get_json()

    try:
        conn = get_conn()
        cur = conn.cursor()

        query = """
            UPDATE asistencias SET
            estudiante_id=%s,
            nombre_estudiante=%s,
            fecha=%s,
            asistencia=%s,
            hora_entrada=%s,
            observaciones=%s
            WHERE id=%s
        """

        cur.execute(query, (
            data.get("estudiante_id"),
            data.get("nombre_estudiante"),
            data.get("fecha"),
            data.get("asistencia"),
            data.get("hora_entrada"),
            data.get("observaciones"),
            id
        ))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"msg": "Asistencia actualizada"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
#   📌 6. Eliminar asistencia
# ======================================================
@app.route("/asistencias/<int:id>", methods=["DELETE"])
@jwt_required()
def eliminar_asistencia(id):
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("DELETE FROM asistencias WHERE id = %s;", (id,))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"msg": "Asistencia eliminada"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ======================================================
#   RUN SERVER
# ======================================================
=======
# Conexión a PostgreSQL
def get_db():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT,
        cursor_factory=RealDictCursor
    )

# =====================================
# API: REGISTRAR USUARIO
# =====================================
@app.route("/api/registrarUsuario", methods=["POST"])
def registrar_usuario():
    try:
        data = request.get_json()

        nombre = data.get("nombre_usuario")
        apellido = data.get("apellido_usuario")
        correo = data.get("correo")
        contraseña = data.get("contrasena")

        if not nombre or not apellido or not correo or not contrasena:
            return jsonify({"mensaje": "Todos los campos son obligatorios"}), 400

        conn = get_db()
        cur = conn.cursor()

        # Verificar si correo ya está registrado
        cur.execute("SELECT * FROM registodeusuario WHERE correo = %s", (correo,))
        existe = cur.fetchone()
        if existe:
            return jsonify({"mensaje": "El correo ya está registrado"}), 400

        # Encriptar contraseña
        hash_pw = bcrypt.generate_password_hash(contrasena).decode('utf-8')

        # Insertar usuario
        cur.execute("""
            INSERT INTO registodeusuario (nombre_usuario, apellido_usuario, correo, contrasena)
            VALUES (%s, %s, %s, %s) RETURNING id_usuario;
        """, (nombre, apellido, correo, hash_pw))

        conn.commit()
        user_id = cur.fetchone()["id_usuario"]

        cur.close()
        conn.close()

        return jsonify({
            "mensaje": "Usuario registrado exitosamente",
            "id_usuario": user_id
        }), 201

    except Exception as e:
        print("Error:", e)
        return jsonify({"mensaje": "Error en el servidor"}), 500


# =====================================
# API: LOGIN
# =====================================
@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.json

        correo = data.get("correo")
        contraseña = data.get("contrasena")

        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM registodeusuario WHERE correo = %s", (correo,))
        user = cur.fetchone()

        if not user:
            return jsonify({"mensaje": "Correo no registrado"}), 400

        # Validar contraseña
        if not bcrypt.check_password_hash(user["contrasena"], contraseña):
            return jsonify({"mensaje": "Contraseña incorrecta"}), 400

        token = create_access_token(identity=user["id_usuario"])

        cur.close()
        conn.close()

        return jsonify({
            "mensaje": "Login exitoso",
            "token": token
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"mensaje": "Error en el servidor"}), 500


# =====================================
# API: PERFIL (PROTEGIDO CON JWT)
# =====================================
@app.route("/api/perfil", methods=["GET"])
@jwt_required()
def perfil():
    user_id = get_jwt_identity()

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id_usuario, nombre_usuario, apellido_usuario, correo FROM registodeusuario WHERE id_usuario = %s", (user_id,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    return jsonify(user)


# =====================================
# RUN SERVER
# =====================================
>>>>>>> df0d89b149c9061aa3af6f53bd50c4254491a377
if __name__ == "__main__":
    app.run(debug=True)
