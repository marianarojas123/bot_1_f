# 🔒 Guía de Seguridad - Bot Financiero

## **Características de Seguridad Implementadas**

### **🛡️ Protección de Contraseñas**
- **Longitud mínima**: 8 caracteres
- **Requisitos obligatorios**:
  - Al menos 1 mayúscula (A-Z)
  - Al menos 1 minúscula (a-z)
  - Al menos 1 número (0-9)
  - Al menos 1 carácter especial (!@#$%^&*)
- **Hash seguro**: PBKDF2 con SHA256 y 600,000 iteraciones
- **Historial**: No reutilizar las últimas 5 contraseñas

### **🔐 Gestión de Sesiones**
- **Timeout automático**: 2 horas de inactividad
- **Regeneración de ID**: Nueva sesión en cada login
- **Cookies seguras**: HttpOnly, SameSite, Secure (en producción)
- **Múltiples sesiones**: Máximo 3 sesiones concurrentes por usuario

### **🚫 Protección contra Ataques**
- **Rate Limiting**:
  - Login: 5 intentos por 15 minutos
  - Registro: 3 intentos por hora
  - API: 100 requests por hora
- **Bloqueo de cuentas**: 30 minutos después de 5 intentos fallidos
- **Protección CSRF**: Tokens únicos para formularios
- **Sanitización de entrada**: Prevención de XSS

### **📊 Auditoría y Monitoreo**
- **Log de eventos de seguridad**:
  - Intentos de login (exitosos y fallidos)
  - Accesos no autorizados
  - Cambios de contraseña
  - Acciones administrativas
- **Retención**: 365 días de logs
- **Alertas en tiempo real** para actividad sospechosa

### **🌐 Headers de Seguridad**
- **X-Content-Type-Options**: nosniff
- **X-Frame-Options**: DENY (previene clickjacking)
- **X-XSS-Protection**: 1; mode=block
- **Strict-Transport-Security**: HSTS para HTTPS
- **Content-Security-Policy**: Control de recursos
- **Referrer-Policy**: Control de referencias

## **🚨 Medidas de Emergencia**

### **Bloqueo Automático de Cuentas**
- Se activa después de 5 intentos fallidos de login
- Duración: 30 minutos
- Se puede desbloquear manualmente por administrador

### **Detección de Actividad Sospechosa**
- Múltiples intentos de login desde diferentes IPs
- Acceso a rutas administrativas sin autorización
- Patrones de uso anómalos

## **📋 Checklist de Seguridad para Producción**

### **Configuración del Servidor**
- [ ] HTTPS habilitado con certificado válido
- [ ] Firewall configurado
- [ ] Puertos innecesarios cerrados
- [ ] Actualizaciones de seguridad automáticas

### **Configuración de la Aplicación**
- [ ] DEBUG = False
- [ ] SECRET_KEY cambiada y segura
- [ ] SESSION_COOKIE_SECURE = True
- [ ] Rate limiting habilitado
- [ ] Logs de seguridad configurados

### **Base de Datos**
- [ ] Usuarios con contraseñas fuertes
- [ ] Acceso restringido por IP
- [ ] Backups regulares y seguros
- [ ] Encriptación de datos sensibles

## **🔧 Comandos de Seguridad**

### **Verificar Logs de Seguridad**
```bash
# Ver eventos de seguridad
grep "SECURITY_EVENT" logs/app.log

# Ver intentos de login fallidos
grep "LOGIN_FAILED" logs/app.log

# Ver accesos no autorizados
grep "UNAUTHORIZED" logs/app.log
```

### **Bloquear Usuario Manualmente**
```python
# En la consola de Python
from app import app, db, User
with app.app_context():
    user = User.query.filter_by(username='usuario_sospechoso').first()
    user.locked_until = datetime.utcnow() + timedelta(hours=24)
    db.session.commit()
```

### **Generar Nueva Secret Key**
```python
import secrets
new_secret = secrets.token_urlsafe(32)
print(f"Nueva SECRET_KEY: {new_secret}")
```

## **📞 Contacto de Emergencia**

En caso de incidente de seguridad:
1. **Inmediato**: Bloquear cuentas comprometidas
2. **1 hora**: Revisar logs y determinar alcance
3. **24 horas**: Reporte completo del incidente
4. **72 horas**: Implementar medidas correctivas

## **🔄 Actualizaciones de Seguridad**

- **Revisar logs** diariamente
- **Actualizar dependencias** semanalmente
- **Auditoría completa** mensualmente
- **Revisión de políticas** trimestralmente

---

**⚠️ IMPORTANTE**: Esta guía debe mantenerse actualizada y todos los administradores deben estar familiarizados con estas medidas de seguridad.
