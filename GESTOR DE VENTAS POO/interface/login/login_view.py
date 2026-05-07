import customtkinter as ctk


class LoginView(ctk.CTkFrame):

    def __init__(self, master, app):
        super().__init__(master)

        self.app = app

        # ========= TITULO =========

        self.label = ctk.CTkLabel(
            self,
            text="Iniciar Sesión",
            font=("Arial", 24)
        )
        self.label.pack(pady=20)

        # ========= USUARIO =========

        self.entry_user = ctk.CTkEntry(
            self,
            placeholder_text="Usuario",
            width=250
        )
        self.entry_user.pack(pady=10)

        # ========= PASSWORD =========

        self.entry_pass = ctk.CTkEntry(
            self,
            placeholder_text="Contraseña",
            show="*",
            width=250
        )
        self.entry_pass.pack(pady=10)

        # ========= MENSAJE ERROR =========

        self.label_error = ctk.CTkLabel(
            self,
            text="",
            text_color="red"
        )
        self.label_error.pack(pady=5)

        # ========= BOTON =========

        self.btn_login = ctk.CTkButton(
            self,
            text="Ingresar",
            command=self.login,
            width=200
        )
        self.btn_login.pack(pady=20)

    def login(self):

        usuario = self.entry_user.get()
        password = self.entry_pass.get()

        # ===== VALIDACION BASICA =====

        if usuario == "" or password == "":
            self.label_error.configure(
                text="Complete todos los campos"
            )
            return

        # ===== PRUEBA TEMPORAL =====

        if usuario == "admin" and password == "1234":

            self.label_error.configure(
                text="Login correcto",
                text_color="green"
            )

            print("Bienvenido")

            # Aquí luego iría:
            # self.app.mostrar_menu()

        else:

            self.label_error.configure(
                text="Usuario o contraseña incorrectos",
                text_color="red"
            )