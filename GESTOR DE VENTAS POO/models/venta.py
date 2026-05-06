class Venta:

    def __init__(self, id_venta, id_cliente, id_empleado):

        self.id_venta = id_venta
        self.id_cliente = id_cliente
        self.id_empleado = id_empleado
        self.detalles = []

    def agregar_producto(self, producto, cantidad):

        if producto.stock >= cantidad:

            
            producto.reducir_stock(cantidad)

        else:
            print("Stock insuficiente")

    def calcular_total(self, descuento):

        total = 0
        for detalle in self.detalles:
            total += detalle.subtotal

        return total*descuento

    def calcular_ganancia(self):

        ganancia = 0
        for detalle in self.detalles:
            ganancia += detalle.calcular_ganancia()

        return ganancia

    def mostrar_venta(self):

        print("Venta:", self.id_venta)
        print("Cliente:", self.id_cliente)
        print("Empleado:", self.id_empleado)

        for detalle in self.detalles:
            detalle.mostrar_detalle()

        print("Total:", self.calcular_total(0.80))