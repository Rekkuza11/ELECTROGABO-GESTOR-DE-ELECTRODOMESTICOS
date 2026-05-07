import customtkinter as ctk
from interface.login.login_view import LoginView


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("ElectroGabo")
        self.geometry("1000x600")

        # Tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Cargar login
        self.login_view = LoginView(
            master=self,
            app=self
        )

        self.login_view.pack(
            fill="both",
            expand=True
        )