"""
Vista: Login.
Responsabilidad: autenticar al usuario contra la BD y redirigir
al dashboard correspondiente según su tipo (admin, empleado, cliente).
Diseño: fondo azul sólido, card blanca centrada, ícono con badge superior.
"""

import customtkinter as ctk
from interface.controllers.auth_controller import AuthController
from exceptions import CredencialesInvalidasError, BaseDatosError


# ── Paleta ────────────────────────────────────────────────────────────────────
_AZUL_FONDO   = "#2563eb"
_AZUL_BADGE   = "#dbeafe"
_AZUL_ICONO   = "#2563eb"
_AZUL_BTN     = "#3b82f6"
_AZUL_BTN_HOV = "#2563eb"
_TEXTO_TITULO = "#1e293b"
_TEXTO_SUB    = "#64748b"
_TEXTO_LABEL  = "#374151"
_BORDE_INPUT  = "#d1d5db"


class LoginView(ctk.CTkFrame):

    def __init__(self, master, app):
        super().__init__(master, fg_color=_AZUL_FONDO)
        self.app   = app
        self._auth = AuthController()
        self._construir_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _construir_ui(self):
        # Card blanca centrada
        card = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=18,
            width=420,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        # ── Badge con ícono ───────────────────────────────────────────────────
        badge_outer = ctk.CTkFrame(
            card,
            fg_color=_AZUL_BADGE,
            corner_radius=999,
            width=72, height=72,
        )
        badge_outer.pack(pady=(36, 0))
        badge_outer.pack_propagate(False)

        ctk.CTkLabel(
            badge_outer,
            text="⚡",
            font=("Arial", 28),
            text_color=_AZUL_ICONO,
        ).place(relx=0.5, rely=0.5, anchor="center")

        # ── Títulos ───────────────────────────────────────────────────────────
        ctk.CTkLabel(
            card,
            text="ElectroGestión",
            font=("Arial", 26, "bold"),
            text_color=_TEXTO_TITULO,
        ).pack(pady=(14, 2))

        ctk.CTkLabel(
            card,
            text="Sistema de Gestión de Electrodomésticos",
            font=("Arial", 12),
            text_color=_TEXTO_SUB,
        ).pack(pady=(0, 24))

        # ── Campos ───────────────────────────────────────────────────────────
        _label(card, "Usuario")
        self.entry_user = _input(card, "Ingrese su usuario")

        _label(card, "Contraseña", pady_top=14)
        self.entry_pass = _input(card, "Ingrese su contraseña", oculto=True)
        self.entry_pass.bind("<Return>", lambda e: self._login())

        # ── Error ─────────────────────────────────────────────────────────────
        self.lbl_error = ctk.CTkLabel(
            card, text="",
            font=("Arial", 11),
            text_color="#dc2626",
        )
        self.lbl_error.pack(pady=(8, 0))

        # ── Botón ─────────────────────────────────────────────────────────────
        ctk.CTkButton(
            card,
            text="Iniciar Sesión",
            command=self._login,
            width=340, height=46,
            fg_color=_AZUL_BTN,
            hover_color=_AZUL_BTN_HOV,
            text_color="white",
            font=("Arial", 14, "bold"),
            corner_radius=10,
        ).pack(padx=40, pady=(12, 40))

    # ── Lógica ────────────────────────────────────────────────────────────────

    def _login(self):
        usuario  = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not usuario or not password:
            self._mostrar_error("Completa todos los campos.")
            return

        try:
            sesion = self._auth.login(usuario, password)
            self._navegar(sesion)
        except CredencialesInvalidasError:
            self._mostrar_error("Usuario o contraseña incorrectos.")
        except BaseDatosError as e:
            self._mostrar_error(f"Error de conexión: {e.mensaje}")
        except Exception as e:
            self._mostrar_error(f"Error inesperado: {e}")

    def _navegar(self, sesion: dict):
        tipo       = sesion.get("tipo")
        id_usuario = sesion.get("id")

        if tipo == "admin":
            from interface.admin.admin_dasboard import abrir_dashboard
            abrir_dashboard(self.app, id_usuario)

        elif tipo == "empleado":
            from interface.empleado.empleado_dashboard import abrir_dashboard_empleado
            abrir_dashboard_empleado(self.app, id_usuario)

        elif tipo == "cliente":
            from interface.cliente.cliente_dashboard import abrir_dashboard_cliente
            abrir_dashboard_cliente(self.app, id_usuario)

        else:
            self._mostrar_error(f"Tipo de usuario desconocido: '{tipo}'.")

    def _mostrar_error(self, mensaje: str):
        self.lbl_error.configure(text=mensaje, text_color="#dc2626")


# ── Helpers internos del login ────────────────────────────────────────────────

def _label(parent, texto: str, pady_top: int = 0) -> None:
    ctk.CTkLabel(
        parent,
        text=texto,
        font=("Arial", 13, "bold"),
        text_color=_TEXTO_LABEL,
        anchor="w",
    ).pack(anchor="w", padx=40, pady=(pady_top, 4))


def _input(parent, placeholder: str, oculto: bool = False) -> ctk.CTkEntry:
    entry = ctk.CTkEntry(
        parent,
        placeholder_text=placeholder,
        width=340, height=44,
        font=("Arial", 13),
        border_color=_BORDE_INPUT,
        border_width=1,
        corner_radius=8,
        show="*" if oculto else "",
        fg_color="white",
        text_color=_TEXTO_TITULO,
    )
    entry.pack(padx=40)
    return entry