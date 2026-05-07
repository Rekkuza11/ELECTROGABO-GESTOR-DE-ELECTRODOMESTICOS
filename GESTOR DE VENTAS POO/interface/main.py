"""
Punto de entrada de la interfaz gráfica.
Responsabilidad: inicializar la ventana principal y cargar el LoginView.
"""

import customtkinter as ctk
from interface.login.login_view import LoginView


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("ElectroGabo")
        self.geometry("1000x620")
        self.resizable(False, False)

        # Tema claro — el dashboard usa colores propios
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Fondo del login
        self.configure(fg_color="#f1f5f9")

        self._cargar_login()

    # ── Métodos públicos ──────────────────────────────────────────────────────

    def _cargar_login(self):
        """Instancia y muestra el LoginView ocupando toda la ventana."""
        # Limpiar cualquier vista anterior
        for widget in self.winfo_children():
            widget.destroy()

        login = LoginView(master=self, app=self)
        login.pack(fill="both", expand=True)

    def mostrar_login(self):
        """Vuelve a mostrar el login (usado tras cerrar sesión)."""
        self.deiconify()
        self.geometry("1000x620")
        self.resizable(False, False)
        self._cargar_login()