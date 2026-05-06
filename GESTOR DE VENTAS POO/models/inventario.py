class Inventario:

    def __init__(self):
        self.productos = []

    def agregar_producto(self, producto):
        self.productos.append(producto)

    def buscar_producto(self, id_producto):

        for producto in self.productos:
            if producto.id_producto == id_producto:
                return producto

        return None

    def mostrar_catalogo(self):

        for producto in self.productos:
            producto.mostrar_producto()
