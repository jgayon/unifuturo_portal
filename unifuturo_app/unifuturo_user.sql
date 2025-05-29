-- 0. Conéctate como SYSDBA y ejecuta esto:

sqlplus / as sysdba
--    @setup_unifuturo.sql

-- 1. Cambiar al contenedor pluggable database (PDB)
ALTER SESSION SET CONTAINER = XEPDB1;

-- 2. Eliminar el usuario si ya existe (opcional, cuidado en producción)
BEGIN
   EXECUTE IMMEDIATE 'DROP USER UNIFUTURO_USER CASCADE';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -01918 THEN -- usuario no existe
         RAISE;
      END IF;
END;
/

-- 3. Crear el usuario y darle permisos
CREATE USER UNIFUTURO_USER IDENTIFIED BY unifuturo2025
DEFAULT TABLESPACE users
QUOTA UNLIMITED ON users;

GRANT CONNECT, RESOURCE TO UNIFUTURO_USER;

-- 4. Conectarse como el nuevo usuario automáticamente
-- NOTA: esto no funciona dentro del script, hay que reconectar manualmente:
-- sqlplus UNIFUTURO_USER/unifuturo2025@localhost:1521/XEPDB1

-- Desde aquí deberás reconectar como UNIFUTURO_USER y luego ejecutar el script de tablas.
