import mysql.connector

def obtener_conexion():
    return mysql.connector.connect(
        user='root',
        password='admin123',
        host='localhost',
        database='base_datos_electrogabo',
        port='3306'
    )

conexion = obtener_conexion()
print(conexion)


