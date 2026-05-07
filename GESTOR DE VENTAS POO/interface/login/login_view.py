"""
Vista: Login.
Responsabilidad: autenticar al usuario contra la BD y redirigir
al dashboard correspondiente según su tipo (admin, empleado, cliente).
Usa AuthController para la lógica de autenticación.
"""

import customtkinter as ctk
from interface.controllers.auth_controller import AuthController
from exceptions import CredencialesInvalidasError, BaseDatosError


class LoginView(ctk.CTkFrame):

    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._auth = AuthController()
        self._construir_ui()

    # ── Construcción de la interfaz ───────────────────────────────────────────

    def _construir_ui(self):
        # Contenedor centrado
        card = ctk.CTkFrame(self, fg_color="white", corner_radius=16, width=420)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        # Logo / título
        ctk.CTkLabel(
            card,
            text="⚡ ElectroGestión",
            font=("Arial", 26, "bold"),
            text_color="#2563eb",
        ).pack(pady=(40, 4))

        ctk.CTkLabel(
            card,
            text="Sistema de Gestión de Ventas",
            font=("Arial", 12),
            text_color="gray",
        ).pack(pady=(0, 30))

        # Separador
        ctk.CTkFrame(card, height=1, fg_color="#e2e8f0").pack(fill="x", padx=30)

        # Campos
        ctk.CTkLabel(
            card, text="Usuario",
            font=("Arial", 12, "bold"), text_color="#475569",
        ).pack(anchor="w", padx=40, pady=(20, 4))

        self.entry_user = ctk.CTkEntry(
            card,
            placeholder_text="Ingresa tu usuario",
            width=340, height=42,
            font=("Arial", 13),
            border_color="#cbd5e1",
        )
        self.entry_user.pack(padx=40)

        ctk.CTkLabel(
            card, text="Contraseña",
            font=("Arial", 12, "bold"), text_color="#475569",
        ).pack(anchor="w", padx=40, pady=(14, 4))

        self.entry_pass = ctk.CTkEntry(
            card,
            placeholder_text="Ingresa tu contraseña",
            show="*",
            width=340, height=42,
            font=("Arial", 13),
            border_color="#cbd5e1",
        )
        self.entry_pass.pack(padx=40)
        self.entry_pass.bind("<Return>", lambda e: self._login())

        # Mensaje de estado
        self.lbl_error = ctk.CTkLabel(
            card, text="",
            font=("Arial", 11),
            text_color="#dc2626",
        )
        self.lbl_error.pack(pady=(10, 0))

        # Botón ingresar
        ctk.CTkButton(
            card,
            text="Ingresar",
            command=self._login,
            width=340, height=44,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            font=("Arial", 13, "bold"),
            corner_radius=8,
        ).pack(padx=40, pady=(10, 40))

    # ── Lógica de login ───────────────────────────────────────────────────────

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
        """Redirige al dashboard según el tipo de usuario."""
        tipo = sesion.get("tipo")
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