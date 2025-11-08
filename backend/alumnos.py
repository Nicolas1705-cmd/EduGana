from flask import Flask, jsonify, request
from configbd import get_db_connection

app = Flask(__name__)

# --- 1️⃣ Agregar alumno ---
@app.route('/alumnos', methods=['POST'])
def agregar_alumno():
    data = request.get_json()

    required_fields = ['id_colegio', 'fecha_nacimiento', 'nombre', 'apellido', 'correo', 'telefono', 'nombre_apoderado', 'dni_apoderado']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "⚠️ Faltan campos requeridos"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "❌ Error de conexión BD"}), 500

    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Alumnos (id_colegio, fecha_nacimiento, nombre, apellido, correo, telefono, nombre_apoderado, dni_apoderado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_alumno;
        """, (
            data['id_colegio'],
            data['fecha_nacimiento'],
            data['nombre'],
            data['apellido'],
            data['correo'],
            data['telefono'],
            data['nombre_apoderado'],
            data['dni_apoderado']
        ))

        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "✅ Alumno registrado correctamente", "id_alumno": new_id}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"❌ Error al registrar alumno: {e}"}), 500


# --- 2️⃣ Eliminar alumno ---
@app.route('/alumnos/<int:id_alumno>', methods=['DELETE'])
def eliminar_alumno(id_alumno):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "❌ Error de conexión BD"}), 500

    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM Alumnos WHERE id_alumno = %s RETURNING id_alumno;", (id_alumno,))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if result:
            return jsonify({"message": f"✅ Alumno {id_alumno} eliminado"}), 200
        else:
            return jsonify({"error": "⚠️ Alumno no encontrado"}), 404

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"❌ Error al eliminar alumno: {e}"}), 500


# --- 3️⃣ Listar alumnos ---
@app.route('/alumnos', methods=['GET'])
def listar_alumnos():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "❌ Error de conexión BD"}), 500

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id_alumno, id_colegio, fecha_nacimiento, nombre, apellido, correo, telefono, nombre_apoderado, dni_apoderado
            FROM Alumnos
            ORDER BY id_alumno;
        """)

        rows = cur.fetchall()
        cur.close()
        conn.close()

        alumnos = []
        for r in rows:
            alumnos.append({
                "id_alumno": r[0],
                "id_colegio": r[1],
                "fecha_nacimiento": str(r[2]),
                "nombre": r[3],
                "apellido": r[4],
                "correo": r[5],
                "telefono": r[6],
                "nombre_apoderado": r[7],
                "dni_apoderado": r[8]
            })

        return jsonify(alumnos), 200

    except Exception as e:
        return jsonify({"error": f"❌ Error al listar alumnos: {e}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5002)
