from models.venta import Venta
class GestorVentas:

    def __init__(self):
        self.ventas = []

    def crear_venta(self, id_cliente, id_empleado, id_venta = None):

        venta = Venta(id_cliente, id_empleado, id_venta)
        self.ventas.append(venta)

        print("Venta creada")

    def agregar_producto_a_venta(self, id_venta, producto, cantidad):

        venta = self.buscar_venta(id_venta)

        if venta:
            venta.agregar_producto(producto, cantidad)
        else:
            print("Venta no encontrada")

    def buscar_venta(self, id_venta):

        for venta in self.ventas:
            if venta.id_venta == id_venta:
                return venta

        return None

    def mostrar_ventas(self):

        for venta in self.ventas:
            venta.mostrar_venta()

    def eliminar_venta(self, id_venta):

        for i, venta in enumerate(self.ventas):
            if venta.id_venta == id_venta:

                self.ventas.pop(i)  
                print("Venta eliminada completamente")
                return

        print("Venta no encontrada")
