from models.usuario import Usuario

class Cliente(Usuario):

    def __init__(self, nombre, telefono, direccion, password, id_cliente = None):

        super().__init__(id_cliente, password)

        self.nombre = nombre
        self.telefono = telefono
        self.direccion = direccion

    def mostrar(self):
        print("Cliente:", self.id_usuario, self.nombre, self.telefono, self.direccion)
