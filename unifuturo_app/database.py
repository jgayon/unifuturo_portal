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


def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            # Si params es None, usar un diccionario vacío para execute, que es lo que espera cx_Oracle
            cursor.execute(query, params if params is not None else {}) 
            
            if commit:
                conn.commit()
                return True
            
            if fetchone:
                row = cursor.fetchone()
                if row is None:
                    return None
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))

            elif fetchall:
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return None 
    except cx_Oracle.Error as e:
        import traceback
        traceback.print_exc()
        error_obj, = e.args
        print(f"Error al ejecutar la consulta: {error_obj.message} - Query: {query}")

if __name__ == '__main__':
    conn = get_db_connection()
    if conn:
        print("Conexión a la base de datos exitosa.")
        conn.close()
    else:
        print("Fallo la conexión a la base de datos.")