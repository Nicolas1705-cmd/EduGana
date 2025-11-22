
from flask import Flask, request, jsonify
from configbd import get_db_connection

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/recompensas', methods=['GET'])
def listar_recompensas():
    """
    API para listar todas las recompensas.
    Parametros opcionales: ?activo=true/false, ?disponible=true
    """
    try:
        # Obtener parametros de consulta
        solo_activos = request.args.get('activo', 'true').lower() == 'true'
        solo_disponibles = request.args.get('disponible', 'false').lower() == 'true'
        
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
        
        cursor = conn.cursor()
        
        # Construir consulta SQL dinamicamente
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
        
        # Formatear respuesta con manejo de encoding
        lista_recompensas = []
        for recompensa in recompensas:
            # Manejar strings con encoding
            def safe_str(val):
                if val is None:
                    return None
                if isinstance(val, str):
                    return val
                return str(val)
            
            lista_recompensas.append({
                'id': recompensa[0],
                'nombre': safe_str(recompensa[1]),
                'descripcion': safe_str(recompensa[2]),
                'puntos_requeridos': recompensa[3],
                'stock': recompensa[4],
                'imagen_url': safe_str(recompensa[5]),
                'activo': recompensa[6],
                'fecha_creacion': str(recompensa[7]) if recompensa[7] else None
            })
        
        return jsonify({
            'total': len(lista_recompensas),
            'recompensas': lista_recompensas
        }), 200
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error completo: {error_details}")
        return jsonify({'error': f'Error al listar recompensas: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

