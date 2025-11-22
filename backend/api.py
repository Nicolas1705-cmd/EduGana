from flask import Flask, request, jsonify
from flask_cors import CORS # Importamos CORS para permitir consumo desde cualquier origen

# Importaciones de módulos
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
# Importación repetida de cupones eliminada


# Inicializa la aplicación Flask
app = Flask(__name__)

# =========================================================
# CONFIGURACIÓN DE CORS GLOBAL
# Permite que cualquier dominio (*) acceda a todas las rutas (/*)
# Para máxima compatibilidad con clientes externos.
# =========================================================
CORS(app, resources={r"/*": {"origins": "*"}})

# RYDER
app.add_url_rule(
    '/addCurso',         # La URL a mapear
    view_func=curso.registrar_inscripcion, # La función del módulo 'seccion'
    methods=['GET']   # Los métodos HTTP permitidos
)

# SEBASTIAN check
app.add_url_rule(
    '/addMatricula',         # La URL a mapear
    view_func=matricula.registrar_matricula, # La función del módulo 'seccion'
    methods=['GET']   # Los métodos HTTP permitidos
)


# BRAYAN check
app.add_url_rule(
    '/addColegio',         # La URL a mapear
    view_func=colegio.registrar_colegio, # La función del módulo 'seccion'
    methods=['GET']   # Los métodos HTTP permitidos
)


# MOSNERRAT
app.add_url_rule(
    '/addProfesor',         # La URL a mapear
    view_func=profesores.agregar_profesor, # La función del módulo 'seccion'
    methods=['GET']   # Los métodos HTTP permitidos
)


# JOSE check
app.add_url_rule(
    '/listRecompensas',         # La URL a mapear
    view_func=listar_recompensas.listar_recompensas, # La función del módulo 'seccion'
    methods=['GET']   # Los métodos HTTP permitidos
)



# CUEVA  check
app.add_url_rule(
    '/registrarAsistencia',         # La URL a mapear
    view_func=registro_de_control_asistencia.registrar_asistencia, # La función del módulo 'seccion'
    methods=['GET']   # Los métodos HTTP permitidos
)


# ANDERSON  check
app.add_url_rule(
    '/listAsistencia',         # La URL a mapear
    view_func=Historial.obtener_asistencias, # La función del módulo 'seccion'
    methods=['GET']   # Los métodos HTTP permitidos
)




# RODRIGO  check
app.add_url_rule(
    '/registrarUsuario',         # La URL a mapear
    view_func=usuarios.registrar_usuario, # La función del módulo 'seccion'
    methods=['GET']   # Los métodos HTTP permitidos
)

# YANELY 
app.add_url_rule(
    '/addTienda',         # La URL a mapear
    view_func=tienda.registrar_tienda, # La función del módulo 'seccion'
    methods=['GET']   # Los métodos HTTP permitidos
)

# FABIAN 
app.add_url_rule(
    '/listCupones',         # La URL a mapear
    view_func=cupones.listar_cupones, # La función del módulo 'seccion'
    methods=['GET']   # Los métodos HTTP permitidos
)


if __name__ == '__main__':
    # Asegúrate de configurar las variables de entorno para JWT antes de correr
    # Se añade host='0.0.0.0' para permitir que el servidor sea accesible
    # desde cualquier dispositivo en la red local.
    app.run(debug=True, host='0.0.0.0')



