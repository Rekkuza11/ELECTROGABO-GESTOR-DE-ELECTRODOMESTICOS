"""
Vista: Gestión de Productos.
Responsabilidad: renderizar el CRUD de productos dentro del frame de contenido
del dashboard administrador.
"""

import customtkinter as ctk
from interface.controllers.producro_controller import ProductoController
from interface.components import tarjetas as cards, tablas, formularios, mensajes, botones
from interface.components.cards import cabecera_vista, seccion_titulo, panel_blanco
from interface.components.tablas import crear_tabla, limpiar, fila_seleccionada
from interface.components.formularios import campo_texto, campo_numero, panel_formulario, limpiar_campos
from interface.components.mensajes import LabelEstado, confirmar, exito, error as msg_error
from interface.components.botones import btn_primario, btn_peligro, btn_secundario, btn_exito
from UTIL.helpers import formatear_moneda


_CTRL = ProductoController()

# Columnas de la tabla
_COLS = ("ID", "Nombre", "Marca", "P. Compra", "P. Venta", "Stock", "Margen %")
_ANCHOS = [60, 200, 120, 110, 110, 70, 80]


def abrir_gestionar_productos(parent: ctk.CTkFrame) -> None:
    """Limpia el frame padre y renderiza la vista de gestión de productos."""
    for w in parent.winfo_children():
        w.destroy()

    cabecera_vista(parent,
                   "📦 Gestión de Productos",
                   "Administra el catálogo e inventario de la tienda")

    # ── Layout: izquierda tabla / derecha formulario ──────────────────────────
    layout = ctk.CTkFrame(parent, fg_color="transparent")
    layout.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # Panel izquierdo — tabla
    panel_izq = ctk.CTkFrame(layout, fg_color="transparent")
    panel_izq.pack(side="left", fill="both", expand=True, padx=(0, 10))

    # Barra de búsqueda + botones de acción rápida
    barra = ctk.CTkFrame(panel_izq, fg_color="white", corner_radius=10)
    barra.pack(fill="x", pady=(0, 8))

    entry_buscar = ctk.CTkEntry(barra, width=220, placeholder_text="🔍  Buscar producto...",
                                font=("Arial", 12), border_color="#cbd5e1")
    entry_buscar.pack(side="left", padx=12, pady=10)

    # El comando se asigna tras definir _recargar_tabla más abajo
    btn_recargar = btn_secundario(barra, "↺  Recargar", ancho=110, alto=34)
    btn_recargar.pack(side="left", padx=(0, 8), pady=10)

    seccion_titulo(panel_izq, "📋 Inventario Completo")

    tabla = crear_tabla(panel_izq, _COLS, altura=12, anchos=_ANCHOS, expandir=True)

    # Panel derecho — formulario
    panel_der = ctk.CTkFrame(layout, fg_color="transparent", width=340)
    panel_der.pack(side="right", fill="y")
    panel_der.pack_propagate(False)

    form_body = panel_formulario(panel_der, "➕ Nuevo / Editar Producto")

    entry_nombre   = campo_texto(form_body,  "Nombre:",       "Ej: Multímetro Digital")
    entry_marca    = campo_texto(form_body,  "Marca:",        "Ej: Fluke")
    entry_p_compra = campo_numero(form_body, "Precio Compra:", "0.00")
    entry_p_venta  = campo_numero(form_body, "Precio Venta:",  "0.00")
    entry_stock    = campo_numero(form_body, "Stock:",         "0")

    estado = LabelEstado(form_body)

    # ID oculto para modo edición
    _id_edicion = {"valor": None}

    # ── Acciones del formulario ───────────────────────────────────────────────
    def _limpiar_form():
        limpiar_campos(entry_nombre, entry_marca,
                       entry_p_compra, entry_p_venta, entry_stock)
        _id_edicion["valor"] = None
        estado.limpiar()

    def _recargar_tabla(filtro: str = ""):
        limpiar(tabla)
        try:
            productos = _CTRL.listar()
        except Exception as e:
            estado.mostrar(f"Error al cargar productos: {e}", "error")
            return
        if not productos:
            estado.mostrar("No hay productos registrados en la base de datos.", "advertencia")
            return
        estado.limpiar()
        for p in productos:
            try:
                if filtro.lower() in p.nombre.lower() or filtro.lower() in p.marca.lower():
                    # Calcular margen de forma segura — precio_compra podria ser 0
                    try:
                        margen = f"{p.calcular_margen(p.precio_compra, p.precio_venta)}%"
                    except Exception:
                        margen = "N/A"
                    tabla.insert("", "end", values=(
                        p.id_producto, p.nombre, p.marca,
                        formatear_moneda(p.precio_compra),
                        formatear_moneda(p.precio_venta),
                        p.stock, margen,
                    ))
            except Exception as e:
                # Si un producto falla, saltarlo y continuar con los demás
                continue

    def _guardar():
        id_ed = _id_edicion["valor"]
        try:
            if id_ed:
                _CTRL.actualizar(
                    id_ed,
                    entry_nombre.get(), entry_marca.get(),
                    entry_p_compra.get(), entry_p_venta.get(), entry_stock.get(),
                )
                estado.mostrar("Producto actualizado correctamente.", "exito")
            else:
                _CTRL.agregar(
                    entry_nombre.get(), entry_marca.get(),
                    entry_p_compra.get(), entry_p_venta.get(), entry_stock.get(),
                )
                estado.mostrar("Producto registrado correctamente.", "exito")
            _limpiar_form()
            _recargar_tabla()
        except Exception as e:
            estado.mostrar(str(e), "error")

    def _cargar_en_form(event=None):
        fila = fila_seleccionada(tabla)
        if not fila:
            return
        _id_edicion["valor"] = fila[0]
        # Quitar formato de moneda para editar
        limpiar_campos(entry_nombre, entry_marca,
                       entry_p_compra, entry_p_venta, entry_stock)
        entry_nombre.insert(0, fila[1])
        entry_marca.insert(0, fila[2])
        entry_p_compra.insert(0, str(fila[3]).replace("$", "").replace(",", ""))
        entry_p_venta.insert(0, str(fila[4]).replace("$", "").replace(",", ""))
        entry_stock.insert(0, str(fila[5]))
        estado.mostrar(f"Editando producto ID {fila[0]}", "info")

    def _eliminar():
        fila = fila_seleccionada(tabla)
        if not fila:
            estado.mostrar("Selecciona un producto de la tabla.", "advertencia")
            return
        if not confirmar("Eliminar producto",
                         f"¿Eliminar '{fila[1]}' permanentemente?"):
            return
        try:
            _CTRL.eliminar(fila[0])
            exito("Eliminado", f"Producto '{fila[1]}' eliminado.")
            _limpiar_form()
            _recargar_tabla()
        except Exception as e:
            msg_error("Error", str(e))

    # Botones del formulario
    fila_btns = ctk.CTkFrame(form_body, fg_color="transparent")
    fila_btns.pack(fill="x", pady=(12, 0))
    btn_exito(fila_btns,     "💾 Guardar",  _guardar,  ancho=130, alto=36).pack(side="left", padx=(0, 8))
    btn_peligro(fila_btns,   "🗑 Eliminar", _eliminar, ancho=130, alto=36).pack(side="left", padx=(0, 8))
    btn_secundario(fila_btns, "✕ Limpiar",  _limpiar_form, ancho=100, alto=36).pack(side="left")

    # Conectar botón Recargar ahora que _recargar_tabla está definida
    btn_recargar.configure(command=_recargar_tabla)

    # Buscador reactivo
    entry_buscar.bind("<KeyRelease>", lambda e: _recargar_tabla(entry_buscar.get()))

    # Doble clic en fila → carga en formulario
    tabla.bind("<Double-1>", _cargar_en_form)

    # Carga inicial
    _recargar_tabla()