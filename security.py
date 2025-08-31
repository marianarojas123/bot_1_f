import re
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash

class SecurityManager:
    """Gestor de seguridad para la aplicación"""
    
    @staticmethod
    def validate_password(password):
        """Valida que la contraseña cumpla con los requisitos de seguridad"""
        if len(password) < current_app.config.get('PASSWORD_MIN_LENGTH', 8):
            return False, "La contraseña debe tener al menos 8 caracteres"
        
        if current_app.config.get('PASSWORD_REQUIRE_UPPERCASE', True):
            if not re.search(r'[A-Z]', password):
                return False, "La contraseña debe contener al menos una mayúscula"
        
        if current_app.config.get('PASSWORD_REQUIRE_LOWERCASE', True):
            if not re.search(r'[a-z]', password):
                return False, "La contraseña debe contener al menos una minúscula"
        
        if current_app.config.get('PASSWORD_REQUIRE_NUMBERS', True):
            if not re.search(r'\d', password):
                return False, "La contraseña debe contener al menos un número"
        
        if current_app.config.get('PASSWORD_REQUIRE_SPECIAL', True):
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                return False, "La contraseña debe contener al menos un carácter especial"
        
        return True, "Contraseña válida"
    
    @staticmethod
    def generate_secure_token():
        """Genera un token seguro para CSRF"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_password(password):
        """Genera un hash seguro de la contraseña"""
        return generate_password_hash(password, method='pbkdf2:sha256:600000')
    
    @staticmethod
    def verify_password(password_hash, password):
        """Verifica una contraseña contra su hash"""
        return check_password_hash(password_hash, password)
    
    @staticmethod
    def sanitize_input(text):
        """Sanitiza entrada de texto para prevenir XSS"""
        if not text:
            return ""
        
        # Remover caracteres peligrosos
        dangerous_chars = ['<', '>', '"', "'", '&']
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        return text.strip()
    
    @staticmethod
    def is_suspicious_activity(user_id, action):
        """Detecta actividad sospechosa"""
        # Implementar lógica de detección de anomalías
        # Por ahora, solo registro básico
        current_app.logger.warning(f"Actividad sospechosa detectada: Usuario {user_id}, Acción: {action}")
        return False

class RateLimiter:
    """Sistema de rate limiting simple en memoria"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, key, limit, window):
        """Verifica si una solicitud está permitida"""
        now = datetime.now()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Limpiar solicitudes antiguas
        self.requests[key] = [req_time for req_time in self.requests[key] 
                             if now - req_time < timedelta(seconds=window)]
        
        if len(self.requests[key]) >= limit:
            return False
        
        self.requests[key].append(now)
        return True

# Instancia global del rate limiter
rate_limiter = RateLimiter()

def rate_limit(limit, window, methods=None):
    """Decorador para aplicar rate limiting solo a métodos específicos"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Si se especifican métodos, solo aplicar rate limiting a esos métodos
            if methods and request.method not in methods:
                return f(*args, **kwargs)
            
            # Usar IP del usuario como clave
            key = request.remote_addr
            
            if not rate_limiter.is_allowed(key, limit, window):
                return jsonify({
                    'error': 'Demasiadas solicitudes. Intenta más tarde.',
                    'retry_after': window
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_strong_password(f):
    """Decorador para requerir contraseñas fuertes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            password = request.form.get('password')
            if password:
                is_valid, message = SecurityManager.validate_password(password)
                if not is_valid:
                    return jsonify({'error': message}), 400
        
        return f(*args, **kwargs)
    return decorated_function

def log_security_event(event_type, user_id=None, details=None):
    """Registra eventos de seguridad"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'event_type': event_type,
        'user_id': user_id,
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
        'details': details or {}
    }
    
    current_app.logger.info(f"SECURITY_EVENT: {log_entry}")
    return log_entry

def add_security_headers(response):
    """Agrega headers de seguridad a las respuestas"""
    config = current_app.config
    
    # Headers básicos de seguridad
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Headers adicionales si están configurados
    if hasattr(config, 'SECURITY_HEADERS'):
        for header, value in config.SECURITY_HEADERS.items():
            response.headers[header] = value
    
    return response

def validate_session():
    """Valida la sesión del usuario"""
    if not session.get('user_id'):
        return False, "Sesión no válida"
    
    # Verificar si la sesión no ha expirado
    last_activity = session.get('last_activity')
    if last_activity:
        last_activity = datetime.fromisoformat(last_activity)
        if datetime.now() - last_activity > timedelta(hours=2):
            session.clear()
            return False, "Sesión expirada"
    
    # Actualizar última actividad
    session['last_activity'] = datetime.now().isoformat()
    return True, "Sesión válida"

def require_valid_session(f):
    """Decorador para requerir sesión válida"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_valid, message = validate_session()
        if not is_valid:
            return jsonify({'error': message}), 401
        
        return f(*args, **kwargs)
    return decorated_function
