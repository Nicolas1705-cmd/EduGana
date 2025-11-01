from flask import Flask, jsonify, request
from configbd import get_db_connection

app = Flask(__name__)

# --- 1️⃣ Registrar canje ---
@app.route('/canjes', methods=['POST'])
def registrar_canje():
    data = request.get_json()

    required_fields = ['id_alumno', 'id_tienda', 'puntos_usados', 'fecha_canje', 'detalle']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "⚠️ Faltan campos requeridos"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "❌ Error de conexión BD"}), 500

    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO HistorialCanjes (id_alumno, id_tienda, puntos_usados, fecha_canje, detalle)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_canjes;
        """, (
            data['id_alumno'],
            data['id_tienda'],
            data['puntos_usados'],
            data['fecha_canje'],
            data['detalle']
        ))

        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "✅ Canje registrado", "id_canjes": new_id}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"❌ Error al registrar canje: {e}"}), 500


# --- 2️⃣ Eliminar registro de canje ---
@app.route('/canjes/<int:id_canjes>', methods=['DELETE'])
def eliminar_canje(id_canjes):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "❌ Error de conexión BD"}), 500

    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM HistorialCanjes WHERE id_canjes = %s RETURNING id_canjes;", (id_canjes,))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if result:
            return jsonify({"message": f"🗑️ Canje {id_canjes} eliminado"}), 200
        else:
            return jsonify({"error": "⚠️ Canje no encontrado"}), 404

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"❌ Error al eliminar canje: {e}"}), 500


# --- 3️⃣ Listar historial de canjes ---
@app.route('/canjes', methods=['GET'])
def listar_canjes():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "❌ Error de conexión BD"}), 500

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id_canjes, id_alumno, id_tienda, puntos_usados, fecha_canje, detalle
            FROM HistorialCanjes
            ORDER BY id_canjes DESC;
        """)

        rows = cur.fetchall()
        cur.close()
        conn.close()

        canjes = []
        for r in rows:
            canjes.append({
                "id_canjes": r[0],
                "id_alumno": r[1],
                "id_tienda": r[2],
                "puntos_usados": r[3],
                "fecha_canje": str(r[4]),
                "detalle": r[5]
            })

        return jsonify(canjes), 200

    except Exception as e:
        return jsonify({"error": f"❌ Error al listar canjes: {e}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5004)
