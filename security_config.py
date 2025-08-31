"""
Configuración de seguridad para el Bot Financiero
"""

# Configuración de contraseñas
PASSWORD_POLICY = {
    'min_length': 8,
    'require_uppercase': True,
    'require_lowercase': True,
    'require_numbers': True,
    'require_special': True,
    'max_age_days': 90,  # Cambio obligatorio cada 90 días
    'history_count': 5   # No reutilizar las últimas 5 contraseñas
}

# Configuración de sesiones
SESSION_POLICY = {
    'timeout_minutes': 120,  # 2 horas
    'max_concurrent_sessions': 3,
    'inactivity_timeout': 30,  # 30 minutos de inactividad
    'regenerate_id': True
}

# Configuración de rate limiting
RATE_LIMITS = {
    'login_attempts': {'max': 5, 'window': 900},      # 5 por 15 minutos
    'registration': {'max': 3, 'window': 3600},       # 3 por hora
    'api_requests': {'max': 100, 'window': 3600},     # 100 por hora
    'admin_actions': {'max': 50, 'window': 3600}      # 50 por hora
}

# Configuración de bloqueo de cuentas
ACCOUNT_LOCKOUT = {
    'max_failed_attempts': 5,
    'lockout_duration_minutes': 30,
    'progressive_lockout': True,
    'unlock_method': 'time_based'  # 'time_based' o 'admin_reset'
}

# Configuración de auditoría
AUDIT_CONFIG = {
    'log_login_attempts': True,
    'log_admin_actions': True,
    'log_financial_transactions': True,
    'log_security_events': True,
    'retention_days': 365
}

# Configuración de headers de seguridad
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;",
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
}

# Configuración de autenticación de dos factores (2FA)
TWO_FACTOR_CONFIG = {
    'enabled': False,  # Habilitar en producción
    'method': 'totp',  # 'totp', 'sms', 'email'
    'issuer': 'Bot Financiero',
    'algorithm': 'sha1',
    'digits': 6,
    'period': 30
}

# Configuración de recuperación de contraseñas
PASSWORD_RECOVERY = {
    'enabled': True,
    'method': 'email',
    'token_expiry_hours': 24,
    'max_attempts_per_day': 3
}

# Configuración de IP permitidas (whitelist)
ALLOWED_IPS = [
    '127.0.0.1',      # Localhost
    '::1',            # IPv6 localhost
    # Agregar IPs de confianza aquí
]

# Configuración de geolocalización
GEO_RESTRICTIONS = {
    'enabled': False,
    'allowed_countries': ['MX', 'US', 'CA'],  # Códigos ISO de países
    'block_vpn': False
}

# Configuración de monitoreo de seguridad
SECURITY_MONITORING = {
    'failed_login_threshold': 10,  # Alertar después de 10 intentos fallidos
    'suspicious_activity_threshold': 5,
    'alert_methods': ['log', 'email'],  # 'log', 'email', 'sms'
    'real_time_alerts': True
}
