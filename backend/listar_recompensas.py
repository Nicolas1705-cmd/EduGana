from flask import Flask, request, jsonify
from flask_cors import CORS
from configbd import get_db_connection

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde el frontend
app.config['JSON_AS_ASCII'] = False

@app.route('/recompensas', methods=['GET'])
def listar_recompensas():
    """
    API para listar todas las recompensas.
    Parámetros opcionales: 
    - ?activo=true/false (filtrar por activas)
    - ?disponible=true (filtrar por stock > 0)
    """
    try:
        # Obtener parámetros de consulta
        solo_activos = request.args.get('activo', 'true').lower() == 'true'
        solo_disponibles = request.args.get('disponible', 'false').lower() == 'true'
        
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
        
        cursor = conn.cursor()
        
        # Construir consulta SQL dinámicamente
        query = """
            SELECT id, nombre, descripcion, puntos_requeridos, stock, imagen_url, 
                   activo, fecha_creacion
            FROM recompensas
            WHERE 1=1
        """
        params = []
        
        if solo_activos:
            query += " AND activo = %s"
            params.append(True)
        
        if solo_disponibles:
            query += " AND stock > 0"
        
        query += " ORDER BY puntos_requeridos ASC"
        
        cursor.execute(query, params if params else None)
        recompensas = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Formatear respuesta
        lista_recompensas = []
        for recompensa in recompensas:
            lista_recompensas.append({
                'id': recompensa[0],
                'nombre': recompensa[1],
                'descripcion': recompensa[2],
                'puntos_requeridos': recompensa[3],
                'stock': recompensa[4],
                'imagen_url': recompensa[5],
                'activo': recompensa[6],
                'fecha_creacion': str(recompensa[7]) if recompensa[7] else None
            })
        
        return jsonify({
            'success': True,
            'total': len(lista_recompensas),
            'recompensas': lista_recompensas
        }), 200
        
    except Exception as e:
        import traceback
        print(f"Error al listar recompensas: {traceback.format_exc()}")
        return jsonify({'error': f'Error al listar recompensas: {str(e)}'}), 500


@app.route('/recompensas/<int:id>', methods=['GET'])
def obtener_recompensa(id):
    """
    API para obtener una recompensa específica por ID.
    """
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
        
        cursor = conn.cursor()
        
        query = """
            SELECT id, nombre, descripcion, puntos_requeridos, stock, imagen_url, 
                   activo, fecha_creacion
            FROM recompensas
            WHERE id = %s
        """
        
        cursor.execute(query, (id,))
        recompensa = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if recompensa is None:
            return jsonify({'error': f'Recompensa con ID {id} no encontrada'}), 404
        
        # Formatear respuesta
        resultado = {
            'id': recompensa[0],
            'nombre': recompensa[1],
            'descripcion': recompensa[2],
            'puntos_requeridos': recompensa[3],
            'stock': recompensa[4],
            'imagen_url': recompensa[5],
            'activo': recompensa[6],
            'fecha_creacion': str(recompensa[7]) if recompensa[7] else None
        }
        
        return jsonify({
            'success': True,
            'recompensa': resultado
        }), 200
        
    except Exception as e:
        import traceback
        print(f"Error al obtener recompensa: {traceback.format_exc()}")
        return jsonify({'error': f'Error al obtener recompensa: {str(e)}'}), 500


if __name__ == '__main__':
    print("=== API de Recompensas ===")
    print("Endpoints disponibles:")
    print("  GET  /recompensas           - Listar todas las recompensas")
    print("  GET  /recompensas/<id>      - Obtener una recompensa por ID")
    print("\nServidor ejecutándose en http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)

