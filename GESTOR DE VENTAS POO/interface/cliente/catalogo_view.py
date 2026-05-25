"""
Vista: Catálogo de Productos (Cliente).
Responsabilidad: mostrar el catálogo de productos disponibles al cliente,
con búsqueda por nombre/marca y visualización de precios y stock.
El cliente NO puede modificar ningún dato — solo consulta.
"""
 
import customtkinter as ctk
from tkinter import ttk
 
from interface.components.cards import cabecera_vista, seccion_titulo
from interface.components.tablas import crear_tabla, limpiar
from UTIL.helpers import formatear_moneda
 
 
def abrir_catalogo(parent: ctk.CTkFrame) -> None:
    """Limpia el frame padre y renderiza el catálogo de productos."""
    for w in parent.winfo_children():
        w.destroy()
 
    cabecera_vista(
        parent,
        "🛍 Catálogo de Productos",
        "Consulta los productos disponibles y sus precios",
    )
 
    # ── Barra de búsqueda ─────────────────────────────────────────────────────
    barra = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
    barra.pack(fill="x", padx=30, pady=(0, 10))
 
    ctk.CTkLabel(
        barra, text="🔍  Buscar:",
        font=("Arial", 12), text_color="#64748b",
    ).pack(side="left", padx=(16, 6), pady=12)
 
    entry_buscar = ctk.CTkEntry(
        barra, width=280,
        placeholder_text="Nombre o marca del producto...",
        font=("Arial", 12), border_color="#cbd5e1",
    )
    entry_buscar.pack(side="left", pady=12)
 
    lbl_total = ctk.CTkLabel(
        barra, text="",
        font=("Arial", 11), text_color="gray",
    )
    lbl_total.pack(side="right", padx=16)
 
    ctk.CTkButton(
        barra, text="↺  Recargar",
        width=110, height=34,
        fg_color="#f1f5f9", hover_color="#e2e8f0",
        text_color="#1e293b", font=("Arial", 12),
        border_width=1, border_color="#cbd5e1",
        command=lambda: _recargar(entry_buscar.get()),
    ).pack(side="right", padx=(0, 8), pady=12)
 
    # ── Tabla de productos ────────────────────────────────────────────────────
    seccion_titulo(parent, "📦 Productos Disponibles")
 
    _COLS   = ("ID", "Nombre", "Marca", "Precio", "Disponibilidad")
    _ANCHOS = [70, 260, 140, 130, 130]
 
    tabla = crear_tabla(parent, _COLS, altura=14, anchos=_ANCHOS, expandir=True)
 
    # ── Detalle al seleccionar ────────────────────────────────────────────────
    panel_detalle = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
    panel_detalle.pack(fill="x", padx=30, pady=(0, 20))
 
    lbl_detalle = ctk.CTkLabel(
        panel_detalle,
        text="  Haz doble clic en un producto para ver el detalle.",
        font=("Arial", 11), text_color="#64748b", anchor="w",
    )
    lbl_detalle.pack(anchor="w", padx=16, pady=12)
 
    # ── Lógica de carga ───────────────────────────────────────────────────────
 
    def _recargar(filtro: str = ""):
        limpiar(tabla)
        try:
            from dao.producto_dao import ProductoDAO
            productos = ProductoDAO().obtener_todos()
        except Exception as e:
            lbl_total.configure(text=f"Error: {e}")
            return
 
        filtro_lower = filtro.strip().lower()
        mostrados = 0
 
        for p in productos:
            if filtro_lower and (
                filtro_lower not in p.nombre.lower()
                and filtro_lower not in p.marca.lower()
            ):
                continue
 
            if p.stock == 0:
                disponibilidad = "❌ Agotado"
            elif p.stock <= 5:
                disponibilidad = f"⚠ Bajo stock ({p.stock})"
            else:
                disponibilidad = f"✅ Disponible ({p.stock})"
 
            tabla.insert("", "end", values=(
                p.id_producto,
                p.nombre,
                p.marca,
                formatear_moneda(p.precio_venta),
                disponibilidad,
            ))
            mostrados += 1
 
        lbl_total.configure(text=f"{mostrados} producto(s) encontrado(s)")
 
    def _mostrar_detalle(event=None):
        sel = tabla.selection()
        if not sel:
            return
        valores = list(tabla.item(sel[0])["values"])
        if not valores:
            return
        id_p, nombre, marca, precio, disp = valores
        lbl_detalle.configure(
            text=f"  📦  {nombre}  ·  Marca: {marca}  ·  Precio: {precio}  ·  {disp}",
            text_color="#1e293b",
        )
 
    entry_buscar.bind("<KeyRelease>", lambda e: _recargar(entry_buscar.get()))
    tabla.bind("<Double-1>", _mostrar_detalle)
 
    # Carga inicial
    _recargar()
