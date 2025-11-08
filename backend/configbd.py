from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
import psycopg2

# Datos de conexión (ajústalos según tu base)
DB_NAME = "edugana_db"
DB_USER = "postgres"
DB_PASS = "System.2025*"
DB_HOST = "35.237.18.79"
DB_PORT = "5432"

def get_db_connection():
    """
    Crea una conexión a PostgreSQL y la devuelve.
    """
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except psycopg2.Error as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return None
