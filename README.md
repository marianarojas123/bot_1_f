# 🤖 Bot Financiero Web

Un sistema web inteligente para gestión financiera personal con distribución automática de sueldo y asistente virtual.

## ✨ Características Principales

### 💰 Distribución Automática del Sueldo
- **50% Gastos Básicos** - Vivienda, alimentación, servicios
- **20% Ahorro** - Fondo de emergencia e inversiones
- **15% Educación** - Cursos, libros, desarrollo profesional
- **10% Disfrute** - Entretenimiento, hobbies, viajes
- **5% Donación** - Causas benéficas y ayuda a otros

### 🎯 Funcionalidades del Sistema
- **Dashboard Financiero** - Visualización completa de finanzas
- **Chat Bot Inteligente** - Asesoramiento financiero personalizado
- **Gestión de Ingresos** - Registro y seguimiento automático
- **Panel de Administración** - Gestión de usuarios y sistema
- **Panel de Empleados** - Acceso limitado a información personal
- **Autenticación Segura** - Sistema de roles y permisos

### 🎨 Interfaz Moderna
- Diseño responsivo para todos los dispositivos
- Interfaz intuitiva y fácil de usar
- Iconos de Font Awesome y diseño Bootstrap
- Colores modernos y atractivos

## 🚀 Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd bot-financiero
   ```

2. **Crear entorno virtual (recomendado)**
   ```bash
   python -m venv venv
   
   # En Windows
   venv\Scripts\activate
   
   # En macOS/Linux
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

5. **Acceder al sistema**
   - Abrir navegador en: `http://localhost:5000`
   - Usuario admin por defecto: `admin` / `admin123`

## 📱 Uso del Sistema

### 👤 Registro e Inicio de Sesión
1. **Registro**: Crear cuenta nueva con rol (admin/empleado)
2. **Login**: Acceder con usuario y contraseña
3. **Navegación**: Menú principal con todas las funcionalidades

### 💵 Gestión de Ingresos
1. **Registrar Ingreso**: Formulario con monto, descripción y categoría
2. **Distribución Automática**: El sistema calcula automáticamente la distribución
3. **Historial**: Ver todos los ingresos registrados con detalles

### 🤖 Chat Bot Financiero
1. **Consultas**: Hacer preguntas sobre finanzas personales
2. **Respuestas Inteligentes**: El bot responde con consejos personalizados
3. **Preguntas Frecuentes**: Botones para consultas comunes

### 📊 Dashboard y Reportes
1. **Vista General**: Resumen de situación financiera
2. **Estadísticas**: Gráficos y métricas de distribución
3. **Consejos**: Recomendaciones personalizadas del sistema

## 🔐 Sistema de Roles

### 👑 Administrador (Admin)
- Acceso completo al sistema
- Gestión de usuarios (crear, editar, eliminar)
- Estadísticas del sistema completo
- Configuración y mantenimiento

### 👨‍💼 Empleado
- Acceso limitado a información personal
- Gestión de propios ingresos
- Dashboard personal
- Consultas al chat bot

## 🛠️ Estructura del Proyecto

```
bot-financiero/
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias de Python
├── README.md             # Este archivo
├── templates/            # Plantillas HTML
│   ├── base.html         # Template base
│   ├── index.html        # Página principal
│   ├── login.html        # Página de login
│   ├── registro.html     # Página de registro
│   ├── dashboard.html    # Dashboard principal
│   ├── ingresos.html     # Gestión de ingresos
│   ├── chat.html         # Chat bot
│   ├── admin.html        # Panel de administración
│   └── empleados.html    # Panel de empleados
└── bot_financiero.db     # Base de datos SQLite (se crea automáticamente)
```

## 🗄️ Base de Datos

### Modelos Principales
- **User**: Usuarios del sistema con roles y permisos
- **Ingreso**: Registro de ingresos financieros
- **Distribucion**: Distribución automática de cada ingreso

### Características
- Base de datos SQLite para desarrollo
- Migración automática al iniciar
- Usuario admin creado por defecto

## 🔧 Configuración

### Variables de Entorno
```python
# En app.py
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot_financiero.db'
```

### Personalización
- Cambiar colores en `templates/base.html`
- Modificar distribución de sueldo en `app.py`
- Agregar nuevas funcionalidades según necesidades

## 🚀 Despliegue en Producción

### Para Producción
1. **Cambiar configuración**:
   ```python
   app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
   app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
   ```

2. **Usar servidor WSGI**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

3. **Configurar proxy reverso** (Nginx/Apache)

## 📱 Características Responsivas

- **Mobile First**: Diseño optimizado para móviles
- **Tablet**: Interfaz adaptada para tablets
- **Desktop**: Experiencia completa en pantallas grandes
- **Navegación**: Menú hamburguesa en dispositivos móviles

## 🎨 Personalización de UI

### Colores del Sistema
```css
:root {
    --primary-color: #2563eb;    /* Azul principal */
    --secondary-color: #64748b;  /* Gris secundario */
    --success-color: #10b981;    /* Verde éxito */
    --warning-color: #f59e0b;    /* Amarillo advertencia */
    --danger-color: #ef4444;     /* Rojo peligro */
    --info-color: #06b6d4;       /* Azul información */
}
```

### Iconos y Fuentes
- **Font Awesome**: Iconos del sistema
- **Google Fonts**: Tipografía Inter
- **Bootstrap 5**: Framework CSS

## 🔒 Seguridad

### Características de Seguridad
- **Autenticación**: Sistema de login seguro
- **Autorización**: Control de acceso por roles
- **Encriptación**: Contraseñas hasheadas
- **Sesiones**: Gestión segura de sesiones de usuario

## 🧪 Pruebas

### Ejecutar Pruebas Básicas
1. **Registro de usuario**: Crear cuenta nueva
2. **Login**: Iniciar sesión
3. **Registro de ingreso**: Probar distribución automática
4. **Chat bot**: Hacer consultas al bot
5. **Dashboard**: Verificar visualización de datos

## 📞 Soporte

### Problemas Comunes
1. **Error de dependencias**: Verificar `pip install -r requirements.txt`
2. **Base de datos**: Eliminar `bot_financiero.db` y reiniciar
3. **Puerto ocupado**: Cambiar puerto en `app.py`

### Contacto
- Crear issue en el repositorio
- Documentar error con pasos de reproducción

## 🚀 Roadmap

### Próximas Funcionalidades
- [ ] Gráficos interactivos con Chart.js
- [ ] Exportación de reportes en PDF
- [ ] Notificaciones por email
- [ ] API REST completa
- [ ] Aplicación móvil nativa
- [ ] Integración con bancos
- [ ] Análisis de gastos
- [ ] Metas financieras

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo LICENSE para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

---

**¡Disfruta gestionando tus finanzas de manera inteligente con el Bot Financiero! 🎉**
