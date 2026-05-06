from models.usuario import Usuario
class Empleado(Usuario):

    def __init__(self, nombre, rol, password, id_empleado = None):

        super().__init__(id_empleado, password)

        self.nombre = nombre
        self.rol = rol

    def mostrar(self):
        print("Empleado:", self.id_usuario, self.nombre, self.rol)