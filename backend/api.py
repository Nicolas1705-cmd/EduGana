from flask import Flask, request, jsonify # Importamos Flask aquí
app = Flask(__name__)
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


# 1. Importa y registra directamente la función:
app.add_url_rule(
    '/bienvenido',         # La URL a mapear
    view_func=seccion.bienvenido, # La función del módulo 'seccion'
    methods=['GET']   # Los métodos HTTP permitidos
)