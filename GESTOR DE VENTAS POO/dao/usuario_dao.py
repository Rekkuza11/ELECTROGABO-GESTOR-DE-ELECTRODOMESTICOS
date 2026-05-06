from database import obtener_conexion

class UsuarioDAO:

    
    def insertar(self, usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            sql = """
            INSERT INTO usuario (id_usuario, password_hash, tipo)
            VALUES (%s, %s, %s)
            """

            valores = (
                usuario.id_usuario,
                usuario.password,
                usuario.tipo
            )

            cursor.execute(sql, valores)
            conexion.commit()

        except Exception as e:
            print("Error en UsuarioDAO:", e)
            conexion.rollback()

        finally:
            conexion.close()

   
    def obtener_todos(self):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM usuario")
        resultados = cursor.fetchall()

        conexion.close()
        return resultados

    def obtener_por_id(self, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT * FROM usuario WHERE id_usuario = %s",
            (id_usuario,)
        )

        resultado = cursor.fetchone()
        conexion.close()
        return resultado

    
    def eliminar(self, id_usuario):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                "DELETE FROM usuario WHERE id_usuario=%s",
                (id_usuario,)
            )
            conexion.commit()

        except Exception as e:
            print("Error en DELETE Usuario:", e)
            conexion.rollback()

        finally:
            conexion.close()