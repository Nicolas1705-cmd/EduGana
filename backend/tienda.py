from flask import Flask, jsonify, request
from configbd import get_db_connection

app = Flask(__name__)

# --- 1️⃣ Agregar producto ---
@app.route('/tienda', methods=['POST'])
def agregar_producto():
    data = request.get_json()

    # Validar que todos los campos necesarios estén presentes
    required_fields = ['NombreTienda', 'NombreProducto', 'CostoPuntos', 'CantidadDispo', 'MarcaProducto']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Faltan campos requeridos"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Error de conexión con la base de datos"}), 500

    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Tienda (NombreTienda, NombreProducto, CostoPuntos, CantidadDispo, MarcaProducto)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_tienda;
        """, (
            data['NombreTienda'],
            data['NombreProducto'],
            data['CostoPuntos'],
            data['CantidadDispo'],
            data['MarcaProducto']
        ))

        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "✅ Producto agregado exitosamente", "id_tienda": new_id}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Error al insertar producto: {e}"}), 500


# --- 2️⃣ Eliminar producto ---
@app.route('/tienda/<int:id_tienda>', methods=['DELETE'])
def eliminar_producto(id_tienda):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Error de conexión con la base de datos"}), 500

    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM Tienda WHERE id_tienda = %s RETURNING id_tienda;", (id_tienda,))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if result:
            return jsonify({"message": f"✅ Producto {id_tienda} eliminado correctamente"}), 200
        else:
            return jsonify({"error": "Producto no encontrado"}), 404

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Error al eliminar producto: {e}"}), 500


# --- 3️⃣ Listar productos ---
@app.route('/tienda', methods=['GET'])
def listar_productos():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Error de conexión con la base de datos"}), 500

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id_tienda, NombreTienda, NombreProducto, CostoPuntos, CantidadDispo, MarcaProducto
            FROM Tienda
            ORDER BY id_tienda;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        productos = []
        for row in rows:
            productos.append({
                "id_tienda": row[0],
                "NombreTienda": row[1],
                "NombreProducto": row[2],
                "CostoPuntos": float(row[3]),
                "CantidadDispo": row[4],
                "MarcaProducto": row[5]
            })

        return jsonify(productos), 200

    except Exception as e:
        return jsonify({"error": f"Error al listar productos: {e}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
