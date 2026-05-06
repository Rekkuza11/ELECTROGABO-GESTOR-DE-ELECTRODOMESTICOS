from database import obtener_conexion

class DetalleVentaDAO:

    def insertar(self, detalle):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            sql = """
            INSERT INTO detalle_venta 
            (id_venta, id_producto, cantidad, precio_unitario, subtotal)
            VALUES (%s, %s, %s, %s, %s)
            """

            valores = (
                detalle.id_venta,
                detalle.id_producto,
                detalle.cantidad,
                detalle.precio_unitario,
                detalle.subtotal
            )

            cursor.execute(sql, valores)
            conexion.commit()

        except Exception as e:
            print("Error en DetalleVentaDAO:", e)
            conexion.rollback()

        finally:
            conexion.close()