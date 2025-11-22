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



