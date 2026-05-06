from database import obtener_conexion

class EmpleadoDAO:

    def insertar(self, empleado):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
        
            sql_usuario = """
            INSERT INTO usuario (id_usuario, password_hash, tipo)
            VALUES (%s, %s, %s)
            """
            cursor.execute(sql_usuario, (empleado.id_usuario, empleado.password, "empleado"))

            
            sql_empleado = """
            INSERT INTO empleado (id_empleado, nombre, rol)
            VALUES (%s, %s, %s)
            """
            cursor.execute(sql_empleado, (empleado.id_usuario, empleado.nombre, empleado.rol))

            conexion.commit()

        except Exception as e:
            print("Error en EmpleadoDAO:", e)
            conexion.rollback()

        finally:
            conexion.close()