class DetalleVenta:

    def __init__(self, producto, cantidad, id_detalle = None):
        id_detalle = id_detalle
        self.producto = producto
        self.cantidad = cantidad
        self.precio_unitario = producto.precio_venta
        self.subtotal = self.precio_unitario * cantidad

    def calcular_ganancia(self):

        return (self.producto.precio_venta - self.producto.precio_compra) * self.cantidad

    def mostrar_detalle(self):

        print(self.producto.nombre, self.cantidad, self.subtotal)