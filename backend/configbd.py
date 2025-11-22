from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
import psycopg2
import os
import locale

# Configurar locale para evitar problemas de encoding
try:
    locale.setlocale(locale.LC_ALL, 'C')
except:
    pass

# Datos de conexión (ajústalos según tu base)
DB_NAME = "edugana_db"
DB_USER = "postgres"
DB_PASS = "System.2025*"
DB_HOST = "localhost"
DB_PORT = "5432"

def get_db_connection():
    """
    Crea una conexión a PostgreSQL y la devuelve.
    Maneja problemas de encoding en mensajes del servidor.
    """
    # Configurar variables de entorno ANTES de importar/usar psycopg2
    os.environ['PGCLIENTENCODING'] = 'UTF8'
    os.environ['LC_ALL'] = 'C'
    os.environ['LANG'] = 'C'
    
    try:
        # Construir connection string con encoding explícito
        conn_params = {
            'host': DB_HOST,
            'port': DB_PORT,
            'dbname': DB_NAME,
            'user': DB_USER,
            'password': DB_PASS,
        }
        
        # Intentar conexión
        conn = psycopg2.connect(**conn_params)
        
        # Configurar la sesión para UTF-8
        with conn.cursor() as cursor:
            cursor.execute("SET client_encoding TO 'UTF8';")
            cursor.execute("SET lc_messages TO 'C';")
        conn.commit()
        
        return conn
        
    except Exception as e:
        # Si el error es de encoding, mostrar mensaje útil
        error_msg = str(e)
        if 'UnicodeDecodeError' in str(type(e).__name__):
            print(f"Error de encoding al conectar. Verifica la contraseña de PostgreSQL.")
            print(f"El servidor PostgreSQL está devolviendo mensajes con caracteres especiales.")
            print(f"Detalles: {error_msg}")
        else:
            print(f"Error al conectar a la base de datos: {error_msg}")
        return None
