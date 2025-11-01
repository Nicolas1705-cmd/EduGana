from flask import Flask, jsonify, request
from configbd import get_db_connection

app = Flask(__name__)

# --- 1️⃣ Agregar cupón ---
@app.route('/cupones', methods=['POST'])
def agregar_cupon():
    data = request.get_json()

    required_fields = ['id_alumno', 'puntos', 'fecha_entrega', 'descripcion']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "⚠️ Faltan campos requeridos"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "❌ Error de conexión BD"}), 500

    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Cupones (id_alumno, puntos, fecha_entrega, descripcion)
            VALUES (%s, %s, %s, %s)
            RETURNING id_cupon;
        """, (
            data['id_alumno'],
            data['puntos'],
            data['fecha_entrega'],
            data['descripcion']
        ))

        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "✅ Cupón creado correctamente", "id_cupon": new_id}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"❌ Error al crear cupón: {e}"}), 500


# --- 2️⃣ Eliminar cupón ---
@app.route('/cupones/<int:id_cupon>', methods=['DELETE'])
def eliminar_cupon(id_cupon):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "❌ Error de conexión BD"}), 500

    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM Cupones WHERE id_cupon = %s RETURNING id_cupon;", (id_cupon,))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if result:
            return jsonify({"message": f"🗑️ Cupón {id_cupon} eliminado"}), 200
        else:
            return jsonify({"error": "⚠️ Cupón no encontrado"}), 404

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"❌ Error al eliminar cupón: {e}"}), 500


# --- 3️⃣ Listar cupones ---
@app.route('/cupones', methods=['GET'])
def listar_cupones():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "❌ Error de conexión BD"}), 500

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id_cupon, id_alumno, puntos, fecha_entrega, descripcion
            FROM Cupones
            ORDER BY id_cupon;
        """)

        rows = cur.fetchall()
        cur.close()
        conn.close()

        cupones = []
        for r in rows:
            cupones.append({
                "id_cupon": r[0],
                "id_alumno": r[1],
                "puntos": r[2],
                "fecha_entrega": str(r[3]),
                "descripcion": r[4]
            })

        return jsonify(cupones), 200

    except Exception as e:
        return jsonify({"error": f"❌ Error al listar cupones: {e}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5003)
