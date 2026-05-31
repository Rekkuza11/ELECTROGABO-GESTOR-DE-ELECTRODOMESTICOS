-- ============================================================
-- FASE 3 — Fix #1: FK admin <-> empleado rompe ventas
-- ============================================================
-- Problema:
--   venta.id_empleado referencia a empleado.id_empleado.
--   Los administradores solo existen en la tabla usuario (tipo='admin'),
--   NO tienen fila en empleado, por lo que el motor rechaza cualquier
--   venta registrada por un admin con error de FK constraint.
--
-- Solución:
--   Redirigir la FK para que apunte a usuario.id_usuario.
--   Todos los actores del sistema (admin, empleado, cliente) tienen
--   siempre una fila en usuario, lo que satisface la restricción.
--
-- Aplicar una sola vez en la base de datos de producción / desarrollo.
-- ============================================================

USE base_datos_electrogabo;

-- Paso 1: Eliminar la FK actual que apunta a empleado
ALTER TABLE venta
    DROP FOREIGN KEY venta_ibfk_2;

-- Paso 2: Crear la nueva FK apuntando a usuario
ALTER TABLE venta
    ADD CONSTRAINT venta_ibfk_2
        FOREIGN KEY (id_empleado) REFERENCES usuario (id_usuario);

-- Verificación: debe mostrar REFERENCES usuario(id_usuario)
-- SHOW CREATE TABLE venta;
