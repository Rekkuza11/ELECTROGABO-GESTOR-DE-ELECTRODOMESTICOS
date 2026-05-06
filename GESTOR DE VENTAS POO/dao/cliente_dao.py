from database import obtener_conexion
from models.cliente import Cliente

class ClienteDAO:

    def insertar(self, cliente):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute(
                "INSERT INTO usuario (id_usuario, password_hash, tipo) VALUES (%s, %s, %s)",
                (cliente.id_usuario, cliente.password, "cliente")
            )

            cursor.execute(
                "INSERT INTO cliente (id_cliente, nombre, telefono, direccion) VALUES (%s, %s, %s, %s)",
                (cliente.id_usuario, cliente.nombre, cliente.telefono, cliente.direccion)
            )

            conexion.commit()

        except Exception as e:
            print(e)
            conexion.rollback()

        finally:
            conexion.close()

    def obtener_todos(self):
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT c.id_cliente, c.nombre, c.telefono, c.direccion, u.password_hash
            FROM cliente c
            JOIN usuario u ON c.id_cliente = u.id_usuario
        """)

        clientes = []
        for fila in cursor.fetchall():
            clientes.append(self._crear_objeto(fila))

        conexion.close()
        return clientes

    def _crear_objeto(self, fila):
        return Cliente(
            fila[0],
            fila[4],
            fila[1],
            fila[2],
            fila[3]
        )


if __name__ == "__main__":
    dao = ClienteDAO()
    clientes = dao.obtener_todos()

    for c in clientes:
        print(c.id_usuario, c.nombre, c.telefono, c.direccion, c.password)