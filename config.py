"""
CONFIGURACIÓN DEL SISTEMA - SISTEMA RECOMENDADOR DE HOTELES
==========================================================

Este archivo contiene todas las configuraciones del sistema, incluyendo:
- Configuración de base de datos
- Configuración de seguridad
- Configuración de Flask
- Variables de entorno
- Configuración de correo electrónico

El sistema utiliza variables de entorno para configuraciones sensibles
como contraseñas y claves de API.

AUTOR: Wilson Munoz Serrano
FECHA: 1 mes jajaja y mucho desvelo
VERSIÓN: 2.0
"""

import os
from datetime import timedelta

# =============================================================================
# CLASE DE CONFIGURACIÓN PRINCIPAL
# =============================================================================

class Config:
    """
    CLASE DE CONFIGURACIÓN PRINCIPAL
    
    Define todas las configuraciones del sistema Flask.
    Las configuraciones sensibles se obtienen de variables de entorno.
    """
    
    # ===== CONFIGURACIÓN DE SEGURIDAD =====
    
    # Clave secreta para sesiones y CSRF (obligatoria para Flask)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuración de sesiones
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # Duración de sesión
    SESSION_COOKIE_SECURE = False  # True en producción con HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevenir acceso desde JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax'  # Protección CSRF
    
    # ===== CONFIGURACIÓN DE BASE DE DATOS =====
    
    # Configuración de SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:KawasakiNinjaH2R@localhost:3306/sistema_recomendador_hoteles'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Desactivar para mejor rendimiento
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,  # Número de conexiones en el pool
        'pool_recycle': 3600,  # Reciclar conexiones cada hora
        'pool_pre_ping': True,  # Verificar conexiones antes de usar
    }
    
    # ===== CONFIGURACIÓN DE CORREO ELECTRÓNICO =====
    
    # Configuración de Flask-Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # ===== CONFIGURACIÓN DE FLASK-WTF =====
    
    # Configuración de CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hora para tokens CSRF
    
    # ===== CONFIGURACIÓN DE LOGGING =====
    
    # Configuración de logs
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'app.log'
    
    # ===== CONFIGURACIÓN DE SCRAPING =====
    
    # Límites de scraping
    SCRAPING_HOTEL_LIMIT = int(os.environ.get('SCRAPING_HOTEL_LIMIT') or 200)
    SCRAPING_DELAY_MIN = float(os.environ.get('SCRAPING_DELAY_MIN') or 1.0)
    SCRAPING_DELAY_MAX = float(os.environ.get('SCRAPING_DELAY_MAX') or 3.0)
    
    # URLs de scraping
    BOOKING_BASE_URL = 'https://www.booking.com'
    TRIVAGO_BASE_URL = 'https://www.trivago.com'
    
    # ===== CONFIGURACIÓN DE RECOMENDACIONES =====
    
    # Parámetros del sistema de recomendación
    RECOMMENDATION_ALGORITHM = os.environ.get('RECOMMENDATION_ALGORITHM') or 'collaborative'
    RECOMMENDATION_MAX_RESULTS = int(os.environ.get('RECOMMENDATION_MAX_RESULTS') or 20)
    RECOMMENDATION_MIN_SIMILARITY = float(os.environ.get('RECOMMENDATION_MIN_SIMILARITY') or 0.3)
    
    # ===== CONFIGURACIÓN DE CACHE =====
    
    # Configuración de caché (si se implementa)
    CACHE_TYPE = os.environ.get('CACHE_TYPE') or 'simple'
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT') or 300)
    
    # ===== CONFIGURACIÓN DE ARCHIVOS =====
    
    # Directorios de archivos
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH') or 16 * 1024 * 1024)  # 16MB
    
    # ===== CONFIGURACIÓN DE DESARROLLO =====
    
    # Configuración específica para desarrollo
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    TESTING = os.environ.get('FLASK_TESTING', 'false').lower() == 'true'
    
    # ===== CONFIGURACIÓN DE PRODUCCIÓN =====
    
    # Configuraciones específicas para producción
    PRODUCTION = os.environ.get('FLASK_ENV') == 'production'
    
    if PRODUCTION:
        # Configuraciones de seguridad para producción
        SESSION_COOKIE_SECURE = True
        SESSION_COOKIE_HTTPONLY = True
        SESSION_COOKIE_SAMESITE = 'Strict'
        
        # Configuración de base de datos para producción
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        
        # Configuración de logging para producción
        LOG_LEVEL = 'WARNING'
    
    # ===== CONFIGURACIÓN DE TESTING =====
    
    if TESTING:
        # Configuración específica para testing
        TESTING = True
        WTF_CSRF_ENABLED = False
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        SECRET_KEY = 'test-secret-key'

# =============================================================================
# CONFIGURACIONES ESPECÍFICAS POR ENTORNO
# =============================================================================

class DevelopmentConfig(Config):
    """
    CONFIGURACIÓN PARA DESARROLLO
    
    Configuraciones específicas para el entorno de desarrollo.
    Incluye debugging, logging detallado y configuraciones menos estrictas.
    """
    DEBUG = True
    TESTING = False
    
    # Configuración de base de datos para desarrollo
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql://root:password@localhost/sistema_recomendador_dev'
    
    # Logging detallado para desarrollo
    LOG_LEVEL = 'DEBUG'
    
    # Configuraciones menos estrictas para desarrollo
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = True

class ProductionConfig(Config):
    """
    CONFIGURACIÓN PARA PRODUCCIÓN
    
    Configuraciones específicas para el entorno de producción.
    Incluye configuraciones de seguridad estrictas y optimizaciones.
    """
    DEBUG = False
    TESTING = False
    
    # Configuración de base de datos para producción
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Configuraciones de seguridad estrictas
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Logging para producción
    LOG_LEVEL = 'WARNING'
    
    # Configuración de caché para producción
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')

class TestingConfig(Config):
    """
    CONFIGURACIÓN PARA TESTING
    
    Configuraciones específicas para ejecutar tests.
    Incluye base de datos en memoria y configuraciones simplificadas.
    """
    TESTING = True
    DEBUG = True
    
    # Base de datos en memoria para testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Desactivar CSRF para testing
    WTF_CSRF_ENABLED = False
    
    # Configuración de logging para testing
    LOG_LEVEL = 'ERROR'
    
    # Configuración de caché para testing
    CACHE_TYPE = 'simple'

# =============================================================================
# DICCIONARIO DE CONFIGURACIONES
# =============================================================================

# Mapeo de entornos a configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# =============================================================================
# FUNCIONES DE UTILIDAD PARA CONFIGURACIÓN
# =============================================================================

def get_config():
    """
    Obtiene la configuración apropiada basada en el entorno
    
    Returns:
        Clase de configuración correspondiente al entorno
    """
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])

def validate_config():
    """
    Valida que todas las configuraciones requeridas estén presentes
    
    Returns:
        True si la configuración es válida, False en caso contrario
    """
    required_vars = [
        'SECRET_KEY',
        'SQLALCHEMY_DATABASE_URI'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var) and var not in globals():
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Variables de entorno faltantes: {', '.join(missing_vars)}")
        return False
    
    return True

def print_config_summary():
    """
    Imprime un resumen de la configuración actual
    
    Útil para debugging y verificación de configuración
    """
    config_instance = get_config()
    
    print("=== RESUMEN DE CONFIGURACIÓN ===")
    print(f"Entorno: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Debug: {config_instance.DEBUG}")
    print(f"Testing: {config_instance.TESTING}")
    print(f"Base de datos: {config_instance.SQLALCHEMY_DATABASE_URI}")
    print(f"Log level: {config_instance.LOG_LEVEL}")
    print(f"CSRF habilitado: {config_instance.WTF_CSRF_ENABLED}")
    print("================================")

# =============================================================================
# CONFIGURACIÓN DE VARIABLES DE ENTORNO
# =============================================================================

# Variables de entorno requeridas y sus valores por defecto
ENVIRONMENT_VARIABLES = {
    # Base de datos
    'DATABASE_URL': 'mysql+pymysql://root:KawasakiNinjaH2R@localhost:3306/sistema_recomendador_hoteles',
    'DEV_DATABASE_URL': 'mysql://root:password@localhost/sistema_recomendador_dev',
    
    # Seguridad
    'SECRET_KEY': 'dev-secret-key-change-in-production',
    
    # Correo electrónico
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': '587',
    'MAIL_USE_TLS': 'true',
    'MAIL_USERNAME': '',
    'MAIL_PASSWORD': '',
    'MAIL_DEFAULT_SENDER': '',
    
    # Scraping
    'SCRAPING_HOTEL_LIMIT': '50',
    'SCRAPING_DELAY_MIN': '1.0',
    'SCRAPING_DELAY_MAX': '3.0',
    
    # Recomendaciones
    'RECOMMENDATION_ALGORITHM': 'collaborative',
    'RECOMMENDATION_MAX_RESULTS': '20',
    'RECOMMENDATION_MIN_SIMILARITY': '0.3',
    
    # Logging
    'LOG_LEVEL': 'INFO',
    'LOG_FILE': 'app.log',
    
    # Archivos
    'UPLOAD_FOLDER': 'uploads',
    'MAX_CONTENT_LENGTH': '16777216',  # 16MB
    
    # Caché
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': '300',
    'REDIS_URL': '',
    
    # Entorno
    'FLASK_ENV': 'development',
    'FLASK_DEBUG': 'false',
    'FLASK_TESTING': 'false'
}

def setup_environment():
    """
    Configura las variables de entorno por defecto si no están definidas
    
    Útil para desarrollo local sin archivo .env
    """
    for var, default_value in ENVIRONMENT_VARIABLES.items():
        if not os.environ.get(var):
            os.environ[var] = default_value

# =============================================================================
# INICIALIZACIÓN AUTOMÁTICA
# =============================================================================

# Configurar variables de entorno por defecto
setup_environment()

# Validar configuración al importar el módulo
if __name__ == "__main__":
    print_config_summary()
    if not validate_config():
        print("ADVERTENCIA: Configuración incompleta detectada")
    else:
        print("Configuración válida") 