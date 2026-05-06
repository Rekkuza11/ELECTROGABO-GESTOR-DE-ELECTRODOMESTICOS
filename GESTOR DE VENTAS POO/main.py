if __name__ == "__main__":
    from models.producto import Producto 
    from dao.producto_dao import ProductoDAO
    
    dao = ProductoDAO()

    nuevo = Producto("Multímetro Digital", "Fluke", 45.50, 85.00, 10)
    dao.insertar(nuevo)
    print(f"Producto insertado con ID: {nuevo.id_producto}")

   
    print("\nInventario actual:")
    productos = dao.obtener_todos()
    for p in productos:
        print(p) 

   
    if nuevo.id_producto:
        dao.actualizar_stock(nuevo.id_producto, 2)
        print(f"\nStock actualizado para el producto {nuevo.id_producto}")