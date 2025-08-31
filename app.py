import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

# Inicializar Flask
app = Flask(__name__)

# Configuración simple y robusta para Render
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave-secreta-por-defecto-cambiar-en-produccion')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///bot_financiero.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = False
app.config['TESTING'] = False

# Configuración de sesiones
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_COOKIE_SECURE'] = False  # Cambiado a False para evitar problemas en Render
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Configuración de seguridad
app.config['WTF_CSRF_ENABLED'] = False  # Deshabilitado temporalmente para evitar errores
app.config['WTF_CSRF_TIME_LIMIT'] = 3600

# Configuración de distribución de sueldo
app.config['DISTRIBUCION_SUELDO'] = {
    'gastos_fijos': 0.50,      # 50% gastos básicos
    'ahorro': 0.20,            # 20% ahorro
    'educacion': 0.15,         # 15% educación
    'disfrute': 0.10,          # 10% disfrute
    'donacion': 0.05            # 5% donación
}

# Configuración de categorías de ingresos
app.config['CATEGORIAS_INGRESOS'] = [
    'Salario', 'Freelance', 'Inversiones', 'Otros'
]

# Configuración de paginación
app.config['ITEMS_PER_PAGE'] = 10

# Configuración del chat bot
app.config['CHAT_BOT_RESPUESTAS'] = {
    'distribución': 'La distribución automática del sueldo es: 50% gastos básicos, 20% ahorro, 15% educación, 10% disfrute, 5% donación.',
    'ahorro': 'El 20% de tu ingreso se destina automáticamente al ahorro. Te recomendamos mantener esta proporción.',
    'gastos': 'El 50% se destina a gastos básicos como vivienda, alimentación y servicios.',
    'educación': 'El 15% se destina a tu desarrollo profesional: cursos, libros, certificaciones.',
    'presupuesto': 'El sistema calcula automáticamente la distribución de cada ingreso que registres.',
    'ayuda': 'Puedes preguntarme sobre: distribución, ahorro, gastos, educación, presupuesto, etc.'
}

# Inicializar extensiones
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'

# Configuración de logging simple
import logging
if not os.path.exists('logs'):
    os.mkdir('logs')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/bot_financiero.log'),
        logging.StreamHandler()
    ]
)

# Modelos de base de datos
class User(UserMixin, db.Model):
    """Modelo de usuario del sistema con roles mejorados"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='empleado')  # 'admin', 'empleado', 'cliente'
    nombre_completo = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    departamento = db.Column(db.String(50))
    salario = db.Column(db.Float)
    fecha_contratacion = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    permisos_especiales = db.Column(db.Text)  # JSON string para permisos adicionales
    
    # Relaciones
    ingresos = db.relationship('Ingreso', backref='usuario', lazy=True)
    distribuciones = db.relationship('Distribucion', backref='usuario', lazy=True)
    clientes_asignados = db.relationship('Cliente', backref='usuario_asignado', lazy=True)
    
    def has_permission(self, permission):
        """Verifica si el usuario tiene un permiso específico"""
        if self.role == 'admin':
            return True
        if self.role == 'empleado':
            return permission in ['ver_ingresos', 'ver_dashboard', 'ver_clientes_asignados']
        if self.role == 'cliente':
            return permission in ['ver_ingresos_propios', 'ver_dashboard_propio']
        return False
    
    def can_access_admin_panel(self):
        """Verifica si puede acceder al panel de administración"""
        return self.role == 'admin'
    
    def can_manage_users(self):
        """Verifica si puede gestionar usuarios"""
        return self.role == 'admin'
    
    def can_manage_clientes(self):
        """Verifica si puede gestionar clientes"""
        return self.role in ['admin', 'empleado']
    
    def can_view_financial_data(self):
        """Verifica si puede ver datos financieros"""
        if self.role == 'admin':
            return True
        if self.role == 'empleado':
            return True
        if self.role == 'cliente':
            return False  # Los clientes no ven datos financieros de otros
        return False
    
    def set_password(self, password):
        """Establece la contraseña hasheada"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica la contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Ingreso(db.Model):
    """Modelo de ingreso financiero"""
    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relaciones
    distribuciones = db.relationship('Distribucion', backref='ingreso', lazy=True)
    
    def __repr__(self):
        return f'<Ingreso {self.descripcion}: ${self.monto}>'

class Distribucion(db.Model):
    """Modelo de distribución automática del ingreso"""
    id = db.Column(db.Integer, primary_key=True)
    ingreso_id = db.Column(db.Integer, db.ForeignKey('ingreso.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    categoria_distribucion = db.Column(db.String(50), nullable=False)
    porcentaje = db.Column(db.Float, nullable=False)
    monto_asignado = db.Column(db.Float, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Distribucion {self.categoria_distribucion}: {self.porcentaje}%>'

class Cliente(db.Model):
    """Modelo de cliente del negocio mejorado"""
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    empresa = db.Column(db.String(100))
    categoria = db.Column(db.String(20), default='Básico')  # Básico, Estándar, Premium
    estado = db.Column(db.String(20), default='Prospecto')  # Prospecto, Activo, Inactivo
    origen = db.Column(db.String(50), default='Web')  # Web, Referido, Marketing, Evento
    notas = db.Column(db.Text)
    ultimo_contacto = db.Column(db.DateTime)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Usuario que lo registró
    
    # Campos adicionales para mejor gestión
    direccion = db.Column(db.Text)
    sitio_web = db.Column(db.String(200))
    redes_sociales = db.Column(db.Text)  # JSON string
    valor_cliente = db.Column(db.Float, default=0.0)  # Valor monetario del cliente
    frecuencia_contacto = db.Column(db.String(20), default='Mensual')  # Diario, Semanal, Mensual, Trimestral
    preferencias_contacto = db.Column(db.String(50), default='Email')  # Email, Teléfono, WhatsApp, etc.
    tags = db.Column(db.Text)  # JSON string para etiquetas personalizadas
    
    # Relaciones
    historial_contactos = db.relationship('ContactoCliente', backref='cliente', lazy=True)
    oportunidades = db.relationship('Oportunidad', backref='cliente', lazy=True)
    
    def __repr__(self):
        return f'<Cliente {self.nombre}>'
    
    def actualizar_ultimo_contacto(self):
        """Actualiza la fecha del último contacto"""
        self.ultimo_contacto = datetime.utcnow()
        return self

class ContactoCliente(db.Model):
    """Modelo para historial de contactos con clientes"""
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tipo_contacto = db.Column(db.String(50), nullable=False)  # Llamada, Email, Reunión, etc.
    descripcion = db.Column(db.Text, nullable=False)
    resultado = db.Column(db.String(100))  # Exitoso, Pendiente, No interesado, etc.
    proximo_seguimiento = db.Column(db.DateTime)
    fecha_contacto = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ContactoCliente {self.tipo_contacto} con {self.cliente_id}>'

class Oportunidad(db.Model):
    """Modelo para oportunidades de negocio"""
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    valor_estimado = db.Column(db.Float)
    probabilidad = db.Column(db.Float, default=0.5)  # 0.0 a 1.0
    etapa = db.Column(db.String(50), default='Prospección')  # Prospección, Calificación, Propuesta, Negociación, Cerrado
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_cierre_esperada = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Usuario responsable
    
    def __repr__(self):
        return f'<Oportunidad {self.titulo} - {self.cliente_id}>'

class Permiso(db.Model):
    """Modelo para permisos granulares del sistema"""
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    modulo = db.Column(db.String(50))  # admin, empleados, clientes, ingresos, etc.
    activo = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Permiso {self.nombre}>'

class RolPermiso(db.Model):
    """Modelo para asignar permisos a roles"""
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False)  # admin, empleado, cliente
    permiso_id = db.Column(db.Integer, db.ForeignKey('permiso.id'), nullable=False)
    
    def __repr__(self):
        return f'<RolPermiso {self.role} - {self.permiso_id}>'

# Configurar login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rutas principales
@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    try:
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                flash('Por favor completa todos los campos', 'error')
                return render_template('login.html')
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password) and user.is_active:
                login_user(user)
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                app.logger.info(f'Login exitoso para usuario: {username}')
                flash(f'¡Bienvenido, {user.username}!', 'success')
                
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            else:
                app.logger.warning(f'Login fallido para usuario: {username}')
                flash('Usuario o contraseña incorrectos', 'error')
        
        return render_template('login.html')
    except Exception as e:
        app.logger.error(f'Error en login: {str(e)}')
        flash('Error interno del servidor. Intenta nuevamente.', 'error')
        return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """Página de registro de usuarios"""
    try:
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            role = request.form.get('role', 'empleado')
            
            # Validaciones básicas
            if not all([username, email, password, confirm_password]):
                flash('Por favor completa todos los campos', 'error')
                return render_template('registro.html')
            
            if password != confirm_password:
                flash('Las contraseñas no coinciden', 'error')
                return render_template('registro.html')
            
            # Verificar si el usuario ya existe
            if User.query.filter_by(username=username).first():
                flash('El nombre de usuario ya está en uso', 'error')
                return render_template('registro.html')
            
            if User.query.filter_by(email=email).first():
                flash('El email ya está registrado', 'error')
                return render_template('registro.html')
            
            # Crear usuario
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            
            try:
                db.session.add(user)
                db.session.commit()
                
                app.logger.info(f'Usuario registrado: {username} con rol: {role}')
                flash('Usuario registrado exitosamente. Por favor inicia sesión.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'Error registrando usuario: {str(e)}')
                flash('Error al registrar usuario. Intenta nuevamente.', 'error')
        
        return render_template('registro.html')
    except Exception as e:
        app.logger.error(f'Error en registro: {str(e)}')
        flash('Error interno del servidor. Intenta nuevamente.', 'error')
        return render_template('registro.html')

@app.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    try:
        username = current_user.username
        logout_user()
        app.logger.info(f'Usuario cerró sesión: {username}')
        flash('Has cerrado sesión exitosamente', 'info')
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f'Error en logout: {str(e)}')
        return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal del usuario"""
    # Obtener estadísticas del usuario
    total_ingresos = Ingreso.query.filter_by(user_id=current_user.id).count()
    total_monto = db.session.query(db.func.sum(Ingreso.monto)).filter_by(user_id=current_user.id).scalar() or 0
    
    # Obtener distribución del mes actual
    mes_actual = datetime.now().month
    ano_actual = datetime.now().year
    
    ingresos_mes = Ingreso.query.filter(
        Ingreso.user_id == current_user.id,
        db.extract('month', Ingreso.fecha) == mes_actual,
        db.extract('year', Ingreso.fecha) == ano_actual
    ).all()
    
    total_mes = sum(ingreso.monto for ingreso in ingresos_mes)
    
    # Calcular distribución del mes
    distribucion_mes = {}
    for ingreso in ingresos_mes:
        for dist in ingreso.distribuciones:
            if dist.categoria_distribucion not in distribucion_mes:
                distribucion_mes[dist.categoria_distribucion] = 0
            distribucion_mes[dist.categoria_distribucion] += dist.monto_asignado
    
    # Crear distribución para el template (valores por defecto si no hay ingresos)
    distribucion = {
        'gastos_fijos': distribucion_mes.get('gastos_fijos', 0),
        'ahorro': distribucion_mes.get('ahorro', 0),
        'educacion': distribucion_mes.get('educacion', 0),
        'disfrute': distribucion_mes.get('disfrute', 0),
        'donacion': distribucion_mes.get('donacion', 0)
    }
    
    # Obtener últimos ingresos
    ultimos_ingresos = Ingreso.query.filter_by(user_id=current_user.id).order_by(Ingreso.fecha.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         total_ingresos=total_ingresos,
                         total_monto=total_monto,
                         total_mes=total_monto,  # Cambiado para mostrar total general
                         distribucion=distribucion,
                         ultimos_ingresos=ultimos_ingresos)

@app.route('/ingresos', methods=['GET', 'POST'])
@login_required
def ingresos():
    """Gestión de ingresos"""
    if request.method == 'POST':
        monto = request.form.get('monto')
        descripcion = request.form.get('descripcion')
        categoria = request.form.get('categoria')
        
        if not all([monto, descripcion, categoria]):
            flash('Por favor completa todos los campos', 'error')
            return redirect(url_for('ingresos'))
        
        try:
            monto = float(monto)
            if monto <= 0:
                flash('El monto debe ser mayor a 0', 'error')
                return redirect(url_for('ingresos'))
        except ValueError:
            flash('El monto debe ser un número válido', 'error')
            return redirect(url_for('ingresos'))
        
        # Crear ingreso
        ingreso = Ingreso(
            monto=monto,
            descripcion=descripcion,  # Simplificado sin sanitización
            categoria=categoria,
            user_id=current_user.id
        )
        
        db.session.add(ingreso)
        db.session.flush()  # Para obtener el ID del ingreso
        
        # Crear distribución automática
        distribucion_config = app.config['DISTRIBUCION_SUELDO']
        for categoria_dist, porcentaje in distribucion_config.items():
            monto_asignado = monto * porcentaje
            distribucion = Distribucion(
                ingreso_id=ingreso.id,
                user_id=current_user.id,
                categoria_distribucion=categoria_dist,
                porcentaje=porcentaje * 100,
                monto_asignado=monto_asignado
            )
            db.session.add(distribucion)
        
        db.session.commit()
        
        flash(f'Ingreso registrado exitosamente: ${monto:,.2f}', 'success')
        return redirect(url_for('ingresos'))
    
    # Obtener ingresos del usuario
    page = request.args.get('page', 1, type=int)
    ingresos = Ingreso.query.filter_by(user_id=current_user.id).order_by(Ingreso.fecha.desc()).paginate(
        page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False
    )
    
    categorias = app.config['CATEGORIAS_INGRESOS']
    
    return render_template('ingresos.html', ingresos=ingresos, categorias=categorias)

@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    """Chat bot financiero"""
    if request.method == 'POST':
        mensaje = request.form.get('mensaje', '').lower().strip()
        
        if not mensaje:
            return jsonify({'error': 'Por favor ingresa un mensaje'})
        
        # Obtener respuesta del bot
        respuestas = app.config['CHAT_BOT_RESPUESTAS']
        respuesta = respuestas.get(mensaje, 'No entiendo tu consulta. Puedes preguntarme sobre: distribución, ahorro, gastos, presupuesto, etc.')
        
        return jsonify({'respuesta': respuesta})
    
    return render_template('chat.html')

@app.route('/admin')
@login_required
def admin():
    """Panel de administración - Solo para administradores"""
    if not current_user.can_access_admin_panel():
        flash('Acceso denegado. Solo los administradores pueden acceder al panel de administración.', 'error')
        return redirect(url_for('dashboard'))
    
    # Estadísticas del sistema
    total_usuarios = User.query.count()
    total_empleados = User.query.filter_by(role='empleado').count()
    total_clientes_usuarios = User.query.filter_by(role='cliente').count()
    total_ingresos_sistema = db.session.query(db.func.sum(Ingreso.monto)).scalar() or 0
    usuarios_activos = User.query.filter_by(is_active=True).count()
    
    # Usuarios recientes
    usuarios_recientes = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    # Estadísticas por rol
    usuarios_por_rol = {
        'admin': User.query.filter_by(role='admin').count(),
        'empleado': total_empleados,
        'cliente': total_clientes_usuarios
    }
    
    return render_template('admin.html',
                         total_usuarios=total_usuarios,
                         total_ingresos=total_ingresos_sistema,
                         usuarios_activos=usuarios_activos,
                         usuarios_recientes=usuarios_recientes,
                         usuarios_por_rol=usuarios_por_rol)

@app.route('/empleados')
@login_required
def empleados():
    """Panel de empleados - Solo para administradores y empleados senior"""
    if not current_user.can_manage_clientes():
        flash('Acceso denegado. No tienes permisos para acceder a esta página.', 'error')
        return redirect(url_for('dashboard'))
    
    # Obtener empleados según el rol del usuario
    if current_user.role == 'admin':
        empleados = User.query.filter_by(role='empleado').all()
    else:
        # Los empleados solo ven información básica de otros empleados
        empleados = User.query.filter_by(role='empleado').filter_by(is_active=True).all()
    
    # Estadísticas de empleados
    total_empleados = User.query.filter_by(role='empleado').count()
    empleados_activos = User.query.filter_by(role='empleado', is_active=True).count()
    empleados_inactivos = total_empleados - empleados_activos
    
    return render_template('empleados.html', 
                         empleados=empleados,
                         total_empleados=total_empleados,
                         empleados_activos=empleados_activos,
                         empleados_inactivos=empleados_inactivos)

@app.route('/gestionar-usuarios')
@login_required
def gestionar_usuarios():
    """Gestión completa de usuarios - Solo para administradores"""
    if not current_user.can_manage_users():
        flash('Acceso denegado. Solo los administradores pueden gestionar usuarios.', 'error')
        return redirect(url_for('dashboard'))
    
    # Obtener usuarios por rol
    administradores = User.query.filter_by(role='admin').all()
    empleados = User.query.filter_by(role='empleado').all()
    clientes_usuarios = User.query.filter_by(role='cliente').all()
    
    # Estadísticas
    total_usuarios = User.query.count()
    usuarios_activos = User.query.filter_by(is_active=True).count()
    usuarios_inactivos = total_usuarios - usuarios_activos
    
    return render_template('gestionar_usuarios.html',
                         administradores=administradores,
                         empleados=empleados,
                         clientes_usuarios=clientes_usuarios,
                         total_usuarios=total_usuarios,
                         usuarios_activos=usuarios_activos,
                         usuarios_inactivos=usuarios_inactivos)

@app.route('/empleado/<int:user_id>')
@login_required
def ver_empleado(user_id):
    """Ver perfil de empleado específico"""
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    empleado = User.query.get_or_404(user_id)
    if empleado.role != 'empleado':
        flash('Usuario no es un empleado', 'error')
        return redirect(url_for('empleados'))
    
    # Obtener ingresos del empleado
    ingresos_empleado = Ingreso.query.filter_by(user_id=user_id).order_by(Ingreso.fecha.desc()).all()
    
    return render_template('empleado_detalle.html', empleado=empleado, ingresos=ingresos_empleado)

@app.route('/clientes')
@login_required
def clientes():
    """Panel de clientes - Solo para administradores y empleados"""
    if not current_user.can_manage_clientes():
        flash('Acceso denegado. No tienes permisos para acceder a esta página.', 'error')
        return redirect(url_for('dashboard'))
    
    # Obtener clientes según el rol del usuario
    if current_user.role == 'admin':
        # Los administradores ven todos los clientes
        clientes = Cliente.query.all()
    else:
        # Los empleados solo ven los clientes asignados a ellos
        clientes = Cliente.query.filter_by(user_id=current_user.id).all()
    
    # Estadísticas de clientes
    total_clientes = Cliente.query.count()
    clientes_premium = Cliente.query.filter_by(categoria='Premium').count()
    clientes_activos = Cliente.query.filter_by(estado='Activo').count()
    clientes_prospectos = Cliente.query.filter_by(estado='Prospecto').count()
    
    return render_template('clientes.html', 
                         clientes=clientes,
                         total_clientes=total_clientes,
                         clientes_premium=clientes_premium,
                         clientes_activos=clientes_activos,
                         clientes_prospectos=clientes_prospectos)

@app.route('/cliente/<int:cliente_id>')
@login_required
def ver_cliente(cliente_id):
    """Ver perfil de cliente específico"""
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    cliente = Cliente.query.get_or_404(cliente_id)
    
    return render_template('cliente_detalle.html', cliente=cliente)

@app.route('/cliente/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_cliente():
    """Crear nuevo cliente"""
    if current_user.role != 'admin':
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        empresa = request.form.get('empresa')
        categoria = request.form.get('categoria')
        estado = request.form.get('estado')
        origen = request.form.get('origen')
        notas = request.form.get('notas')
        
        # Validar email único
        if Cliente.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'error')
            return render_template('nuevo_cliente.html')
        
        # Crear cliente
        nuevo_cliente = Cliente(
            nombre=nombre,
            email=email,
            telefono=telefono,
            empresa=empresa,
            categoria=categoria,
            estado=estado,
            origen=origen,
            notas=notas,
            user_id=current_user.id
        )
        
        db.session.add(nuevo_cliente)
        db.session.commit()
        
        flash('Cliente creado exitosamente', 'success')
        return redirect(url_for('clientes'))
    
    return render_template('nuevo_cliente.html')

# Rutas adicionales para libros contables
@app.route('/libro-diario')
@login_required
def libro_diario():
    """Libro diario de ingresos"""
    fecha = request.args.get('fecha', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
    except ValueError:
        fecha_obj = datetime.now()
        fecha = fecha_obj.strftime('%Y-%m-%d')
    
    ingresos_dia = Ingreso.query.filter(
        Ingreso.user_id == current_user.id,
        db.func.date(Ingreso.fecha) == fecha_obj.date()
    ).all()
    
    return render_template('libro_diario.html', ingresos=ingresos_dia, fecha=fecha)

@app.route('/libro-mensual')
@login_required
def libro_mensual():
    """Libro mensual de ingresos"""
    mes = request.args.get('mes', datetime.now().strftime('%Y-%m'))
    
    try:
        ano, mes_num = mes.split('-')
        ingresos_mes = Ingreso.query.filter(
            Ingreso.user_id == current_user.id,
            db.extract('year', Ingreso.fecha) == int(ano),
            db.extract('month', Ingreso.fecha) == int(mes_num)
        ).all()
    except ValueError:
        ingresos_mes = []
        mes = datetime.now().strftime('%Y-%m')
    
    return render_template('libro_mensual.html', ingresos=ingresos_mes, mes=mes)

@app.route('/libro-anual')
@login_required
def libro_anual():
    """Libro anual de ingresos"""
    ano = request.args.get('ano', datetime.now().year)
    
    try:
        ano = int(ano)
        ingresos_ano = Ingreso.query.filter(
            Ingreso.user_id == current_user.id,
            db.extract('year', Ingreso.fecha) == ano
        ).all()
    except ValueError:
        ingresos_ano = []
        ano = datetime.now().year
    
    return render_template('libro_anual.html', ingresos=ingresos_ano, ano=ano)

# Rutas para API
@app.route('/api/ingresos', methods=['GET'])
@login_required
def api_ingresos():
    """API para obtener ingresos del usuario"""
    ingresos = Ingreso.query.filter_by(user_id=current_user.id).order_by(Ingreso.fecha.desc()).all()
    
    return jsonify([{
        'id': ingreso.id,
        'monto': ingreso.monto,
        'descripcion': ingreso.descripcion,
        'categoria': ingreso.categoria,
        'fecha': ingreso.fecha.isoformat()
    } for ingreso in ingresos])

@app.route('/api/distribucion/<int:ingreso_id>')
@login_required
def api_distribucion(ingreso_id):
    """API para obtener distribución de un ingreso específico"""
    ingreso = Ingreso.query.get_or_404(ingreso_id)
    
    # Verificar que el ingreso pertenece al usuario
    if ingreso.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Acceso denegado'}), 403
    
    distribuciones = Distribucion.query.filter_by(ingreso_id=ingreso_id).all()
    
    return jsonify([{
        'categoria': dist.categoria_distribucion,
        'porcentaje': dist.porcentaje,
        'monto': dist.monto_asignado
    } for dist in distribuciones])

# Manejadores de errores para producción
@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f'Page not found: {request.url}')
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f'Server Error: {error}')
    return render_template('500.html'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f'Unhandled exception: {str(e)}')
    return render_template('500.html'), 500

# Middleware para agregar headers de seguridad básicos
@app.after_request
def add_security_headers_after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# Función para crear usuario administrador
def create_admin_user():
    try:
        # Verificar si ya existe un administrador
        admin = User.query.filter_by(role='admin').first()
        if admin:
            app.logger.info('Administrador ya existe')
            return
        
        # Crear usuario administrador por defecto
        admin = User(
            username='admin',
            email='admin@botfinanciero.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            nombre_completo='Administrador del Sistema',
            telefono='+1234567890',
            departamento='Administración',
            salario=0,
            fecha_contratacion=datetime.now(),
            permisos_especiales='all',
            is_active=True
        )
        
        db.session.add(admin)
        db.session.commit()
        app.logger.info('Usuario administrador creado exitosamente')
        
    except Exception as e:
        app.logger.error(f'Error creando administrador: {str(e)}')
        db.session.rollback()

# Función para inicializar la base de datos
def init_db():
    try:
        with app.app_context():
            db.create_all()
            create_admin_user()
            app.logger.info('Base de datos inicializada correctamente')
    except Exception as e:
        app.logger.error(f'Error inicializando base de datos: {str(e)}')

if __name__ == '__main__':
    # Inicializar base de datos
    init_db()
    
    # Ejecutar aplicación
    app.run(debug=True, host='0.0.0.0', port=5000)
