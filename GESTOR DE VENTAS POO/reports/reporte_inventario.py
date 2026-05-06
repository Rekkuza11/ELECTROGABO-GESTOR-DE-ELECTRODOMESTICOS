"""
Reporte de Inventario.
Responsabilidad: consultar y estructurar el estado del inventario desde la BD.
Aplica:
  - SRP: única responsabilidad — generar datos del reporte de inventario.
  - Método de clase: punto de entrada al reporte.
  - Métodos estáticos: cálculos puros de dominio (valor de inventario, margen).
  - Excepciones especializadas del dominio.
"""
 
from database import DatabaseConnection
from exceptions import BaseDatosError
from models.producto import Producto
from UTIL.helpers import formatear_moneda, obtener_fecha_actual
 
 
class ReporteInventario:
    """
    Genera reportes sobre el estado del inventario de productos.
 
    Atributos de clase:
        _tabla          (protegido) — tabla principal.
        STOCK_MINIMO    (protegido) — umbral bajo el cual se emite alerta.
    """
 
    _tabla: str = "producto"
    STOCK_MINIMO: int = 5  # umbral de alerta configurable a nivel de clase
 
    def __init__(self):
        self._db = DatabaseConnection()
 
    # ── Método de clase (punto de entrada recomendado) ────────────────────────
 
    @classmethod
    def generar(cls) -> "ReporteInventario":
        """Fábrica: crea e imprime el reporte completo de inventario."""
        reporte = cls()
        reporte.mostrar_resumen()
        return reporte
 
    @classmethod
    def configurar_stock_minimo(cls, nuevo_minimo: int) -> None:
        """
        Método de clase: permite cambiar el umbral de alerta globalmente
        sin necesitar una instancia.
        """
        if nuevo_minimo < 0:
            raise ValueError("El stock mínimo no puede ser negativo.")
        cls.STOCK_MINIMO = nuevo_minimo
 
    # ── Métodos públicos ──────────────────────────────────────────────────────
 
    def obtener_todos_los_productos(self) -> list:
        """
        Retorna todos los productos con su información completa.
        Cada fila: (id_producto, nombre, marca, precio_compra, precio_venta, stock)
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(f"""
                SELECT id_producto, nombre, marca,
                       precio_compra, precio_venta, stock
                FROM {self._tabla}
                ORDER BY nombre ASC
            """)
            return cursor.fetchall()
        except Exception as e:
            raise BaseDatosError(f"Error al obtener productos: {e}") from e
        finally:
            cursor.close()
 
    def obtener_productos_stock_bajo(self) -> list:
        """
        Retorna productos cuyo stock es menor o igual al STOCK_MINIMO.
        Alerta temprana para reabastecimiento.
        Retorna: (id_producto, nombre, marca, stock)
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT id_producto, nombre, marca, stock
                FROM producto
                WHERE stock <= %s
                ORDER BY stock ASC
            """, (self.STOCK_MINIMO,))
            return cursor.fetchall()
        except Exception as e:
            raise BaseDatosError(f"Error al obtener productos con stock bajo: {e}") from e
        finally:
            cursor.close()
 
    def obtener_productos_sin_stock(self) -> list:
        """
        Retorna productos con stock igual a cero (agotados).
        Retorna: (id_producto, nombre, marca)
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT id_producto, nombre, marca
                FROM producto
                WHERE stock = 0
                ORDER BY nombre ASC
            """)
            return cursor.fetchall()
        except Exception as e:
            raise BaseDatosError(f"Error al obtener productos sin stock: {e}") from e
        finally:
            cursor.close()
 
    def obtener_valor_total_inventario(self) -> float:
        """
        Calcula el valor total del inventario a precio de compra
        (lo que la empresa tiene invertido).
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT COALESCE(SUM(precio_compra * stock), 0)
                FROM producto
            """)
            resultado = cursor.fetchone()
            return round(float(resultado[0]), 2) if resultado else 0.0
        except Exception as e:
            raise BaseDatosError(f"Error al calcular valor del inventario: {e}") from e
        finally:
            cursor.close()
 
    def obtener_valor_potencial_ventas(self) -> float:
        """
        Calcula el ingreso potencial si se vendiera todo el inventario
        (a precio de venta).
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT COALESCE(SUM(precio_venta * stock), 0)
                FROM producto
            """)
            resultado = cursor.fetchone()
            return round(float(resultado[0]), 2) if resultado else 0.0
        except Exception as e:
            raise BaseDatosError(f"Error al calcular valor potencial: {e}") from e
        finally:
            cursor.close()
 
    def obtener_total_productos(self) -> int:
        """Retorna el número total de productos distintos en inventario."""
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM producto")
            resultado = cursor.fetchone()
            return int(resultado[0]) if resultado else 0
        except Exception as e:
            raise BaseDatosError(f"Error al contar productos: {e}") from e
        finally:
            cursor.close()
 
    def obtener_productos_mayor_margen(self, limite: int = 5) -> list:
        """
        Productos con mayor margen de ganancia porcentual.
        Retorna: (nombre, marca, precio_compra, precio_venta, margen_pct)
        """
        conexion = self._db.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""
                SELECT
                    nombre,
                    marca,
                    precio_compra,
                    precio_venta,
                    ROUND(
                        ((precio_venta - precio_compra) / precio_compra) * 100, 2
                    ) AS margen_pct
                FROM producto
                WHERE precio_compra > 0
                ORDER BY margen_pct DESC
                LIMIT %s
            """, (limite,))
            return cursor.fetchall()
        except Exception as e:
            raise BaseDatosError(f"Error al obtener productos por margen: {e}") from e
        finally:
            cursor.close()
 
    def obtener_productos_como_objetos(self) -> list:
        """
        Retorna la lista de productos como instancias de la clase Producto.
        Útil para lógica que requiere el modelo de dominio completo.
        """
        filas = self.obtener_todos_los_productos()
        return [Producto.desde_fila_bd(fila) for fila in filas]
 
    def mostrar_resumen(self) -> None:
        """Imprime en consola un resumen ejecutivo del inventario."""
        total_productos   = self.obtener_total_productos()
        valor_inventario  = self.obtener_valor_total_inventario()
        valor_potencial   = self.obtener_valor_potencial_ventas()
        ganancia_potencial = self.calcular_ganancia_potencial(valor_inventario, valor_potencial)
        stock_bajo        = self.obtener_productos_stock_bajo()
        sin_stock         = self.obtener_productos_sin_stock()
 
        print("\n" + "═" * 50)
        print("     REPORTE DE INVENTARIO — ElectroGabo")
        print("═" * 50)
        print(f"  Fecha de generación   : {obtener_fecha_actual()}")
        print(f"  Total de productos    : {total_productos}")
        print(f"  Valor invertido       : {formatear_moneda(valor_inventario)}")
        print(f"  Potencial de venta    : {formatear_moneda(valor_potencial)}")
        print(f"  Ganancia potencial    : {formatear_moneda(ganancia_potencial)}")
 
        print(f"\n  — Productos con stock bajo (≤ {self.STOCK_MINIMO} uds) —")
        if stock_bajo:
            for id_p, nombre, marca, stock in stock_bajo:
                estado = "⚠ AGOTADO" if stock == 0 else f"⚠ stock: {stock}"
                print(f"  • [{id_p}] {nombre} ({marca}) — {estado}")
        else:
            print("  ✓ Todos los productos tienen stock suficiente.")
 
        if sin_stock:
            print(f"\n  — Productos AGOTADOS ({len(sin_stock)}) —")
            for id_p, nombre, marca in sin_stock:
                print(f"  ✗ [{id_p}] {nombre} ({marca})")
 
        print("\n  — Top 5 productos con mayor margen —")
        top_margen = self.obtener_productos_mayor_margen(5)
        if top_margen:
            for i, (nombre, marca, p_compra, p_venta, margen) in enumerate(top_margen, 1):
                print(f"  {i}. {nombre} ({marca}) | "
                      f"Compra: {formatear_moneda(float(p_compra))} | "
                      f"Venta: {formatear_moneda(float(p_venta))} | "
                      f"Margen: {margen}%")
        else:
            print("  Sin datos aún.")
 
        print("═" * 50 + "\n")
 
    # ── Métodos estáticos ────────────────────────────────────────────────────
 
    @staticmethod
    def calcular_ganancia_potencial(valor_compra: float, valor_venta: float) -> float:
        """
        Método estático: diferencia entre el potencial de venta y el costo invertido.
        No necesita estado de instancia.
        """
        return round(valor_venta - valor_compra, 2)
 
    @staticmethod
    def evaluar_estado_stock(stock: int, stock_minimo: int) -> str:
        """
        Método estático: clasifica el estado de stock de un producto.
        Retorna: 'AGOTADO', 'BAJO', u 'OK'.
        """
        if stock == 0:
            return "AGOTADO"
        if stock <= stock_minimo:
            return "BAJO"
        return "OK"
 
    @staticmethod
    def formatear_fila_consola(id_p, nombre, marca, precio_venta, stock) -> str:
        """Método estático: formatea una fila de producto para consola."""
        return (
            f"  [{id_p}] {nombre} ({marca}) | "
            f"Precio: {formatear_moneda(float(precio_venta))} | "
            f"Stock: {stock}"
        )