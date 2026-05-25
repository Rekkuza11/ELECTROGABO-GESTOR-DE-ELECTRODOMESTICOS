"""
Vista: Catálogo de Productos (Empleado).
Responsabilidad: mostrar el inventario completo al empleado.
El empleado NO puede agregar, editar ni eliminar productos — solo consultar.
"""

import customtkinter as ctk
from interface.controllers.producro_controller import ProductoController
from interface.components.cards import cabecera_vista, seccion_titulo
from interface.components.tablas import crear_tabla, limpiar
from interface.components.botones import btn_secundario
from interface.components.mensajes import alerta_inline
from UTIL.helpers import formatear_moneda
from models.producto import Producto


_CTRL = ProductoController()

_COLS   = ("ID", "Nombre", "Marca", "Precio Venta", "Stock", "Estado", "Margen %")
_ANCHOS = [60, 200, 130, 120, 80, 100, 90]


def abrir_catalogo_empleado(parent: ctk.CTkFrame) -> None:
    """Limpia el frame padre y renderiza el catálogo de productos (solo lectura)."""
    for w in parent.winfo_children():
        w.destroy()

    cabecera_vista(parent,
                   "📦 Catálogo de Productos",
                   "Consulta el inventario disponible — vista de solo lectura")

    # ── Barra de búsqueda y recarga ───────────────────────────────────────────
    barra = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
    barra.pack(fill="x", padx=30, pady=(0, 8))

    entry_buscar = ctk.CTkEntry(
        barra, width=260, placeholder_text="🔍  Buscar por nombre o marca...",
        font=("Arial", 12), border_color="#cbd5e1",
    )
    entry_buscar.pack(side="left", padx=12, pady=10)

    # Filtro de estado
    combo_filtro = ctk.CTkComboBox(
        barra, values=["Todos", "Con stock", "Stock bajo", "Agotados"],
        width=160, font=("Arial", 12),
        border_color="#cbd5e1", button_color="#0891b2",
    )
    combo_filtro.set("Todos")
    combo_filtro.pack(side="left", padx=(0, 8), pady=10)

    # Aviso de solo lectura
    ctk.CTkLabel(
        barra,
        text="🔒  Solo lectura",
        font=("Arial", 11), text_color="#0369a1",
        fg_color="#e0f2fe", corner_radius=6,
    ).pack(side="right", padx=12, pady=10)

    # ── Resumen rápido ────────────────────────────────────────────────────────
    resumen_frame = ctk.CTkFrame(parent, fg_color="transparent")
    resumen_frame.pack(fill="x", padx=30, pady=(0, 8))

    lbl_total   = ctk.CTkLabel(resumen_frame, text="Total: —",
                                font=("Arial", 12), text_color="#64748b")
    lbl_total.pack(side="left", padx=(0, 16))

    lbl_agotados = ctk.CTkLabel(resumen_frame, text="Agotados: —",
                                 font=("Arial", 12), text_color="#dc2626")
    lbl_agotados.pack(side="left", padx=(0, 16))

    lbl_bajo = ctk.CTkLabel(resumen_frame, text="Stock bajo: —",
                             font=("Arial", 12), text_color="#ca8a04")
    lbl_bajo.pack(side="left")

    # ── Tabla ─────────────────────────────────────────────────────────────────
    seccion_titulo(parent, "📋 Inventario Completo")
    tabla = crear_tabla(parent, _COLS, altura=14, anchos=_ANCHOS, expandir=True)

    # ── Panel de detalle (al seleccionar) ─────────────────────────────────────
    detalle_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10, height=80)
    detalle_frame.pack(fill="x", padx=30, pady=(0, 16))
    detalle_frame.pack_propagate(False)

    lbl_detalle = ctk.CTkLabel(
        detalle_frame,
        text="Haz doble clic en un producto para ver su detalle.",
        font=("Arial", 12), text_color="#64748b",
    )
    lbl_detalle.pack(expand=True)

    # ── Lógica ────────────────────────────────────────────────────────────────

    _todos_los_productos: list = []

    def _evaluar_estado(stock: int) -> str:
        if stock == 0:
            return "AGOTADO"
        if stock <= 5:
            return "BAJO"
        return "Disponible"

    def _recargar(filtro_texto: str = "", filtro_estado: str = "Todos"):
        limpiar(tabla)
        _todos_los_productos.clear()

        try:
            productos = _CTRL.listar()
        except Exception as e:
            alerta_inline(parent, f"Error al cargar productos: {e}", tipo="error")
            return

        _todos_los_productos.extend(productos)

        total = len(productos)
        agotados = sum(1 for p in productos if p.stock == 0)
        bajo = sum(1 for p in productos if 0 < p.stock <= 5)
        lbl_total.configure(text=f"Total: {total}")
        lbl_agotados.configure(text=f"Agotados: {agotados}")
        lbl_bajo.configure(text=f"Stock bajo: {bajo}")

        filtro_lower = filtro_texto.strip().lower()

        for p in productos:
            # Filtro de texto
            if filtro_lower and (
                filtro_lower not in p.nombre.lower()
                and filtro_lower not in p.marca.lower()
            ):
                continue

            estado = _evaluar_estado(p.stock)

            # Filtro de estado
            if filtro_estado == "Con stock" and p.stock == 0:
                continue
            if filtro_estado == "Stock bajo" and (p.stock == 0 or p.stock > 5):
                continue
            if filtro_estado == "Agotados" and p.stock != 0:
                continue

            try:
                margen = f"{p.calcular_margen(p.precio_compra, p.precio_venta)}%"
            except Exception:
                margen = "N/A"

            tabla.insert("", "end", values=(
                p.id_producto,
                p.nombre,
                p.marca,
                formatear_moneda(p.precio_venta),
                p.stock,
                estado,
                margen,
            ))

    def _filtrar(event=None):
        _recargar(entry_buscar.get(), combo_filtro.get())

    def _ver_detalle(event=None):
        seleccion = tabla.selection()
        if not seleccion:
            return
        valores = tabla.item(seleccion[0])["values"]
        id_p, nombre, marca, precio_v, stock, estado, margen = valores
        lbl_detalle.configure(
            text=(
                f"📦  {nombre}  ({marca})   |   "
                f"Precio venta: {precio_v}   |   "
                f"Stock: {stock}   |   "
                f"Estado: {estado}   |   "
                f"Margen: {margen}"
            ),
            text_color="#1e293b",
        )

    entry_buscar.bind("<KeyRelease>", _filtrar)
    combo_filtro.bind("<<ComboboxSelected>>", _filtrar)
    tabla.bind("<Double-1>", _ver_detalle)

    btn_secundario(barra, "↺  Recargar", _recargar, ancho=110, alto=34).pack(
        side="left", padx=(0, 8), pady=10
    )

    # Carga inicial
    _recargar()