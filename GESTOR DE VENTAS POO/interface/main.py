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
        self.frame_actual = None
        self.mostrar_login()

    def limpiar_frame(self):
        if self.frame_actual:
            self.frame_actual.destroy()

    def mostrar_login(self):
        self.limpiar_frame()

        self.frame_actual = LoginView(
            master=self,
            app=self
        )

        self.frame_actual.pack(
            fill="both",
            expand=True
        )

    def mostrar_menu(self):
        pass