"""
Vista: Login.
Responsabilidad: autenticar al usuario contra la BD y redirigir
al dashboard correspondiente según su tipo (admin, empleado, cliente).
Diseño: fondo azul sólido, card blanca centrada con pack, ícono badge superior.
"""

import customtkinter as ctk
from interface.controllers.auth_controller import AuthController
from exceptions import CredencialesInvalidasError, BaseDatosError


# ── Paleta ────────────────────────────────────────────────────────────────────
_AZUL_FONDO   = "#2563eb"
_AZUL_BADGE   = "#dbeafe"
_AZUL_ICONO   = "#2563eb"
_AZUL_BTN     = "#3b82f6"
_AZUL_BTN_HOV = "#1d4ed8"
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

        # Fila que ocupa todo el alto para centrar verticalmente la card
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Card blanca
        card = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=18,
            width=420,
        )
        card.grid(row=0, column=0)
        card.grid_propagate(False)

        # ── Badge con ícono ───────────────────────────────────────────────────
        badge = ctk.CTkFrame(
            card,
            fg_color=_AZUL_BADGE,
            corner_radius=999,
            width=72, height=72,
        )
        badge.pack(pady=(36, 0))
        badge.pack_propagate(False)

        ctk.CTkLabel(
            badge,
            text="⚡",
            font=("Arial", 30),
            text_color=_AZUL_ICONO,
        ).pack(expand=True)

        # ── Título y subtítulo ────────────────────────────────────────────────
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
        ).pack(pady=(0, 20))

        # ── Campo Usuario ─────────────────────────────────────────────────────
        ctk.CTkLabel(
            card,
            text="Usuario",
            font=("Arial", 13, "bold"),
            text_color=_TEXTO_LABEL,
            anchor="w",
        ).pack(anchor="w", padx=40, pady=(0, 4))

        self.entry_user = ctk.CTkEntry(
            card,
            placeholder_text="Ingrese su usuario",
            width=340,
            height=44,
            font=("Arial", 13),
            border_color=_BORDE_INPUT,
            border_width=1,
            corner_radius=8,
            fg_color="white",
            text_color=_TEXTO_TITULO,
        )
        self.entry_user.pack(padx=40)

        # ── Campo Contraseña ──────────────────────────────────────────────────
        ctk.CTkLabel(
            card,
            text="Contraseña",
            font=("Arial", 13, "bold"),
            text_color=_TEXTO_LABEL,
            anchor="w",
        ).pack(anchor="w", padx=40, pady=(14, 4))

        self.entry_pass = ctk.CTkEntry(
            card,
            placeholder_text="Ingrese su contraseña",
            show="*",
            width=340,
            height=44,
            font=("Arial", 13),
            border_color=_BORDE_INPUT,
            border_width=1,
            corner_radius=8,
            fg_color="white",
            text_color=_TEXTO_TITULO,
        )
        self.entry_pass.pack(padx=40)
        self.entry_pass.bind("<Return>", lambda e: self._login())

        # ── Mensaje de error ──────────────────────────────────────────────────
        self.lbl_error = ctk.CTkLabel(
            card,
            text="",
            font=("Arial", 11),
            text_color="#dc2626",
        )
        self.lbl_error.pack(pady=(8, 0))

        # ── Botón Iniciar Sesión ──────────────────────────────────────────────
        ctk.CTkButton(
            card,
            text="Iniciar Sesión",
            command=self._login,
            width=340,
            height=46,
            fg_color=_AZUL_BTN,
            hover_color=_AZUL_BTN_HOV,
            text_color="white",
            font=("Arial", 14, "bold"),
            corner_radius=10,
        ).pack(padx=40, pady=(12, 40))

    # ── Lógica de autenticación ───────────────────────────────────────────────

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