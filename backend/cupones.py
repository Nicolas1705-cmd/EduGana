from flask import Flask, request, jsonify
from flask_cors import CORS
from configbd import get_db_connection

# --- 3️⃣ Listar cupones ---

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
