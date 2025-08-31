import os
from datetime import timedelta

class Config:
    """Configuración base del sistema"""
    
    # Configuración básica
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de seguridad
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    WTF_CSRF_SSL_STRICT = True
    
    # Configuración de sesión
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)  # Sesiones más cortas
    SESSION_COOKIE_SECURE = False  # Cambiar a True en producción con HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_MAX_AGE = 7200  # 2 horas
    
    # Configuración de rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT = '100 per hour'
    RATELIMIT_LOGIN = '5 per 15 minutes'
    
    # Configuración de contraseñas
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL = True
    
    # Configuración de la aplicación
    APP_NAME = 'Bot Financiero'
    APP_VERSION = '1.0.0'
    APP_DESCRIPTION = 'Sistema de gestión financiera personal con distribución automática de sueldo'
    
    # Configuración de paginación
    ITEMS_PER_PAGE = 10
    
    # Configuración de distribución de sueldo original
    DISTRIBUCION_SUELDO = {
        'gastos_fijos': 0.50,        # 50% - Vivienda, servicios, seguros
        'ahorro': 0.20,              # 20% - Fondo de emergencia
        'educacion': 0.15,           # 15% - Educación y desarrollo
        'disfrute': 0.10,            # 10% - Entretenimiento y ocio
        'donacion': 0.05             # 5% - Donaciones y causas benéficas
    }
    
    # Configuración de categorías de ingresos mejorada
    CATEGORIAS_INGRESOS = [
        'Sueldo Base',
        'Bono por Rendimiento',
        'Horas Extras',
        'Freelance',
        'Inversiones',
        'Rentas',
        'Comisiones',
        'Otros Ingresos'
    ]
    
    # Configuración del chat bot original
    CHAT_BOT_RESPUESTAS = {
        'hola': '¡Hola! Soy tu asistente financiero. ¿En qué puedo ayudarte?',
        'ayuda': 'Puedo ayudarte con: distribución de sueldo, ahorros, presupuestos y más.',
        'distribucion': 'Tu sueldo se distribuye automáticamente: 50% gastos fijos, 20% ahorro, 15% educación, 10% disfrute, 5% donación.',
        'gastos_fijos': 'El 50% de tu sueldo se destina a gastos fijos como vivienda, alimentación, servicios y obligaciones mensuales.',
        'ahorro': 'El 20% de tu sueldo va automáticamente a ahorro. ¡Excelente hábito financiero!',
        'educacion': 'El 15% de tu sueldo se destina a educación y desarrollo profesional.',
        'disfrute': 'El 10% de tu sueldo es para disfrute y entretenimiento personal.',
        'donacion': 'El 5% de tu sueldo se destina a donaciones y causas benéficas.',
        'presupuesto': 'Para hacer un presupuesto: 1) Registra todos tus ingresos, 2) Categoriza tus gastos, 3) Revisa la distribución automática, 4) Ajusta según tus necesidades.',
        'emergencia': 'El 20% de ahorro te ayudará a crear un fondo de emergencia de 3-6 meses de gastos.',
        'gastos': 'El 50% de gastos fijos debe incluir vivienda, alimentación, servicios y pagos mínimos de deudas.'
    }

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///bot_financiero_dev.db'
    
    # Configuración de desarrollo
    TESTING = False
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Configuración para producción en Hostinger"""
    
    DEBUG = False
    # Base de datos para producción (MySQL en Hostinger)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql://username:password@localhost/database_name'
    
    # Configuración de producción
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora
    
    # Configuración de seguridad adicional
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 1800  # 30 minutos
    WTF_CSRF_SSL_STRICT = True
    
    # Configuración de headers de seguridad
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
    }
    
    # Configuración de rate limiting más estricto
    RATELIMIT_DEFAULT = '100 per hour'  # Aumentado de 50 a 100
    RATELIMIT_LOGIN = '5 per 15 minutes'  # Aumentado de 3 a 5
    
    # Configuración de logging para producción
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/app.log'
    
    # Configuración de caché para producción
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300

class TestingConfig(Config):
    """Configuración para pruebas"""
    
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///bot_financiero_test.db'
    
    # Configuración de pruebas
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False

# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Obtiene la configuración según el entorno"""
    config_name = os.environ.get('FLASK_ENV', 'default')
    return config.get(config_name, config['default'])
