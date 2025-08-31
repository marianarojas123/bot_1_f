import os
from datetime import timedelta

class RenderConfig:
    """Configuración específica para Render.com"""
    
    # Configuración básica
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-secreta-por-defecto-cambiar-en-produccion')
    DEBUG = False
    TESTING = False
    
    # Base de datos - Render proporciona DATABASE_URL automáticamente
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///bot_financiero.db')
    
    # Configuración de sesiones
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # Configuración de seguridad
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Configuración de logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/app.log'
    
    # Configuración de caché
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Configuración de rate limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT = '200 per day;50 per hour'
    
    # Configuración de archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Configuración de email (para futuras funcionalidades)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configuración de Redis (para sesiones en producción)
    REDIS_URL = os.environ.get('REDIS_URL')
    
    # Configuración de CDN (para archivos estáticos)
    CDN_DOMAIN = os.environ.get('CDN_DOMAIN')
    
    # Configuración de monitoreo
    ENABLE_MONITORING = os.environ.get('ENABLE_MONITORING', 'false').lower() == 'true'
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    
    # Configuración de backup
    BACKUP_ENABLED = os.environ.get('BACKUP_ENABLED', 'false').lower() == 'true'
    BACKUP_SCHEDULE = os.environ.get('BACKUP_SCHEDULE', '0 2 * * *')  # 2 AM daily
    
    # Configuración de notificaciones
    NOTIFICATIONS_ENABLED = os.environ.get('NOTIFICATIONS_ENABLED', 'false').lower() == 'true'
    SLACK_WEBHOOK = os.environ.get('SLACK_WEBHOOK')
    DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK')
    
    # Configuración de analytics
    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID')
    FACEBOOK_PIXEL_ID = os.environ.get('FACEBOOK_PIXEL_ID')
    
    # Configuración de SEO
    SITE_NAME = 'Bot Financiero'
    SITE_DESCRIPTION = 'Sistema inteligente para gestión financiera personal'
    SITE_KEYWORDS = 'finanzas, ahorro, inversión, presupuesto, bot financiero'
    SITE_AUTHOR = 'Bot Financiero Team'
    SITE_URL = os.environ.get('SITE_URL', 'https://bot-financiero.onrender.com')
    
    # Configuración de mantenimiento
    MAINTENANCE_MODE = os.environ.get('MAINTENANCE_MODE', 'false').lower() == 'true'
    MAINTENANCE_MESSAGE = os.environ.get('MAINTENANCE_MESSAGE', 'Sitio en mantenimiento. Volveremos pronto.')
    
    # Configuración de desarrollo
    DEVELOPMENT_MODE = os.environ.get('DEVELOPMENT_MODE', 'false').lower() == 'true'
    ENABLE_DEBUG_TOOLBAR = False
    ENABLE_PROFILER = False
