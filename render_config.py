import os

class Config:
    """Configuración base para la aplicación"""
    
    # Configuración básica
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-secreta-por-defecto-cambiar-en-produccion')
    DEBUG = False
    TESTING = False
    
    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///bot_financiero.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de sesiones
    PERMANENT_SESSION_LIFETIME = 86400  # 24 horas en segundos
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # Configuración de seguridad
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Configuración de archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

class DevelopmentConfig(Config):
    """Configuración para desarrollo local"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///bot_financiero.db'
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Configuración para producción (Render)"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///bot_financiero.db')

def get_config():
    """Retorna la configuración apropiada según el entorno"""
    if os.environ.get('FLASK_ENV') == 'production' or os.environ.get('RENDER'):
        return ProductionConfig
    else:
        return DevelopmentConfig
