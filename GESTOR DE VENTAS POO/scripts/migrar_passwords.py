"""
scripts/migrar_passwords.py
───────────────────────────────────────────────────────────────────────────────
Script de migración — Fase 2, Corrección #6.

Propósito:
    Hashear todas las contraseñas que actualmente se encuentran en texto
    plano dentro de la tabla `usuario`.  Solo afecta los registros cuyo
    password_hash NO sea ya un hash SHA-256 válido (64 caracteres hex).

Uso:
    Ejecutar UNA SOLA VEZ desde la raíz del proyecto:

        python scripts/migrar_passwords.py

    El script imprime un resumen de cuántos registros fueron actualizados
    y cuántos ya estaban hasheados.  Es seguro re-ejecutarlo: si detecta
    que un password ya es un hash, lo omite.

ADVERTENCIA:
    Después de ejecutar este script, la función verificar() de UTIL/security.py
    es la única forma válida de autenticar usuarios.  La comparación directa
    de texto plano dejará de funcionar (eso es exactamente lo deseado).
"""

import sys
import os

# Aseguramos que la raíz del proyecto esté en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseConnection
from UTIL.security import hashear, es_hash
from exceptions import ConexionBaseDatosError


def migrar_passwords() -> None:
    print("=" * 60)
    print("  MIGRACIÓN DE CONTRASEÑAS — ElectroGabo Fase 2")
    print("=" * 60)

    try:
        db = DatabaseConnection()
        conexion = db.obtener_conexion()
    except ConexionBaseDatosError as e:
        print(f"\n  ✗ No se pudo conectar a la base de datos: {e}")
        sys.exit(1)

    cursor = conexion.cursor()

    # Leer todos los usuarios con sus contraseñas actuales
    cursor.execute("SELECT id_usuario, password_hash FROM usuario")
    usuarios = cursor.fetchall()

    total      = len(usuarios)
    migrados   = 0
    ya_hasheados = 0
    errores    = 0

    print(f"\n  Usuarios encontrados: {total}\n")

    for id_usuario, pwd_actual in usuarios:
        if es_hash(pwd_actual):
            # Ya está hasheado — no tocar
            print(f"  [OK]  {id_usuario}  — ya hasheado, omitido.")
            ya_hasheados += 1
            continue

        # Texto plano detectado — hashear y actualizar
        try:
            nuevo_hash = hashear(pwd_actual)
            cursor.execute(
                "UPDATE usuario SET password_hash = %s WHERE id_usuario = %s",
                (nuevo_hash, id_usuario),
            )
            print(f"  [✓]   {id_usuario}  — contraseña migrada.")
            migrados += 1
        except Exception as e:
            print(f"  [✗]   {id_usuario}  — ERROR: {e}")
            errores += 1

    if errores == 0:
        conexion.commit()
        print(f"\n  Commit realizado correctamente.")
    else:
        conexion.rollback()
        print(f"\n  ✗ Se encontraron errores. Se realizó rollback. "
              "Corrígelos y vuelve a ejecutar el script.")

    cursor.close()

    print("\n" + "=" * 60)
    print(f"  Total usuarios   : {total}")
    print(f"  Migrados         : {migrados}")
    print(f"  Ya hasheados     : {ya_hasheados}")
    print(f"  Errores          : {errores}")
    print("=" * 60 + "\n")

    if errores > 0:
        sys.exit(1)


if __name__ == "__main__":
    migrar_passwords()
