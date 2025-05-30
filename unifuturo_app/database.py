from dotenv import load_dotenv
load_dotenv()
import oracledb as cx_Oracle
from config import Config


def get_db_connection():
    try:
        dsn_tns = cx_Oracle.makedsn(Config.ORACLE_DB_HOST, Config.ORACLE_DB_PORT, service_name=Config.ORACLE_DB_SERVICE_NAME)
        connection = cx_Oracle.connect(
            user=Config.ORACLE_DB_USER,
            password=Config.ORACLE_DB_PASSWORD,
            dsn=dsn_tns
        )
        return connection
    except cx_Oracle.Error as e:
        error_obj, = e.args
        print(f"Error al conectar a la base de datos: {error_obj.message}")
        return None
    
    print("Intentando conectar con:")
    print("Usuario:", Config.ORACLE_DB_USER)
    print("Contraseña:", Config.ORACLE_DB_PASSWORD)
    print("DSN:", cx_Oracle.makedsn(Config.ORACLE_DB_HOST, Config.ORACLE_DB_PORT, service_name=Config.ORACLE_DB_SERVICE_NAME))


def execute_query(query, params=None, fetchone=False, fetchall=False):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or {})

        if fetchone:
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))
            return None

        if fetchall:
            rows = cursor.fetchall()
            if rows:
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

        # Solo se hace commit si NO es fetchone ni fetchall
        conn.commit()
        return True

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Error al ejecutar la consulta: {error.message}\nHelp: {error.context}\n - Query: {query}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



if __name__ == '__main__':
    conn = get_db_connection()
    if conn:
        print("Conexión a la base de datos exitosa.")
        conn.close()
    else:
        print("Fallo la conexión a la base de datos.")