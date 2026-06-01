"""
Vista: Historial de Compras del Cliente.
Responsabilidad: mostrar al cliente sus propias compras con detalle
de productos por venta.

Fase 9 · Corrección NE-3:
  - Se elimina la función local _crear_tabla() duplicada que existía
    al final de este módulo.
  - Se elimina el import directo de tkinter.ttk, que solo era necesario
    para la función local eliminada.
  - Todas las tablas ahora se crean mediante crear_tabla() del componente
    centralizado interface.components.tablas, coherente con el resto de
    vistas del sistema (ventas_report, clientes_report, inventario_report,
    clientes_view — ya corregidos en Fase 6 / corrección #20).
  - Se usa expandir=False en ambas llamadas para replicar el comportamiento
    original de fill="x" de la función local.
"""

import customtkinter as ctk

from interface.components.cards import cabecera_vista, seccion_titulo
from interface.components.tablas import crear_tabla, limpiar
from interface.components.mensajes import alerta_inline
from UTIL.helpers import formatear_moneda


def abrir_historial(parent: ctk.CTkFrame, id_usuario: str) -> None:
    """Limpia el frame padre y renderiza el historial de compras del cliente."""
    for w in parent.winfo_children():
        w.destroy()

    cabecera_vista(
        parent,
        "📋 Mis Compras",
        "Consulta el detalle de todas tus transacciones",
    )

    # ── Tarjetas de resumen ───────────────────────────────────────────────────
    try:
        from reports.reporte_clientes import ReporteClientes
        rc = ReporteClientes()
        historial     = rc.obtener_historial_cliente(id_usuario)
        total_compras = len(historial)
        monto_total   = sum(float(row[2]) for row in historial) if historial else 0.0
        promedio      = round(monto_total / total_compras, 2) if total_compras else 0.0
    except Exception:
        historial     = []
        total_compras = 0
        monto_total   = 0.0
        promedio      = 0.0

    fila_cards = ctk.CTkFrame(parent, fg_color="transparent")
    fila_cards.pack(fill="x", padx=30, pady=(0, 15))

    _tarjeta(fila_cards, "🛒", "#2563eb",
             str(total_compras), "Total Compras", "Pedidos realizados")
    _tarjeta(fila_cards, "$", "#22c55e",
             formatear_moneda(monto_total), "Total Gastado", "Historial acumulado")
    _tarjeta(fila_cards, "~", "#a855f7",
             formatear_moneda(promedio), "Ticket Promedio", "Por transacción")

    # ── Área scrollable ───────────────────────────────────────────────────────
    scroll = ctk.CTkScrollableFrame(parent, fg_color="#f1f5f9")
    scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # ── Tabla principal de ventas ─────────────────────────────────────────────
    seccion_titulo(scroll, "🧾 Listado de Compras")

    cols_hist = ("ID Venta", "Fecha", "Total", "Atendido por")

    # NE-3: crear_tabla() centralizado — expandir=False replica fill="x" original
    tabla_hist = crear_tabla(
        scroll, cols_hist,
        altura=6, anchos=[100, 180, 130, 180], expandir=False,
    )

    if historial:
        for id_v, fecha, total, empleado in historial:
            tabla_hist.insert("", "end", values=(
                id_v, str(fecha)[:16],
                formatear_moneda(float(total)),
                empleado,
            ))
    else:
        tabla_hist.insert("", "end",
                          values=("Sin compras registradas", "-", "-", "-"))

    # ── Detalle de productos de la venta seleccionada ─────────────────────────
    seccion_titulo(scroll, "🔍 Detalle de la Venta Seleccionada")

    detalle_frame = ctk.CTkFrame(scroll, fg_color="white", corner_radius=10)
    detalle_frame.pack(fill="x", pady=(0, 10))

    lbl_instruccion = ctk.CTkLabel(
        detalle_frame,
        text="  Haz doble clic en una venta para ver sus productos.",
        font=("Arial", 12), text_color="#64748b", anchor="w",
    )
    lbl_instruccion.pack(anchor="w", padx=15, pady=12)

    cols_det = ("Producto", "Marca", "Cantidad", "Precio Unitario", "Subtotal")

    # NE-3: crear_tabla() centralizado — expandir=False replica fill="x" original
    tabla_det = crear_tabla(
        detalle_frame, cols_det,
        altura=5, anchos=[200, 130, 90, 140, 130], expandir=False,
    )

    lbl_total_venta = ctk.CTkLabel(
        detalle_frame, text="",
        font=("Arial", 13, "bold"), text_color="#1e293b",
    )
    lbl_total_venta.pack(anchor="e", padx=20, pady=(4, 12))

    # ── Lógica al seleccionar venta ───────────────────────────────────────────
    def _ver_detalle(event=None):
        sel = tabla_hist.selection()
        if not sel:
            return
        valores = tabla_hist.item(sel[0])["values"]
        if not valores or valores[0] == "Sin compras registradas":
            return

        id_venta = valores[0]

        # Limpiar tabla de detalle
        for row in tabla_det.get_children():
            tabla_det.delete(row)
        lbl_total_venta.configure(text="")
        lbl_instruccion.configure(text="")

        try:
            from dao.detalle_venta_dao import DetalleVentaDAO
            from dao.producto_dao import ProductoDAO
            detalles = DetalleVentaDAO().obtener_por_venta(id_venta)
            prod_dao = ProductoDAO()

            subtotal_acum = 0.0
            if detalles:
                for fila in detalles:
                    # fila: (id_detalle, id_venta, id_producto,
                    #         cantidad, precio_unitario, subtotal)
                    _, __, id_prod, cant, precio_u, sub = fila
                    try:
                        prod  = prod_dao.obtener_por_id(id_prod)
                        nombre = prod.nombre
                        marca  = prod.marca
                    except Exception:
                        nombre = f"Producto #{id_prod}"
                        marca  = "-"
                    subtotal_acum += float(sub)
                    tabla_det.insert("", "end", values=(
                        nombre, marca,
                        int(cant),
                        formatear_moneda(float(precio_u)),
                        formatear_moneda(float(sub)),
                    ))
            else:
                tabla_det.insert("", "end",
                                 values=("Sin detalle disponible", "-", "-", "-", "-"))

            lbl_total_venta.configure(
                text=f"Total de la venta:  {formatear_moneda(subtotal_acum)}"
            )

        except Exception as e:
            tabla_det.insert("", "end",
                             values=(f"Error: {e}", "-", "-", "-", "-"))

    tabla_hist.bind("<Double-1>", _ver_detalle)


# ── Helpers internos ──────────────────────────────────────────────────────────

def _tarjeta(parent, icono, color, valor, titulo, subtitulo):
    """Tarjeta de estadística compacta para el panel de resumen."""
    card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12, height=150)
    card.pack(side="left", expand=True, fill="both", padx=(0, 10))
    card.pack_propagate(False)

    ctk.CTkLabel(card, text=icono, font=("Arial", 20, "bold"),
                 fg_color=color, text_color="white",
                 width=45, height=45, corner_radius=10).pack(
                     anchor="w", padx=20, pady=(18, 8))
    ctk.CTkLabel(card, text=valor,    font=("Arial", 20, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(card, text=titulo,   font=("Arial", 13, "bold"),
                 text_color="#1e293b").pack(anchor="w", padx=20)
    ctk.CTkLabel(card, text=subtitulo, font=("Arial", 11),
                 text_color="gray").pack(anchor="w", padx=20, pady=(0, 18))