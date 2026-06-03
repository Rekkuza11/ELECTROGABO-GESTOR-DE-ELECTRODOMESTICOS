"""
DAO Producto.
Aplica:
  - Usa el Singleton DatabaseConnection.
  - Encapsulamiento: métodos de ayuda privados.
  - Método de clase: fábrica de Producto desde fila de BD.
  - Excepciones especializadas: ProductoNoEncontradoError, IntegridadDatosError.
  - Principio DIP: depende de la abstracción (DatabaseConnection), no de mysql directo.

CORRECCIONES — Fase 1:
  - #7:  actualizar_stock() añade cláusula AND stock >= %s para que el motor
         rechace el UPDATE si no hay unidades suficientes, imposibilitando que
         el stock quede negativo por concurrencia o doble llamada.
  - #19: nuevo método aumentar_stock() para reponer unidades; se usa al revertir
         una venta eliminada (fix #18 en venta_controller.py).

CORRECCIÓN #11 — SQL dinámico mediante f-string:
    Los métodos obtener_todos(), obtener_por_id() y eliminar() usaban
    f"... FROM {self._tabla} ..." para construir las queries.
    Solución: tabla hardcodeada directamente en cada SQL.

CORRECCIÓN NE-TYPE — Mismatch de tipo en id_producto:
    Tkinter Treeview retorna valores numéricos como int de Python aunque la
    columna id_producto sea varchar(20) en la BD (ej: "44444" → 44444).
    Cuando ese int se pasa como parámetro %s a MySQL/TiDB, el motor intenta
    castear TODAS las filas de id_producto a INTEGER para comparar, y falla
    al encontrar valores alfanuméricos como 'PD8827':
        "1292 (22007): Truncated incorrect INTEGER value: 'PD8827'"

    Solución: castear str(id_producto) en TODOS los métodos que usan el
    id como parámetro de query. Así MySQL siempre recibe un string y compara
    varchar contra varchar correctamente.

FASE 8 — Eliminación segura:
  - tiene_ventas(id): consulta si el producto aparece en algún detalle_venta
    antes de intentar el DELETE.
"""

from database import DatabaseConnection
from models.producto import Producto
from exceptions import (
    ProductoNoEncontradoError,
    StockInsuficienteError,
    IntegridadDatosError,
    BaseDatosError,
)


class ProductoDAO:
    """Objeto de acceso a datos para la entidad Producto."""

    # Atributo de clase — identifica la tabla que gestiona este DAO.
    # CORRECCIÓN #11: ya NO se interpola en f-strings de SQL.
    _tabla: str = "producto"

    def __init__(self):
        self._db = DatabaseConnection()

    # ── CRUD estándar ─────────────────────────────────────────────────────────

    def insertar(self, producto: Producto) -> None:
        if producto.id_producto is None:
            raise BaseDatosError(
                "Error en 'insertar producto': se requiere un ID de producto."
            )
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            sql = """
                INSERT INTO producto
                    (id_producto, nombre, marca, precio_compra, precio_venta, stock)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            # CORRECCIÓN NE-TYPE: id siempre como str
            cursor.execute(sql, (str(producto.id_producto),) + self.__a_valores(producto))
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            self.__manejar_error(e, "insertar producto")
        finally:
            cursor.close()

    def obtener_todos(self) -> list:
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            # CORRECCIÓN #11: tabla hardcodeada — sin f-string ni interpolación dinámica.
            cursor.execute("SELECT * FROM producto")
            filas = cursor.fetchall()
            productos = []
            for fila in filas:
                try:
                    productos.append(Producto.desde_fila_bd(fila))
                except Exception:
                    continue
            return productos
        except Exception as e:
            self.__manejar_error(e, "obtener todos los productos")
        finally:
            cursor.close()

    def obtener_por_id(self, id_producto) -> Producto:
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            # CORRECCIÓN NE-TYPE: str() garantiza comparación varchar vs varchar.
            cursor.execute(
                "SELECT * FROM producto WHERE id_producto = %s",
                (str(id_producto),)
            )
            fila = cursor.fetchone()
            if not fila:
                raise ProductoNoEncontradoError(id_producto)
            return Producto.desde_fila_bd(fila)
        except ProductoNoEncontradoError:
            raise
        except Exception as e:
            self.__manejar_error(e, f"obtener producto {id_producto}")
        finally:
            cursor.close()

    def actualizar(self, producto: Producto) -> None:
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            sql = """
                UPDATE producto
                SET nombre=%s, marca=%s, precio_compra=%s, precio_venta=%s, stock=%s
                WHERE id_producto=%s
            """
            # CORRECCIÓN NE-TYPE: str() en el id del WHERE
            valores = self.__a_valores(producto) + (str(producto.id_producto),)
            cursor.execute(sql, valores)
            if cursor.rowcount == 0:
                raise ProductoNoEncontradoError(producto.id_producto)
            conexion.commit()
        except ProductoNoEncontradoError:
            raise
        except Exception as e:
            conexion.rollback()
            self.__manejar_error(e, f"actualizar producto {producto.id_producto}")
        finally:
            cursor.close()

    def eliminar(self, id_producto) -> None:
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            # CORRECCIÓN NE-TYPE: str() garantiza comparación varchar vs varchar.
            cursor.execute(
                "DELETE FROM producto WHERE id_producto = %s",
                (str(id_producto),)
            )
            if cursor.rowcount == 0:
                raise ProductoNoEncontradoError(id_producto)
            conexion.commit()
        except ProductoNoEncontradoError:
            raise
        except Exception as e:
            conexion.rollback()
            self.__manejar_error(e, f"eliminar producto {id_producto}")
        finally:
            cursor.close()

    # ── Validación de dependencias FK (Fase 8) ────────────────────────────────

    def tiene_ventas(self, id_producto) -> bool:
        """
        FASE 8 — Pre-validación de FK antes de eliminar.

        CORRECCIÓN NE-TYPE: str(id_producto) evita que MySQL intente castear
        todos los valores varchar de id_producto a INTEGER cuando el parámetro
        llega como int desde Tkinter Treeview, lo que causaba:
            "1292 (22007): Truncated incorrect INTEGER value: 'PD8827'"

        Retorna:
            True  — el producto tiene ventas asociadas y NO puede eliminarse.
            False — el producto no tiene ventas y puede eliminarse con seguridad.
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            # CORRECCIÓN NE-TYPE: str() garantiza comparación varchar vs varchar.
            cursor.execute(
                "SELECT 1 FROM detalle_venta WHERE id_producto = %s LIMIT 1",
                (str(id_producto),)
            )
            return cursor.fetchone() is not None
        except Exception as e:
            raise BaseDatosError(
                f"Error al verificar ventas del producto {id_producto}: {e}"
            ) from e
        finally:
            cursor.close()

    # ── Gestión de stock ──────────────────────────────────────────────────────

    def actualizar_stock(self, id_producto, cantidad: int) -> None:
        """
        Descuenta `cantidad` unidades del stock del producto.

        CORRECCIÓN #7: cláusula AND stock >= %s previene stock negativo.
        CORRECCIÓN NE-TYPE: str(id_producto) en todos los parámetros.
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "UPDATE producto "
                "SET stock = stock - %s "
                "WHERE id_producto = %s AND stock >= %s",
                (cantidad, str(id_producto), cantidad),
            )
            if cursor.rowcount == 0:
                cursor.execute(
                    "SELECT nombre, stock FROM producto WHERE id_producto = %s",
                    (str(id_producto),),
                )
                fila = cursor.fetchone()
                if not fila:
                    raise ProductoNoEncontradoError(id_producto)
                raise StockInsuficienteError(fila[0], int(fila[1]), cantidad)

            conexion.commit()

        except (ProductoNoEncontradoError, StockInsuficienteError):
            raise
        except Exception as e:
            conexion.rollback()
            self.__manejar_error(e, f"actualizar stock {id_producto}")
        finally:
            cursor.close()

    def aumentar_stock(self, id_producto, cantidad: int) -> None:
        """
        CORRECCIÓN #19 — Método para reponer stock.
        CORRECCIÓN NE-TYPE: str(id_producto) en todos los parámetros.
        """
        if cantidad <= 0:
            raise BaseDatosError(
                f"Error en 'aumentar stock': la cantidad debe ser positiva "
                f"(recibido: {cantidad})."
            )
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "UPDATE producto SET stock = stock + %s WHERE id_producto = %s",
                (cantidad, str(id_producto)),
            )
            if cursor.rowcount == 0:
                raise ProductoNoEncontradoError(id_producto)
            conexion.commit()
        except ProductoNoEncontradoError:
            raise
        except Exception as e:
            conexion.rollback()
            self.__manejar_error(e, f"aumentar stock {id_producto}")
        finally:
            cursor.close()

    # ── Helpers privados ──────────────────────────────────────────────────────

    @staticmethod
    def __a_valores(producto: Producto) -> tuple:
        return (
            producto.nombre,
            producto.marca,
            producto.precio_compra,
            producto.precio_venta,
            producto.stock,
        )

    @staticmethod
    def __manejar_error(error: Exception, operacion: str) -> None:
        mensaje = str(error)
        if "Duplicate entry" in mensaje or "foreign key" in mensaje.lower():
            raise IntegridadDatosError(mensaje) from error
        raise BaseDatosError(f"Error en '{operacion}': {mensaje}") from error
