import os
from dotenv import load_dotenv


# Cargar las variables del archivo .env
load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'una_clave_secreta_para_unifuturo_basico')
    
    ORACLE_DB_USER = os.getenv('ORACLE_USER')
    ORACLE_DB_PASSWORD = os.getenv('ORACLE_PASSWORD')
    ORACLE_DB_HOST = os.getenv('ORACLE_HOST', 'localhost')
    ORACLE_DB_PORT = os.getenv('ORACLE_PORT', '1521')
    ORACLE_DB_SERVICE_NAME = os.getenv('ORACLE_SERVICE', 'XE')

    ADMIN_REGISTRATION_CODE = os.getenv('ADMIN_REGISTRATION_CODE', 'ADMIN123')
