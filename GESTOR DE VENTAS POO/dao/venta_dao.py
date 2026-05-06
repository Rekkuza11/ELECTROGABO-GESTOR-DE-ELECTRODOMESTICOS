from database import obtener_conexion

class VentaDAO:

    
    def insertar(self, venta):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            sql = """
            INSERT INTO venta 
            (id_cliente, id_empleado, fecha, total)
            VALUES (%s, %s, %s, %s)
            """

            valores = (
                venta.id_cliente,
                venta.id_empleado,
                venta.fecha,
                venta.total
            )

            cursor.execute(sql, valores)
            conexion.commit()

            
            venta.id_venta = cursor.lastrowid

        except Exception as e:
            print("Error en VentaDAO:", e)
            conexion.rollback()

        finally:
            conexion.close()

  
    def obtener_todos(self):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM venta")
        resultados = cursor.fetchall()

        conexion.close()
        return resultados

    
    def obtener_completo(self):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT v.id_venta, v.fecha, v.total,
                   c.nombre AS cliente,
                   e.nombre AS empleado
            FROM venta v
            JOIN cliente c ON v.id_cliente = c.id_cliente
            JOIN empleado e ON v.id_empleado = e.id_empleado
        """)

        resultados = cursor.fetchall()
        conexion.close()
        return resultados

    
    def eliminar(self, id_venta):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                "DELETE FROM venta WHERE id_venta=%s",
                (id_venta,)
            )
            conexion.commit()

        except Exception as e:
            print("Error en DELETE Venta:", e)
            conexion.rollback()

        finally:
            conexion.close()