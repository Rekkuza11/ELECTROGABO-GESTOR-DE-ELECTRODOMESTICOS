class Sistema:

    def __init__(self):

        self.usuarios = []
        self.usuario_actual = None

    def agregar_usuario(self, usuario):

        self.usuarios.append(usuario)

    def mostrar_usuarios(self):

        for usuario in self.usuarios:
            usuario.mostrar()

    def login(self, id_usuario, password):

        for usuario in self.usuarios:

            if usuario.id_usuario == id_usuario and usuario.password == password:

                self.usuario_actual = usuario
                print("Acceso concedido")
                return True

        print("Credenciales incorrectas")
        return False

    def logout(self):

        self.usuario_actual = None
        print("Sesión cerrada")