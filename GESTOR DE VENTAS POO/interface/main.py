"""
Punto de entrada de la interfaz gráfica.
Responsabilidad: inicializar la ventana principal y cargar el LoginView.
"""

import customtkinter as ctk
from interface.login.login_view import LoginView


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("ElectroGestión")
        self.geometry("900x600")
        self.resizable(False, False)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Fondo azul igual al LoginView para no ver bordes
        self.configure(fg_color="#2563eb")

        self._cargar_login()

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def _cargar_login(self):
        for widget in self.winfo_children():
            widget.destroy()
        login = LoginView(master=self, app=self)
        login.pack(fill="both", expand=True)

    def mostrar_login(self):
        """Vuelve al login tras cerrar sesión."""
        self.deiconify()
        self.geometry("900x600")
        self.resizable(False, False)
        self._cargar_login()