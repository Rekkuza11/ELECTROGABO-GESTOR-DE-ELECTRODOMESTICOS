"""
Dashboard Cliente.
Responsabilidad: ventana principal del panel del cliente.
- Menú lateral de navegación.
- Frame de contenido intercambiable.
- Vistas: Inicio, Catálogo, Historial de compras, Cambiar contraseña.

CORRECCIÓN NE-PWD — Cambio de contraseña siempre fallaba:
    _vista_cambiar_password() comparaba la contraseña actual ingresada
    directamente contra fila[1] (el hash almacenado en BD):
        if not fila or fila[1] != actual:
    Desde la Fase 2 (corrección #6) las contraseñas se guardan como
    HMAC-SHA256, por lo que esa comparación siempre devuelve True
    (texto plano != hash) y el sistema reporta "contraseña incorrecta"
    aunque el usuario haya ingresado la clave correcta.

    Solución: usar UTIL.security.verificar(actual, fila[1]) exactamente
    igual que AuthController.login() verifica las credenciales al entrar.
"""

import customtkinter as ctk

from interface.components.botones import btn_menu
from interface.components.mensajes import alerta_inline
from interface.components.cards import (
    cabecera_vista,
    tarjeta_stat,
    fila_tarjetas,
    seccion_titulo,
    panel_blanco,
)
from UTIL.helpers import formatear_moneda


# ── Paleta y constantes ───────────────────────────────────────────────────────

_COLOR_SIDEBAR   = "white"
_COLOR_CONTENIDO = "#f1f5f9"
_COLOR_PRIMARIO  = "#2563eb"
_ANCHO_SIDEBAR   = 220


# ── Punto de entrada ──────────────────────────────────────────────────────────

def abrir_dashboard_cliente(app, id_usuario: str) -> None:
    app.withdraw()
    ventana = _VentanaDashboardCliente(app, id_usuario)
    ventana.mainloop()


# ── Ventana principal ─────────────────────────────────────────────────────────

class _VentanaDashboardCliente(ctk.CTkToplevel):

    def __init__(self, app, id_usuario: str):
        super().__init__()
        self._app        = app
        self._id_usuario = id_usuario

        self.title("ElectroGestión — Mi Portal")
        self.geometry("1200x700")
        self.minsize(900, 600)
        self.configure(fg_color=_COLOR_CONTENIDO)

        self.protocol("WM_DELETE_WINDOW", self._cerrar)

        self._construir_layout()
        self._mostrar_inicio()

    def _construir_layout(self):
        self._sidebar = ctk.CTkFrame(
            self, fg_color=_COLOR_SIDEBAR,
            width=_ANCHO_SIDEBAR, corner_radius=0,
        )
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        self._construir_sidebar()

        self._contenido = ctk.CTkFrame(self, fg_color=_COLOR_CONTENIDO)
        self._contenido.pack(side="left", fill="both", expand=True)

    def _construir_sidebar(self):
        sb = self._sidebar

        ctk.CTkLabel(
            sb, text="⚡ ElectroGestión",
            font=("Arial", 15, "bold"),
            text_color=_COLOR_PRIMARIO,
        ).pack(pady=(24, 2), padx=16, anchor="w")

        ctk.CTkLabel(
            sb, text="Mi Portal",
            font=("Arial", 11),
            text_color="gray",
        ).pack(padx=16, anchor="w")

        ctk.CTkFrame(sb, height=1, fg_color="#e2e8f0").pack(fill="x", pady=12)

        perfil = ctk.CTkFrame(sb, fg_color="#f1f5f9", corner_radius=8)
        perfil.pack(fill="x", padx=10, pady=(0, 4))

        ctk.CTkLabel(
            perfil, text="👤 Cliente",
            font=("Arial", 12, "bold"), text_color="#1e293b",
        ).pack(anchor="w", padx=10, pady=(8, 0))

        ctk.CTkLabel(
            perfil, text=f"ID: {self._id_usuario}",
            font=("Arial", 10), text_color="gray",
        ).pack(anchor="w", padx=10, pady=(0, 8))

        ctk.CTkFrame(sb, height=1, fg_color="#e2e8f0").pack(fill="x", pady=10)

        self._botones_nav: dict[str, ctk.CTkButton] = {}

        nav = [
            ("🏠  Inicio",         self._mostrar_inicio),
            ("🛍  Catálogo",       self._mostrar_catalogo),
            ("📋  Mis Compras",    self._mostrar_historial),
            ("🔑  Cambiar Clave",  self._mostrar_cambiar_password),
        ]

        for texto, comando in nav:
            btn = btn_menu(sb, texto, comando, activo=False)
            btn.pack(pady=2, padx=10)
            self._botones_nav[texto] = btn

        ctk.CTkFrame(sb, height=1, fg_color="#e2e8f0").pack(fill="x", pady=10)

        ctk.CTkButton(
            sb, text="🔒  Cerrar Sesión",
            width=180, height=40,
            fg_color="transparent", text_color="#dc2626",
            hover_color="#fee2e2", anchor="w",
            font=("Arial", 12),
            command=self._cerrar_sesion,
        ).pack(padx=10, pady=(0, 16), side="bottom")

    def _activar_nav(self, texto_boton: str):
        for txt, btn in self._botones_nav.items():
            activo = txt == texto_boton
            btn.configure(
                fg_color="#dbeafe" if activo else "transparent",
                text_color=_COLOR_PRIMARIO if activo else "#1e293b",
                font=("Arial", 12, "bold" if activo else "normal"),
            )

    def _limpiar_contenido(self):
        for w in self._contenido.winfo_children():
            w.destroy()

    def _mostrar_inicio(self):
        self._activar_nav("🏠  Inicio")
        self._limpiar_contenido()
        _vista_inicio_cliente(self._contenido, self._id_usuario)

    def _mostrar_catalogo(self):
        self._activar_nav("🛍  Catálogo")
        self._limpiar_contenido()
        from interface.cliente.catalogo_view import abrir_catalogo
        abrir_catalogo(self._contenido)

    def _mostrar_historial(self):
        self._activar_nav("📋  Mis Compras")
        self._limpiar_contenido()
        from interface.cliente.historial_view import abrir_historial
        abrir_historial(self._contenido, self._id_usuario)

    def _mostrar_cambiar_password(self):
        self._activar_nav("🔑  Cambiar Clave")
        self._limpiar_contenido()
        _vista_cambiar_password(self._contenido, self._id_usuario)

    def _cerrar_sesion(self):
        self.destroy()
        self._app.mostrar_login()

    def _cerrar(self):
        self.destroy()
        self._app.mostrar_login()


# ── Vista de Inicio del Cliente ───────────────────────────────────────────────

def _vista_inicio_cliente(parent: ctk.CTkFrame, id_usuario: str) -> None:
    cabecera_vista(
        parent,
        "¡Bienvenido a ElectroGestión!",
        f"Hola, cliente {id_usuario} — aquí puedes ver tu resumen de actividad",
    )

    try:
        from reports.reporte_clientes import ReporteClientes
        rc = ReporteClientes()
        historial = rc.obtener_historial_cliente(id_usuario)
        total_compras = len(historial)
        monto_total   = sum(float(row[2]) for row in historial) if historial else 0.0
        segmento      = ReporteClientes.clasificar_cliente(monto_total)
    except Exception:
        total_compras = 0
        monto_total   = 0.0
        segmento      = "NUEVO"
        historial     = []

    fila1 = fila_tarjetas(parent)

    tarjeta_stat(fila1, "🛒", "#2563eb", str(total_compras),
                 "Mis Compras", "Total de pedidos")
    tarjeta_stat(fila1, "$", "#22c55e", formatear_moneda(monto_total),
                 "Total Gastado", "Historial acumulado")
    tarjeta_stat(fila1, "⭐", "#f97316", segmento,
                 "Mi Segmento", "Nivel de cliente", padx=(0, 0))

    scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    seccion_titulo(scroll, "🕐 Últimas Compras")

    panel = panel_blanco(scroll, pady=(0, 12))

    if not historial:
        alerta_inline(panel, "Aún no tienes compras registradas.", tipo="info")
    else:
        for id_v, fecha, total, empleado in historial[:5]:
            fila = ctk.CTkFrame(panel, fg_color="#f8fafc", corner_radius=8)
            fila.pack(fill="x", padx=15, pady=(4, 0))

            ctk.CTkLabel(
                fila,
                text=f"🧾 Venta #{id_v}  —  {str(fecha)[:16]}",
                font=("Arial", 12, "bold"), text_color="#1e293b", anchor="w",
            ).pack(side="left", padx=12, pady=8)

            ctk.CTkLabel(
                fila,
                text=formatear_moneda(float(total)),
                font=("Arial", 12, "bold"), text_color="#2563eb",
            ).pack(side="right", padx=12)

    ctk.CTkLabel(panel, text="", fg_color="transparent").pack(pady=4)


# ── Vista: Cambiar Contraseña ─────────────────────────────────────────────────

def _vista_cambiar_password(parent: ctk.CTkFrame, id_usuario: str) -> None:
    """
    Permite al cliente cambiar su contraseña.

    CORRECCIÓN NE-PWD:
        La versión anterior comparaba fila[1] (hash almacenado) contra la
        contraseña ingresada en texto plano, lo que siempre fallaba después
        de la migración a HMAC-SHA256 (Fase 2, corrección #6).
        Ahora usa UTIL.security.verificar() igual que AuthController.login().
    """
    from interface.components.formularios import campo_password, panel_formulario
    from interface.components.mensajes import LabelEstado
    from interface.components.botones import btn_exito
    from UTIL.security import verificar   # ← CORRECCIÓN NE-PWD

    cabecera_vista(
        parent,
        "🔑 Cambiar Contraseña",
        "Actualiza tu clave de acceso al sistema",
    )

    contenedor = ctk.CTkFrame(parent, fg_color="transparent")
    contenedor.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    form_body = panel_formulario(contenedor, "🔐 Nueva Contraseña")

    entry_actual  = campo_password(form_body, "Contraseña actual:")
    entry_nueva   = campo_password(form_body, "Nueva contraseña:")
    entry_repetir = campo_password(form_body, "Repetir nueva:")

    estado = LabelEstado(form_body)

    def _cambiar():
        actual  = entry_actual.get().strip()
        nueva   = entry_nueva.get().strip()
        repetir = entry_repetir.get().strip()

        if not actual or not nueva or not repetir:
            estado.mostrar("Completa todos los campos.", "error")
            return
        if nueva != repetir:
            estado.mostrar("Las nuevas contraseñas no coinciden.", "error")
            return
        if len(nueva) < 4:
            estado.mostrar("La contraseña debe tener al menos 4 caracteres.", "error")
            return

        try:
            from dao.usuario_dao import UsuarioDAO
            dao  = UsuarioDAO()
            fila = dao.obtener_por_id(id_usuario)

            if not fila:
                estado.mostrar("Usuario no encontrado.", "error")
                return

            # CORRECCIÓN NE-PWD: verificar con hash, no comparación directa.
            # fila[1] es el password_hash almacenado (HMAC-SHA256 desde Fase 2).
            # Antes: fila[1] != actual  → siempre True (hash != texto plano)
            # Ahora: verificar(actual, fila[1]) → compara correctamente
            if not verificar(actual, fila[1]):
                estado.mostrar("La contraseña actual es incorrecta.", "error")
                return

            dao.actualizar_password(id_usuario, nueva)
            estado.mostrar("Contraseña actualizada correctamente.", "exito")
            for e in (entry_actual, entry_nueva, entry_repetir):
                e.delete(0, "end")

        except Exception as e:
            estado.mostrar(f"Error: {e}", "error")

    btn_exito(form_body, "💾 Guardar Cambios", _cambiar, ancho=200, alto=38).pack(
        anchor="w", pady=(12, 0)
    )
