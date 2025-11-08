from flask import Flask, request, jsonify
from configbd import get_db_connection

app = Flask(__name__)


@app.route('/idiomas', methods=['POST'])
def agregar_idioma():
    """
    API para agregar un nuevo idioma.
    Espera un JSON con: nombre_idioma y codigo
    """
    try:
        data = request.get_json()
        
        # Validar que se reciban los datos necesarios
        if not data or 'nombre_idioma' not in data or 'codigo' not in data:
            return jsonify({
                'error': 'Faltan datos requeridos: nombre_idioma y codigo'
            }), 400
        
        nombre_idioma = data['nombre_idioma']
        codigo = data['codigo']
        
        # Validar longitud del código (máximo 5 caracteres)
        if len(codigo) > 5:
            return jsonify({
                'error': 'El código no puede tener más de 5 caracteres'
            }), 400
        
        # Validar longitud del nombre (máximo 50 caracteres)
        if len(nombre_idioma) > 50:
            return jsonify({
                'error': 'El nombre del idioma no puede tener más de 50 caracteres'
            }), 400
        
        # Conectar a la base de datos
        conn = get_db_connection()
        if conn is None:
            return jsonify({
                'error': 'No se pudo conectar a la base de datos'
            }), 500
        
        cursor = conn.cursor()
        
        # Insertar el nuevo idioma
        cursor.execute(
            "INSERT INTO idiomas (nombre_idioma, codigo) VALUES (%s, %s) RETURNING id",
            (nombre_idioma, codigo)
        )
        
        idioma_id = cursor.fetchone()[0]
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'mensaje': 'Idioma agregado exitosamente',
            'id': idioma_id,
            'nombre_idioma': nombre_idioma,
            'codigo': codigo
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': f'Error al agregar idioma: {str(e)}'
        }), 500  


@app.route('/idiomas/<int:idioma_id>', methods=['DELETE'])
def eliminar_idioma(idioma_id):
    """
    API para eliminar un idioma por su ID.
    """
    try:
        # Conectar a la base de datos
        conn = get_db_connection()
        if conn is None:
            return jsonify({
                'error': 'No se pudo conectar a la base de datos'
            }), 500
        
        cursor = conn.cursor()
        
        # Verificar si el idioma existe
        cursor.execute("SELECT id FROM idiomas WHERE id = %s", (idioma_id,))
        idioma = cursor.fetchone()
        
        if not idioma:
            cursor.close()
            conn.close()
            return jsonify({
                'error': f'No se encontró el idioma con ID {idioma_id}'
            }), 404
        
        # Eliminar el idioma
        cursor.execute("DELETE FROM idiomas WHERE id = %s", (idioma_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'mensaje': f'Idioma con ID {idioma_id} eliminado exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Error al eliminar idioma: {str(e)}'
        }), 500


@app.route('/idiomas', methods=['GET'])
def listar_idiomas():
    """
    API para listar todos los idiomas.
    """
    try:
        # Conectar a la base de datos
        conn = get_db_connection()
        if conn is None:
            return jsonify({
                'error': 'No se pudo conectar a la base de datos'
            }), 500
        
        cursor = conn.cursor()
        
        # Obtener todos los idiomas
        cursor.execute("SELECT id, nombre_idioma, codigo FROM idiomas ORDER BY id")
        idiomas = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Formatear la respuesta
        lista_idiomas = []
        for idioma in idiomas:
            lista_idiomas.append({
                'id': idioma[0],
                'nombre_idioma': idioma[1],
                'codigo': idioma[2]
            })
        
        return jsonify({
            'total': len(lista_idiomas),
            'idiomas': lista_idiomas
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Error al listar idiomas: {str(e)}'
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
