from flask import Flask, request, jsonify # Importamos Flask aquí
app = Flask(__name__)
import seccion
import curso
import colegio
import historialdecanjes
import Historial
# import tienda
import registro_de_control_asistencia
import listar_recompensas
import usuarios
import cupones
import matricula
import profesores


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


# BRAYAN
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



# CUEVA 
app.add_url_rule(
    '/registrarAsistencia',         # La URL a mapear
    view_func=registro_de_control_asistencia.registrar_asistencia, # La función del módulo 'seccion'
    methods=['GET']   # Los métodos HTTP permitidos
)


# ANDERSON 
app.add_url_rule(
    '/listAsistencia',         # La URL a mapear
    view_func=Historial.obtener_asistencias, # La función del módulo 'seccion'
    methods=['GET']   # Los métodos HTTP permitidos
)




# RODRIGO 
app.add_url_rule(
    '/registrarUsuario',         # La URL a mapear
    view_func=usuarios.registrar_usuario, # La función del módulo 'seccion'
    methods=['GET']   # Los métodos HTTP permitidos
)








