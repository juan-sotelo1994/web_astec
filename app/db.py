from flask import abort
import mysql.connector

def obtener_conexion():
    try:
        mydb = mysql.connector.connect(
            host ="localhost",
            user ="root",
            password ="",
            db = "astec"
        )
    except Exception:
        abort(500)
    return mydb
