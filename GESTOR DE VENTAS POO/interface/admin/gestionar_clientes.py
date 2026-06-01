"""
Vista: Gestión de Clientes.
Responsabilidad: renderizar el CRUD de clientes dentro del frame de contenido
del dashboard administrador.

NOTA DE PRIVACIDAD: El administrador NO ingresa la contraseña del cliente.
Se genera automáticamente una contraseña temporal que el cliente debe cambiar
en su primer inicio de sesión.

CORRECCIONES — Fase 3:
  - #8: placeholder de ID corregido de 'Ej: CLI001' a 'Ej: 443322'.
        usuario.id_cliente es int NOT NULL; el string 'CLI001' era rechazado
        por la BD.  La validación numérica ahora vive en ClienteController.

FASE 8 — Eliminación segura:
  - _eliminar() llama a ClienteDAO.tiene_ventas() antes de intentar el DELETE.
    Si el cliente tiene ventas asociadas, se muestra un aviso comprensible al
    usuario en lugar de dejar que el motor lance un FK constraint error crudo.
"""

import secrets
import string
import customtkinter as ctk
from interface.controllers.cliente__controller import ClienteController
from interface.components.cards import cabecera_vista, seccion_titulo
from interface.components.tablas import crear_tabla, limpiar, fila_seleccionada
from interface.components.formularios import (
    campo_texto, panel_formulario, limpiar_campos
)
from interface.components.mensajes import LabelEstado, confirmar, exito, error as msg_error
from interface.components.botones import btn_exito, btn_peligro, btn_secundario


_CTRL = ClienteController()

_COLS   = ("ID", "Nombre", "Teléfono", "Dirección")
_ANCHOS = [100, 220, 130, 260]


def _generar_password_temporal(longitud: int = 10) -> str:
    """Genera una contraseña temporal aleatoria segura."""
    caracteres = string.ascii_letters + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(longitud))


def abrir_gestionar_clientes(parent: ctk.CTkFrame) -> None:
    """Limpia el frame padre y renderiza la vista de gestión de clientes."""
    for w in parent.winfo_children():
        w.destroy()

    cabecera_vista(parent,
                   "👥 Gestión de Clientes",
                   "Registra, consulta y elimina clientes del sistema")

    layout = ctk.CTkFrame(parent, fg_color="transparent")
    layout.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # ── Panel izquierdo — tabla ───────────────────────────────────────────────
    panel_izq = ctk.CTkFrame(layout, fg_color="transparent")
    panel_izq.pack(side="left", fill="both", expand=True, padx=(0, 10))

    barra = ctk.CTkFrame(panel_izq, fg_color="white", corner_radius=10)
    barra.pack(fill="x", pady=(0, 8))

    entry_buscar = ctk.CTkEntry(barra, width=220,
                                placeholder_text="🔍  Buscar cliente...",
                                font=("Arial", 12), border_color="#cbd5e1")
    entry_buscar.pack(side="left", padx=12, pady=10)

    seccion_titulo(panel_izq, "📋 Listado de Clientes")
    tabla = crear_tabla(panel_izq, _COLS, altura=12, anchos=_ANCHOS, expandir=True)

    # ── Panel derecho — formulario ────────────────────────────────────────────
    panel_der = ctk.CTkFrame(layout, fg_color="transparent", width=340)
    panel_der.pack(side="right", fill="y")
    panel_der.pack_propagate(False)

    form_body = panel_formulario(panel_der, "➕ Registrar Nuevo Cliente")

    # CORRECCIÓN #8: placeholder refleja que el ID debe ser un número entero
    entry_id       = campo_texto(form_body, "ID Cliente:",  "Ej: 443322")
    entry_nombre   = campo_texto(form_body, "Nombre:",      "Nombre completo")
    entry_telefono = campo_texto(form_body, "Teléfono:",    "Ej: 3001234567")
    entry_dir      = campo_texto(form_body, "Dirección:",   "Calle / barrio")

    aviso = ctk.CTkFrame(form_body, fg_color="#f0f9ff", corner_radius=8)
    aviso.pack(fill="x", pady=(6, 2))
    ctk.CTkLabel(aviso,
                 text="🔐  La contraseña se genera automáticamente.\n"
                      "El cliente la recibirá y podrá cambiarla al ingresar.",
                 font=("Arial", 10), text_color="#0369a1",
                 justify="left").pack(anchor="w", padx=10, pady=8)

    lbl_pwd_generada = ctk.CTkLabel(form_body, text="", font=("Arial", 11),
                                    text_color="#15803d", wraplength=280)
    lbl_pwd_generada.pack(anchor="w", padx=4, pady=(2, 0))

    estado = LabelEstado(form_body)

    # ── Acciones ──────────────────────────────────────────────────────────────
    def _limpiar_form():
        limpiar_campos(entry_id, entry_nombre, entry_telefono, entry_dir)
        lbl_pwd_generada.configure(text="")
        estado.limpiar()

    def _recargar_tabla(filtro: str = ""):
        limpiar(tabla)
        try:
            clientes = _CTRL.listar()
        except Exception as e:
            msg_error("Error", str(e))
            return
        for c in clientes:
            if (filtro.lower() in c.nombre.lower()
                    or filtro.lower() in str(c.id_usuario).lower()):
                tabla.insert("", "end", values=(
                    c.id_usuario, c.nombre, c.telefono, c.direccion
                ))

    def _registrar():
        pwd_temp = _generar_password_temporal()
        try:
            _CTRL.agregar(
                entry_id.get(), entry_nombre.get(),
                entry_telefono.get(), entry_dir.get(), pwd_temp,
            )
            estado.mostrar("Cliente registrado correctamente.", "exito")
            lbl_pwd_generada.configure(
                text=f"🔑 Contraseña temporal: {pwd_temp}\n"
                     "(Entréguela al cliente de forma segura)"
            )
            limpiar_campos(entry_id, entry_nombre, entry_telefono, entry_dir)
            _recargar_tabla()
        except Exception as e:
            estado.mostrar(str(e), "error")

    def _eliminar():
        """
        FASE 8 — Pre-valida FK antes de intentar el DELETE.

        1. Verifica que haya una fila seleccionada.
        2. Pide confirmación al usuario.
        3. Llama a ClienteDAO.tiene_ventas() para detectar dependencias en
           la tabla venta antes de invocar _CTRL.eliminar().
        4. Si tiene ventas, muestra un aviso claro sin tocar la BD.
        5. Si no tiene ventas, procede con la eliminación normal.
        """
        fila = fila_seleccionada(tabla)
        if not fila:
            estado.mostrar("Selecciona un cliente de la tabla.", "advertencia")
            return
        if not confirmar("Eliminar cliente",
                         f"¿Eliminar al cliente '{fila[1]}' permanentemente?\n"
                         f"Se eliminarán también sus datos de acceso."):
            return

        # FASE 8: pre-validación de FK
        try:
            from dao.cliente_dao import ClienteDAO
            if ClienteDAO().tiene_ventas(fila[0]):
                msg_error(
                    "No se puede eliminar",
                    f"El cliente '{fila[1]}' tiene ventas registradas.\n"
                    "No es posible eliminarlo para preservar el historial de ventas."
                )
                return
        except Exception as e:
            msg_error("Error", f"No se pudo verificar dependencias: {e}")
            return

        try:
            _CTRL.eliminar(fila[0])
            exito("Eliminado", f"Cliente '{fila[1]}' eliminado correctamente.")
            _limpiar_form()
            _recargar_tabla()
        except Exception as e:
            msg_error("Error", str(e))

    def _cargar_en_form(event=None):
        fila = fila_seleccionada(tabla)
        if not fila:
            return
        limpiar_campos(entry_id, entry_nombre, entry_telefono, entry_dir)
        lbl_pwd_generada.configure(text="")
        entry_id.insert(0, str(fila[0]))
        entry_nombre.insert(0, str(fila[1]))
        entry_telefono.insert(0, str(fila[2]))
        entry_dir.insert(0, str(fila[3]))
        estado.mostrar(f"Datos del cliente ID {fila[0]} cargados.", "info")

    fila_btns = ctk.CTkFrame(form_body, fg_color="transparent")
    fila_btns.pack(fill="x", pady=(12, 0))
    btn_exito(fila_btns,     "💾 Registrar", _registrar, ancho=130, alto=36).pack(side="left", padx=(0, 8))
    btn_peligro(fila_btns,   "🗑 Eliminar",  _eliminar,  ancho=130, alto=36).pack(side="left", padx=(0, 8))
    btn_secundario(fila_btns, "✕ Limpiar",   _limpiar_form, ancho=100, alto=36).pack(side="left")

    entry_buscar.bind("<KeyRelease>", lambda e: _recargar_tabla(entry_buscar.get()))
    tabla.bind("<Double-1>", _cargar_en_form)

    _recargar_tabla()
