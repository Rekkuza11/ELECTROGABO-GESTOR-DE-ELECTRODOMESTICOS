class Producto:

    def __init__(self, nombre, marca, precio_compra, precio_venta, stock, id_producto = None):

        self.id_producto = id_producto
        self.nombre = nombre
        self.marca = marca
        self.precio_compra = precio_compra
        self.precio_venta = precio_venta
        self.stock = stock

    def actualizar_precio_venta(self, nuevo_precio):
        self.precio_venta = nuevo_precio

    def aumentar_stock(self, cantidad):
        self.stock += cantidad

    def reducir_stock(self, cantidad):

        if cantidad <= self.stock:
            self.stock -= cantidad
        else:
            print("Stock insuficiente")

    def mostrar_producto(self):
        print(self.id_producto, self.nombre, self.precio_venta, self.stock)