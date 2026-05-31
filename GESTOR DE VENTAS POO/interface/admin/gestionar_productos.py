"""
Vista: Gestión de Productos.
Responsabilidad: renderizar el CRUD de productos dentro del frame de contenido
del dashboard administrador.

CORRECCIONES — Fase 3:
  - #4: entry_id cambia de campo_numero a campo_texto y el placeholder refleja
        que el ID puede ser alfanumérico (varchar(20) en BD, ej. 'PD66322').
"""

import customtkinter as ctk
from interface.controllers.producro_controller import ProductoController
from interface.components.cards import cabecera_vista, seccion_titulo
from interface.components.tablas import crear_tabla, limpiar, fila_seleccionada
from interface.components.formularios import (
    campo_texto, campo_numero, panel_formulario, limpiar_campos
)
from interface.components.mensajes import (
    LabelEstado, confirmar, exito, error as msg_error
)
from interface.components.botones import btn_peligro, btn_secundario, btn_exito
from UTIL.helpers import formatear_moneda


_CTRL = ProductoController()

_COLS   = ("ID", "Nombre", "Marca", "P. Compra", "P. Venta", "Stock", "Margen %")
_ANCHOS = [80, 200, 120, 110, 110, 70, 80]


def abrir_gestionar_productos(parent: ctk.CTkFrame) -> None:
    """Limpia el frame padre y renderiza la vista de gestión de productos."""
    for w in parent.winfo_children():
        w.destroy()

    cabecera_vista(parent,
                   "📦 Gestión de Productos",
                   "Administra el catálogo e inventario de la tienda")

    # ── Mensaje de error global ───────────────────────────────────────────────
    lbl_error_global = ctk.CTkLabel(
        parent, text="", font=("Arial", 12, "bold"),
        text_color="#dc2626", fg_color="#fee2e2",
        corner_radius=8, anchor="w"
    )

    def _mostrar_error_global(msg: str):
        lbl_error_global.configure(text=f"  ✗  {msg}")
        lbl_error_global.pack(fill="x", padx=30, pady=(0, 8))

    def _ocultar_error_global():
        lbl_error_global.configure(text="")
        lbl_error_global.pack_forget()

    # ── Layout: izquierda tabla / derecha formulario ──────────────────────────
    layout = ctk.CTkFrame(parent, fg_color="transparent")
    layout.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # Panel izquierdo — tabla
    panel_izq = ctk.CTkFrame(layout, fg_color="transparent")
    panel_izq.pack(side="left", fill="both", expand=True, padx=(0, 10))

    barra = ctk.CTkFrame(panel_izq, fg_color="white", corner_radius=10)
    barra.pack(fill="x", pady=(0, 8))

    entry_buscar = ctk.CTkEntry(
        barra, width=220, placeholder_text="🔍  Buscar producto...",
        font=("Arial", 12), border_color="#cbd5e1"
    )
    entry_buscar.pack(side="left", padx=12, pady=10)

    seccion_titulo(panel_izq, "📋 Inventario Completo")
    tabla = crear_tabla(panel_izq, _COLS, altura=12, anchos=_ANCHOS, expandir=True)

    # Panel derecho — formulario
    panel_der = ctk.CTkFrame(layout, fg_color="transparent", width=340)
    panel_der.pack(side="right", fill="y")
    panel_der.pack_propagate(False)

    form_body = panel_formulario(panel_der, "➕ Nuevo / Editar Producto")

    # CORRECCIÓN #4: campo_texto (no campo_numero) y placeholder alfanumérico
    entry_id       = campo_texto(form_body,  "ID Producto:",   "Ej: PD66322")
    entry_nombre   = campo_texto(form_body,  "Nombre:",        "Ej: Multímetro Digital")
    entry_marca    = campo_texto(form_body,  "Marca:",         "Ej: Fluke")
    entry_p_compra = campo_numero(form_body, "Precio Compra:", "0.00")
    entry_p_venta  = campo_numero(form_body, "Precio Venta:",  "0.00")
    entry_stock    = campo_numero(form_body, "Stock:",         "0")

    aviso_id = ctk.CTkFrame(form_body, fg_color="#fefce8", corner_radius=8)
    aviso_id.pack(fill="x", pady=(2, 6))
    ctk.CTkLabel(aviso_id,
                 text="⚠  El ID es obligatorio, único y puede ser alfanumérico.\n"
                      "Al editar, el ID no se puede cambiar.",
                 font=("Arial", 10), text_color="#92400e",
                 justify="left").pack(anchor="w", padx=10, pady=6)

    estado = LabelEstado(form_body)
    _id_edicion = {"valor": None}

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _set_id_editable(editable: bool):
        entry_id.configure(state="normal" if editable else "disabled",
                           fg_color="white" if editable else "#f1f5f9",
                           text_color="#1e293b" if editable else "#94a3b8")

    def _limpiar_form():
        limpiar_campos(entry_id, entry_nombre, entry_marca,
                       entry_p_compra, entry_p_venta, entry_stock)
        _id_edicion["valor"] = None
        _set_id_editable(True)
        estado.limpiar()

    def _recargar_tabla(filtro: str = ""):
        limpiar(tabla)
        _ocultar_error_global()
        try:
            productos = _CTRL.listar()
        except Exception as e:
            _mostrar_error_global(f"Error al conectar con la base de datos: {e}")
            return

        if not productos:
            tabla.insert("", "end", values=(
                "Sin productos en BD", "", "", "", "", "", ""
            ))
            return

        filtro_lower = filtro.strip().lower()
        for p in productos:
            try:
                if filtro_lower and (
                    filtro_lower not in p.nombre.lower()
                    and filtro_lower not in p.marca.lower()
                ):
                    continue
                try:
                    margen = f"{p.calcular_margen(p.precio_compra, p.precio_venta)}%"
                except Exception:
                    margen = "N/A"
                tabla.insert("", "end", values=(
                    p.id_producto,
                    p.nombre,
                    p.marca,
                    formatear_moneda(p.precio_compra),
                    formatear_moneda(p.precio_venta),
                    p.stock,
                    margen,
                ))
            except Exception:
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
                    entry_id.get(),
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
        limpiar_campos(entry_id, entry_nombre, entry_marca,
                       entry_p_compra, entry_p_venta, entry_stock)

        _set_id_editable(True)
        entry_id.insert(0, str(fila[0]))
        _set_id_editable(False)

        entry_nombre.insert(0,   str(fila[1]))
        entry_marca.insert(0,    str(fila[2]))
        entry_p_compra.insert(0, str(fila[3]).replace("$", "").replace(",", ""))
        entry_p_venta.insert(0,  str(fila[4]).replace("$", "").replace(",", ""))
        entry_stock.insert(0,    str(fila[5]))
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

    # ── Botones del formulario ────────────────────────────────────────────────
    fila_btns = ctk.CTkFrame(form_body, fg_color="transparent")
    fila_btns.pack(fill="x", pady=(12, 0))
    btn_exito(fila_btns, "💾 Guardar", _guardar,
              ancho=130, alto=36).pack(side="left", padx=(0, 8))
    btn_peligro(fila_btns, "🗑 Eliminar", _eliminar,
                ancho=130, alto=36).pack(side="left", padx=(0, 8))
    btn_secundario(fila_btns, "✕ Limpiar", _limpiar_form,
                   ancho=100, alto=36).pack(side="left")

    btn_secundario(barra, "↺  Recargar", _recargar_tabla,
                   ancho=110, alto=34).pack(side="left", padx=(0, 8), pady=10)

    entry_buscar.bind("<KeyRelease>", lambda e: _recargar_tabla(entry_buscar.get()))
    tabla.bind("<Double-1>", _cargar_en_form)

    _recargar_tabla()