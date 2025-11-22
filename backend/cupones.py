from flask import Flask, jsonify
from flask_cors import CORS
from configbd import get_db_connection


# --- Listar cupones ---
def listar_cupones():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "❌ Error de conexión BD"}), 500

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                id,
                nombre,
                descripcion,
                puntos_necesar,
                stock,
                fecha_inicio,
                fecha_fin,
                activo,
                imagen,
                premios
            FROM listar_cupones
            ORDER BY id;
        """)

        rows = cur.fetchall()

        cupones = []
        for r in rows:
            cupones.append({
                "id": r[0],
                "nombre": r[1],
                "descripcion": r[2],
                "puntos_necesar": r[3],
                "stock": r[4],
                "fecha_inicio": str(r[5]) if r[5] else None,
                "fecha_fin": str(r[6]) if r[6] else None,
                "activo": bool(r[7]),
                "imagen": r[8],
                "premios": r[9]
            })

        cur.close()
        conn.close()

        return jsonify(cupones), 200

    except Exception as e:
        if conn:
            conn.close()
        return jsonify({"error": f"❌ Error al listar cupones: {e}"}), 500
