"""
Ejecutar desde: C:/MiProyecto/GESTOR DE VENTAS POO/
    python diagnostico.py
"""
import sys, traceback

print("=" * 55)

# 1. Conexión
print("[1] Conexion a MySQL...")
try:
    from database import DatabaseConnection
    conn = DatabaseConnection().obtener_conexion()
    print("    OK")
except Exception as e:
    print(f"    FALLO: {e}")
    sys.exit(1)

# 2. SELECT directo
print("[2] SELECT * FROM producto...")
try:
    cur = conn.cursor()
    cur.execute("SELECT * FROM producto")
    filas = cur.fetchall()
    cur.close()
    print(f"    Filas encontradas: {len(filas)}")
    for f in filas:
        print(f"    {f}")
except Exception as e:
    print(f"    FALLO: {e}")

# 3. ProductoDAO
print("[3] ProductoDAO.obtener_todos()...")
try:
    from dao.producto_dao import ProductoDAO
    prods = ProductoDAO().obtener_todos()
    print(f"    Productos: {len(prods)}")
    for p in prods:
        print(f"    {p}")
except Exception as e:
    print(f"    FALLO: {type(e).__name__}: {e}")
    traceback.print_exc()

# 4. Import de gestionar_productos
print("[4] Import gestionar_productos...")
try:
    from interface.admin.gestionar_productos import abrir_gestionar_productos
    print("    OK")
except Exception as e:
    print(f"    FALLO: {type(e).__name__}: {e}")
    traceback.print_exc()

# 5. Columnas de venta
print("[5] Columnas tabla venta...")
try:
    cur = conn.cursor()
    cur.execute("DESCRIBE venta")
    cols = [r[0] for r in cur.fetchall()]
    cur.close()
    print(f"    {cols}")
except Exception as e:
    print(f"    FALLO: {e}")

print("=" * 55)
input("Presiona Enter para cerrar...")