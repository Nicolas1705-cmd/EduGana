from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity, unset_jwt_cookies
import psycopg2
from psycopg2.extras import RealDictCursor





# =====================================
# API: REGISTRAR USUARIO
# =====================================
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
if __name__ == "__main__":