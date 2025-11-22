from flask import Flask, request, jsonify
from flask_cors import CORS
from configbd import get_db_connection


def listar_cupones():
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT * FROM listar_cupones ORDER BY id ASC;")
        data = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500