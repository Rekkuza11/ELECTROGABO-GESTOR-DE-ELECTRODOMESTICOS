from database import obtener_conexion

class ProductoDAO:

    def insertar(self, producto):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            sql = """
            INSERT INTO producto 
            (nombre, marca, precio_compra, precio_venta, stock)
            VALUES (%s, %s, %s, %s, %s)
            """

            valores = (
                producto.nombre,
                producto.marca,
                producto.precio_compra,
                producto.precio_venta,
                producto.stock
            )

            cursor.execute(sql, valores)
            conexion.commit()

            
            producto.id_producto = cursor.lastrowid

        except Exception as e:
            print("Error en INSERT Producto:", e)
            conexion.rollback()

        finally:
            conexion.close()

    def obtener_todos(self):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM producto")
        resultados = cursor.fetchall()

        conexion.close()
        return resultados

   
    def actualizar(self, producto):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            sql = """
            UPDATE producto 
            SET nombre=%s, marca=%s, precio_compra=%s, precio_venta=%s, stock=%s
            WHERE id_producto=%s
            """

            valores = (
                producto.nombre,
                producto.marca,
                producto.precio_compra,
                producto.precio_venta,
                producto.stock,
                producto.id_producto
            )

            cursor.execute(sql, valores)
            conexion.commit()

        except Exception as e:
            print("Error en UPDATE Producto:", e)
            conexion.rollback()

        finally:
            conexion.close()

   
    def eliminar(self, id_producto):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                "DELETE FROM producto WHERE id_producto=%s",
                (id_producto,)
            )
            conexion.commit()

        except Exception as e:
            print("Error en DELETE Producto:", e)
            conexion.rollback()

        finally:
            conexion.close()

    
    def actualizar_stock(self, id_producto, cantidad):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            sql = """
            UPDATE producto 
            SET stock = stock - %s
            WHERE id_producto = %s
            """
            cursor.execute(sql, (cantidad, id_producto))
            conexion.commit()

        except Exception as e:
            print("Error al actualizar stock:", e)
            conexion.rollback()

        finally:
            conexion.close()