from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os # Importamos el módulo os para manejar rutas

# Importaciones de módulos
# ... (dejar todas tus importaciones existentes)
import seccion
import curso
import colegio
import historialdecanjes
import Historial
import tienda
import registro_de_control_asistencia
import listar_recompensas
import usuarios
import cupones
import matricula
import profesores


# Inicializa la aplicación Flask
app = Flask(__name__)

# =========================================================
# CONFIGURACIÓN DE RUTAS Y CORS
# =========================================================
CORS(app, resources={r"/*": {"origins": "*"}})

# Define la ruta base para el frontend (relativa a donde está api.py)
# Como api.py está en 'backend', '../frontend' apunta a la carpeta 'frontend'
FRONTEND_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')
FRONTEND_STATIC_FOLDER = os.path.join(FRONTEND_FOLDER) # La carpeta frontend contiene los estáticos y HTML

# --- RUTAS PARA EL FRONTEND (Servicio de archivos estáticos) ---

# 1. Ruta principal (Servir la página inicial)
# Cuando el usuario navega a la URL raíz (/)
@app.route('/')
def serve_index():
    # Asume que 'inicio.html' es tu página principal
    return send_from_directory(FRONTEND_STATIC_FOLDER, 'inicio.html')

# 2. Ruta para todos los demás archivos estáticos (CSS, JS, imágenes, otros HTML)
# Captura cualquier ruta que no haya sido mapeada por el backend (como /tienda.html, /css/style.css, etc.)
@app.route('/<path:filename>')
def serve_static(filename):
    # Esto busca el archivo solicitado dentro de la carpeta 'frontend'
    # Ejemplo: para 'tienda.html', buscará 'EduGana/frontend/tienda.html'
    return send_from_directory(FRONTEND_STATIC_FOLDER, filename)


# --- TUS REGLAS DE API EXISTENTES ---

# LUIGGY
app.add_url_rule(
  '/addSeccion', view_func=seccion.addSeccion, methods=['GET']
)


# RYDER
app.add_url_rule(
  '/addCurso', view_func=curso.registrar_inscripcion, methods=['GET']
)

# SEBASTIAN check
app.add_url_rule(
  '/addMatricula', view_func=matricula.registrar_matricula, methods=['GET']
)

# BRAYAN check
app.add_url_rule(
  '/addColegio', view_func=colegio.registrar_colegio, methods=['GET']
)

# ... (Continuar con todas tus otras rutas de API)
# MOSNERRAT
app.add_url_rule(
  '/addProfesor', view_func=profesores.agregar_profesor, methods=['GET']
)
# JOSE check
app.add_url_rule(
  '/listRecompensas', view_func=listar_recompensas.listar_recompensas, methods=['GET']
)
# CUEVA check
app.add_url_rule(
  '/registrarAsistencia', view_func=registro_de_control_asistencia.registrar_asistencia, methods=['GET']
)
# ANDERSON check
app.add_url_rule(
  '/listAsistencia', view_func=Historial.obtener_asistencias, methods=['GET']
)
# RODRIGO check
app.add_url_rule(
  '/registrarUsuario', view_func=usuarios.registrar_usuario, methods=['GET']
)
# YANELY
app.add_url_rule(
  '/addTienda', view_func=tienda.registrar_tienda, methods=['GET']
)
# FABIAN
app.add_url_rule(
  '/listCupones', view_func=cupones.listar_cupones, methods=['GET']
)


if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')