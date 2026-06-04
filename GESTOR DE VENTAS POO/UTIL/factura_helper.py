"""
UTIL/factura_helper.py
Lógica centralizada de generación de factura PDF.
Importada por gestionar_ventas.py y ventas_view.py para no duplicar código.
Aplica SRP: única responsabilidad — orquestar los datos y delegar al FacturaPDF.
"""

import os
from database import DatabaseConnection
from dao.detalle_venta_dao import DetalleVentaDAO
from dao.producto_dao import ProductoDAO
from reports.factura_pdf import FacturaPDF
from UTIL.config_empresa import EMPRESA_CONFIG


def generar_factura(id_venta) -> str:
    """
    Genera la factura PDF de una venta y la guarda en la carpeta 'facturas/'.

    Args:
        id_venta — ID de la venta a facturar.

    Returns:
        Ruta absoluta del archivo PDF generado.

    Raises:
        ValueError    — si la venta no existe en la BD.
        Exception     — si ocurre error de BD o al generar el PDF.
    """
    # ── 1. Datos de la venta + cliente + vendedor ─────────────────────────────
    conn = DatabaseConnection().obtener_conexion()
    cur  = conn.cursor()
    cur.execute("""
        SELECT
            v.id_venta,
            v.fecha,
            v.total,
            c.nombre     AS cli_nombre,
            c.telefono   AS cli_tel,
            c.direccion  AS cli_dir,
            COALESCE(e.nombre, CONCAT(u.id_usuario, ' (Admin)')) AS empleado
        FROM venta v
        JOIN  cliente  c ON v.id_cliente  = c.id_cliente
        JOIN  usuario  u ON v.id_empleado = u.id_usuario
        LEFT JOIN empleado e ON v.id_empleado = e.id_empleado
        WHERE v.id_venta = %s
    """, (id_venta,))
    fila = cur.fetchone()
    cur.close()

    if not fila:
        raise ValueError(f"No existe la venta con ID {id_venta}.")

    id_v, fecha, total, cli_nombre, cli_tel, cli_dir, empleado = fila

    venta_dict = {
        "id_venta": id_v,
        "fecha":    fecha,
        "total":    total,
        "empleado": empleado,
        "cliente": {
            "nombre":    cli_nombre,
            "telefono":  cli_tel   or "—",
            "direccion": cli_dir   or "—",
        },
    }

    # ── 2. Líneas de detalle ──────────────────────────────────────────────────
    # formato fila: (id_detalle, id_venta, id_producto, cantidad, precio_unitario, subtotal)
    detalles_raw = DetalleVentaDAO().obtener_por_venta(id_venta)
    prod_dao     = ProductoDAO()
    detalles     = []

    for fila_d in detalles_raw:
        _, __, id_prod, cant, precio_u, sub = fila_d
        try:
            prod     = prod_dao.obtener_por_id(id_prod)
            nombre_p = prod.nombre
        except Exception:
            nombre_p = f"Producto #{id_prod}"
        detalles.append((nombre_p, cant, precio_u, sub))

    # ── 3. Generar PDF ────────────────────────────────────────────────────────
    carpeta = "facturas"
    os.makedirs(carpeta, exist_ok=True)

    ruta = FacturaPDF(EMPRESA_CONFIG).generar(venta_dict, detalles, carpeta)
    return os.path.abspath(ruta)