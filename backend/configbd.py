from flask import Flask, request, jsonifyBcrypt  
import psycopg2

app = Flask(__name__)  

# Configuración de la conexión a la base de datos
DB_NAME = "edugana_db"
DB_USER = "postgres"
DB_PASS = "System.2025*"
DB_HOST = "35.237.18.79" # o la IP del servidor
DB_PORT = "5432"
 

def get_db_connection():
    """
    Función para establecer la conexión a la base de datos PostgreSQL.
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
        print(f"Error al conectar a la base de datos: {e}")
        return None
