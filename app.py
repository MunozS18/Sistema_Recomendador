"""
SISTEMA RECOMENDADOR DE HOTELES - ARCHIVO PRINCIPAL
===================================================

Este archivo contiene la aplicación principal Flask que maneja:
- Autenticación y gestión de usuarios
- Rutas de la aplicación web
- API REST para hoteles y recomendaciones
- Panel de administración
- Gestión de historial y favoritos
- Sistema de valoraciones

AUTOR: Wilson Munoz Serrano
FECHA: 12-07-2025, mucho desvelo.....  Chicos lean el README, traté de comentar todo, espero y lo entiendan
tengan en cuenta que el archivo prueba.txt es el HTML de la pagina de Booking

Profe el sistema de Scrapping no puede extraer los comentarios, porque Booking bloquea el Scrapping, traté de que 
todo estuviera bien, espero y quede satisfecho con el trabajo, fueron noches sin dormir, sin vida social jajajaja.

VERSIÓN: Ultima jajaj, creo que ya estoy quedando loco
"""

# =============================================================================
# IMPORTS Y CONFIGURACIÓN INICIAL
# =============================================================================

# Flask y extensiones principales
from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify, abort
from scraper import scrape_booking_hotels
from config import Config

# Modelos de base de datos
from models import db, Usuario, PreferenciasUsuario, Valoraciones, Hoteles, InteraccionesUsuario
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

# Formularios
from forms import RegisterForm, LoginForm, PreferenciasForm, ScrapingForm

# Utilidades para recomendaciones
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Utilidades del sistema
from datetime import datetime, timedelta
import os
import json
import re
import unicodedata

# Configuración de Flask-Mail
from flask_wtf import CSRFProtect
import logging
import html
import click
import random
from models import CodigoVerificacion
from flask_mail import Mail, Message
from collections import defaultdict
import locale

# Configuración de localización para fechas en español
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8' if 'es_ES.UTF-8' in locale.locale_alias else '')

# =============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN FLASK
# =============================================================================

# Crear instancia de Flask
app = Flask(__name__)
app.config.from_object(Config)

# =============================================================================
# CONFIGURACIÓN DE CORREO ELECTRÓNICO
# =============================================================================
# Configuración para envío de correos (recuperación de contraseña, notificaciones)
# Este paso aun está en desarrollo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Tu correo
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Tu contraseña o app password
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])
mail = Mail(app)

# =============================================================================
# CONFIGURACIÓN DE SEGURIDAD
# =============================================================================
# Protección CSRF global para prevenir ataques Cross-Site Request Forgery
csrf = CSRFProtect(app)

# =============================================================================
# INICIALIZACIÓN DE EXTENSIONES
# =============================================================================

# Base de datos (Obviamente primero se debe crear la base de datos en el servidor de la nube y luego conectarla a la aplicación)
db.init_app(app)

# Encriptación de contraseñas (Se usa bcrypt para encriptar las contraseñas de los usuarios)
bcrypt = Bcrypt(app)

# Gestión de sesiones de usuario y autenticación (Flask-Login)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# =============================================================================
# VARIABLES GLOBALES
# =============================================================================
# Rutas de la aplicación web (de aquí se extraen las rutas de las páginas)
# Declaración de rutas de la aplicación web
SCRAPED_HOTELS_FILE = 'hoteles_scrapeados.json'
BOOKING_URL = "https://www.booking.com/"

# Crear todas las tablas de la base de datos al iniciar la aplicación
with app.app_context():
    db.create_all()

# =============================================================================
# FUNCIONES AUXILIARES DE USUARIO Y AUTENTICACIÓN
# =============================================================================

@login_manager.user_loader
def load_user(user_id):
    """
    Función para cargar un usuario desde la base de datos a partir de su ID
    Requerida por Flask-Login para gestionar sesiones de usuario
    """
    return Usuario.query.get(int(user_id))

def guardar_hoteles_scrapeados(hoteles):
    """
    Guarda los hoteles scrapeados en un archivo JSON (función legacy)
    Esta función se usa para almacenar temporalmente los datos scrapeados
    """
    with open(SCRAPED_HOTELS_FILE, 'w', encoding='utf-8') as f:
        json.dump(hoteles, f, ensure_ascii=False)

def cargar_hoteles_scrapeados():
    """
    Carga los hoteles desde el archivo JSON (función legacy)
    Lee los datos scrapeados guardados anteriormente
    """
    if os.path.exists(SCRAPED_HOTELS_FILE):
        with open(SCRAPED_HOTELS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# =============================================================================
# RUTAS PRINCIPALES DE LA APLICACIÓN
# =============================================================================

@app.route('/')
@login_required
def home():
    """
    PÁGINA PRINCIPAL - Dashboard del usuario
    
    Muestra:
    - Hoteles recomendados basados en preferencias del usuario
    - Redirección a configuración si el usuario no tiene preferencias
    - Mensaje de advertencia si no hay hoteles disponibles
    """
    # Verificar si el usuario tiene preferencias configuradas
    if not current_user.preferencias:
        return redirect(url_for('ajustes_usuario'))
    
    # Obtener todos los hoteles de la base de datos
    hoteles = Hoteles.query.all()
    if not hoteles:
        flash('No hay hoteles disponibles. El administrador debe ejecutar el scraping.', 'warning')
        return render_template('hoteles.html', recomendados=[], otros=[])
    
    # Enriquecer hoteles con valoraciones y comentarios
    hoteles_con_valoraciones = agregar_valoraciones_a_hoteles_db(hoteles)
    return render_template('hoteles.html', recomendados=hoteles_con_valoraciones, otros=[])

def agregar_valoraciones_a_hoteles_db(hoteles):
    """
    ENRIQUECE LOS DATOS DE HOTELES CON VALORACIONES Y COMENTARIOS
    
    Args:
        hoteles: Lista de objetos Hotel de la base de datos
    
    Returns:
        Lista de hoteles enriquecidos con:
        - valoracion_promedio: Promedio de todas las valoraciones
        - total_valoraciones: Número total de valoraciones
        - comentarios_recientes: Últimos 3 comentarios
    """
    hoteles_limpios = []
    for hotel in hoteles:
        # Busca valoraciones para este hotel
        valoraciones = Valoraciones.query.filter_by(id_hotel=hotel.id_hotel).all()
        if valoraciones:
            # Calcular promedio de valoraciones
            puntuaciones = [float(v.puntuacion) for v in valoraciones]
            hotel.valoracion_promedio = sum(puntuaciones) / len(puntuaciones)
            hotel.total_valoraciones = len(valoraciones)
            # Obtener comentarios recientes (maximo 3)
            comentarios = [v.comentario for v in valoraciones if v.comentario][:3]
            hotel.comentarios_recientes = comentarios
        else:
            # Hotel sin valoraciones
            hotel.valoracion_promedio = None
            hotel.total_valoraciones = 0
            hotel.comentarios_recientes = []
        hoteles_limpios.append(hotel)
    return hoteles_limpios

# =============================================================================
# SISTEMA DE AUTENTICACIÓN
# =============================================================================

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    """
    PÁGINA UNIFICADA DE AUTENTICACIÓN
    
    Maneja tanto el login como el registro en una sola página con pestañas.
    Características:
    - Formularios separados para login y registro
    - Validación de credenciales
    - Encriptación de contraseñas
    - Redirección automática según el caso
    """
    login_form = LoginForm(prefix='login')
    register_form = RegisterForm(prefix='register')
    active_tab = request.args.get('tab', 'login')
    
    # ===== PROCESAMIENTO DE LOGIN =====
    if login_form.validate_on_submit() and login_form.submit.data:
        # Buscar usuario por email
        user = Usuario.query.filter_by(email=login_form.email.data).first()
        
        # Verificar credenciales
        if user and bcrypt.check_password_hash(user.password_hash, login_form.contrasena.data):
            # Login exitoso
            login_user(user)
            user.ultimo_login = db.func.now()
            db.session.commit()
            flash('Bienvenido de nuevo.', 'success')
            return redirect(url_for('home'))
        else:
            # Credenciales incorrectas
            flash('Credenciales incorrectas.', 'danger')
        active_tab = 'login'
    
    # ===== PROCESAMIENTO DE REGISTRO =====
    elif register_form.validate_on_submit() and register_form.submit.data:
        # Encriptar contraseña
        hashed_pw = bcrypt.generate_password_hash(register_form.contrasena.data).decode('utf-8')
        
        # Crear nuevo usuario
        user = Usuario(nombre_usuario=register_form.nombre_usuario.data, email=register_form.email.data, password_hash=hashed_pw)
        
        # Guardar en base de datos
        db.session.add(user)
        db.session.commit()
        
        # Login automático después del registro
        login_user(user)
        flash('Registro exitoso. Completa tus preferencias.', 'success')
        return redirect(url_for('ajustes_usuario'))
        active_tab = 'register'
    
    return render_template('auth.html', login_form=login_form, register_form=register_form, active_tab=active_tab)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Redirección a la página de autenticación con pestaña de login
    """
    return redirect(url_for('auth', tab='login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Redirección a la página de autenticación con pestaña de registro
    """
    return redirect(url_for('auth', tab='register'))

@app.route('/logout')
@login_required
def logout():
    """
    CERRAR SESIÓN
    
    Cierra la sesión del usuario actual y redirige al login
    """
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('login'))

# =============================================================================
# PERFIL DE USUARIO
# =============================================================================

@app.route('/perfil')
@login_required
def perfil():
    """
    PÁGINA DE PERFIL DEL USUARIO
    
    Muestra:
    - Información personal del usuario
    - Preferencias configuradas
    - Historial de valoraciones
    - Interacciones recientes (vistas, favoritos)
    """
    preferencias = current_user.preferencias
    valoraciones = Valoraciones.query.filter_by(id_usuario=current_user.id_usuario).all()
    interacciones = InteraccionesUsuario.query.filter_by(id_usuario=current_user.id_usuario).all()
    hoteles_dict = {h.id_hotel: h for h in Hoteles.query.all()}
    return render_template('perfil.html', user=current_user, preferencias=preferencias, valoraciones=valoraciones, interacciones=interacciones, hoteles_dict=hoteles_dict)

@app.route('/perfil/borrar_historial', methods=['POST'])
@login_required
def borrar_historial_usuario():
    """
    BORRAR HISTORIAL COMPLETO DEL USUARIO
    
    Elimina todas las valoraciones e interacciones del usuario actual.
    Protegido para que el admin no pueda borrar su propio historial.
    """
    if current_user.email == 'admin@gmail.com':
        return redirect(url_for('perfil'))
    
    # Eliminar valoraciones
    Valoraciones.query.filter_by(id_usuario=current_user.id_usuario).delete()
    
    # Eliminar interacciones
    InteraccionesUsuario.query.filter_by(id_usuario=current_user.id_usuario).delete()
    
    db.session.commit()
    return redirect(url_for('perfil'))

# =============================================================================
# API REST PARA HOTELES
# =============================================================================

@app.route('/api/hotels')
def hotels():
    """
    API ENDPOINT: LISTA DE HOTELES
    
    Retorna todos los hoteles en formato JSON para consumo de frontend
    """
    hoteles = Hoteles.query.all()
    if not hoteles:
        return jsonify({'error': 'No hay hoteles disponibles. El administrador debe ejecutar el scraping.'}), 404
    
    data = [h.to_dict() for h in hoteles]
    return jsonify(data)

@app.route('/api/recomendaciones')
@login_required
def recomendaciones():
    """
    API ENDPOINT: RECOMENDACIONES PERSONALIZADAS
    
    Sistema de recomendación basado en:
    - Preferencias del usuario (estrellas, amenities, ubicación)
    - Historial de valoraciones (filtrado colaborativo)
    - Filtrado por criterios específicos
    
    Returns:
        JSON con hoteles recomendados ordenados por relevancia
    """
    hoteles = Hoteles.query.all()
    if not hoteles:
        return jsonify({'error': 'No hay hoteles disponibles. El administrador debe ejecutar el scraping.'}), 404
    
    # Obtener valoraciones para análisis colaborativo
    valoraciones = Valoraciones.query.all()
    if not valoraciones:
        # Sin valoraciones, mostrar hoteles aleatorios
        return jsonify([h.to_dict() for h in hoteles[:10]])
    
    # Crear matriz de valoraciones para análisis colaborativo
    data = [
        {'usuario': v.id_usuario, 'hotel': v.id_hotel, 'puntuacion': float(v.puntuacion)}
        for v in valoraciones
    ]
    
    import pandas as pd
    df = pd.DataFrame(data)
    matriz = df.pivot_table(index='usuario', columns='hotel', values='puntuacion')
    
    # Si el usuario no tiene valoraciones, usar filtrado por preferencias
    if current_user.id_usuario not in matriz.index:
        return jsonify([h.to_dict() for h in hoteles[:10]])
    
    # ===== FILTRADO POR PREFERENCIAS DEL USUARIO =====
    pref = current_user.preferencias
    hoteles_filtrados = hoteles
    
    if pref:
        # Filtrar por estrellas
        if pref.estrellas:
            estrellas = [e.strip() for e in (pref.estrellas.split(',') if isinstance(pref.estrellas, str) else pref.estrellas)]
            hoteles_filtrados = [h for h in hoteles_filtrados if str(h.stars_count) in estrellas]
        
        # Filtrar por rating mínimo
        if pref.rating_minimo:
            try:
                hoteles_filtrados = [h for h in hoteles_filtrados if (h.rating_score or 0) >= float(pref.rating_minimo)]
            except Exception:
                pass
        
        # Filtrar por amenities importantes
        if pref.amenities_importantes:
            def amenities_texts(h):
                if h.amenities:
                    return h.amenities.lower()
                return ""
            
            amenities_buscar = pref.amenities_importantes.lower().split(',')
            hoteles_filtrados = [h for h in hoteles_filtrados if any(amenity.strip() in amenities_texts(h) for amenity in amenities_buscar)]
    
    # Retornar hoteles filtrados
    return jsonify([h.to_dict() for h in hoteles_filtrados[:20]])

# =============================================================================
# SISTEMA DE VALORACIONES
# =============================================================================

@app.route('/api/valorar', methods=['POST'])
@login_required
def valorar_hotel():
    """
    API ENDPOINT: VALORAR HOTEL
    
    Permite a los usuarios valorar hoteles con puntuación y comentarios.
    Registra la valoración en la base de datos.
    """
    data = request.get_json()
    hotel_id = data.get('hotel_id')
    puntuacion = data.get('puntuacion')
    comentario = data.get('comentario', '')
    
    # Validar datos
    if not hotel_id or not puntuacion:
        return jsonify({'error': 'Datos incompletos'}), 400
    
    # Buscar hotel
    hotel = Hoteles.query.get(hotel_id)
    if not hotel:
        return jsonify({'error': 'Hotel no encontrado'}), 404
    
    # Crear valoración
    valoracion = Valoraciones(
        id_usuario=current_user.id_usuario,
        id_hotel=hotel.nombre,  # Usar nombre del hotel
        puntuacion=puntuacion,
        comentario=comentario,
        fecha_valoracion=datetime.now()
    )
    
    # Guardar en base de datos
    db.session.add(valoracion)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Valoración registrada exitosamente'})

# =============================================================================
# FUNCIONES DE ADMINISTRACIÓN
# =============================================================================

def is_admin():
    """
    Verifica si el usuario actual es administrador
    """
    return current_user.is_authenticated and current_user.es_admin

@app.route('/admin/ajustes', methods=['GET', 'POST'])
@login_required
def admin_ajustes():
    """
    PANEL DE ADMINISTRACIÓN - AJUSTES DEL SISTEMA
    
    Permite a los administradores:
    - Ejecutar scraping de hoteles
    - Configurar parámetros del sistema
    - Monitorear el estado del sistema
    """
    if not is_admin():
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('home'))
    
    scraping_form = ScrapingForm()
    
    if scraping_form.validate_on_submit():
        try:
            # Ejecutar scraping con parámetros del formulario
            resultado = scrape_booking_hotels(
                hotel_limit=scraping_form.hotel_limit.data,
                destino=scraping_form.destino.data,
                checkin=scraping_form.checkin.data,
                checkout=scraping_form.checkout.data
            )
            
            flash(f'Scraping completado. {len(resultado)} hoteles procesados.', 'success')
        except Exception as e:
            flash(f'Error durante el scraping: {str(e)}', 'danger')
    
    return render_template('admin_ajustes.html', formulario=scraping_form)

# =============================================================================
# CONFIGURACIÓN DE USUARIO
# =============================================================================

@app.route('/ajustes', methods=['GET', 'POST'])
@login_required
def ajustes_usuario():
    """
    PÁGINA DE CONFIGURACIÓN DE USUARIO
    
    Permite a los usuarios configurar sus preferencias para el sistema
    de recomendaciones. Incluye estrellas, amenities, ubicación, etc.
    """
    form = PreferenciasForm()
    
    # Cargar preferencias existentes
    if current_user.preferencias:
        form.estrellas.data = current_user.preferencias.estrellas
        form.rating_minimo.data = current_user.preferencias.rating_minimo
        form.amenities_importantes.data = current_user.preferencias.amenities_importantes
        form.ubicacion_preferida.data = current_user.preferencias.ubicacion_preferida
        form.presupuesto.data = current_user.preferencias.presupuesto
        form.tipo_viaje.data = current_user.preferencias.tipo_viaje
    
    if form.validate_on_submit():
        # Crear o actualizar preferencias
        if not current_user.preferencias:
            preferencias = PreferenciasUsuario(
                id_usuario=current_user.id_usuario,
                fecha_actualizacion=datetime.now()
            )
            db.session.add(preferencias)
        else:
            preferencias = current_user.preferencias
            preferencias.fecha_actualizacion = datetime.now()
        
        # Actualizar campos
        preferencias.estrellas = form.estrellas.data
        preferencias.rating_minimo = form.rating_minimo.data
        preferencias.amenities_importantes = form.amenities_importantes.data
        preferencias.ubicacion_preferida = form.ubicacion_preferida.data
        preferencias.presupuesto = form.presupuesto.data
        preferencias.tipo_viaje = form.tipo_viaje.data
        
        db.session.commit()
        flash('Preferencias guardadas exitosamente.', 'success')
        return redirect(url_for('home'))
    
    return render_template('ajustes_usuario.html', form=form)

# =============================================================================
# GESTIÓN DE HISTORIAL
# =============================================================================

@app.route('/historial')
@login_required
def historial():
    """
    PÁGINA DE HISTORIAL DEL USUARIO
    
    Muestra un timeline de todas las interacciones del usuario:
    - Hoteles visitados
    - Hoteles marcados como favoritos
    - Valoraciones realizadas
    """
    # Unificar eventos de historial: visitados y favoritos
    interacciones = InteraccionesUsuario.query.filter_by(
        id_usuario=current_user.id_usuario
    ).order_by(InteraccionesUsuario.fecha_interaccion.desc()).all()
    
    # Agrupar por fecha
    eventos_por_fecha = defaultdict(list)
    for interaccion in interacciones:
        fecha = interaccion.fecha_interaccion.strftime('%Y-%m-%d')
        eventos_por_fecha[fecha].append(interaccion)
    
    # Obtener información de hoteles
    hoteles_dict = {h.id_hotel: h for h in Hoteles.query.all()}
    
    return render_template('historial.html', 
                         eventos_por_fecha=eventos_por_fecha,
                         hoteles_dict=hoteles_dict)

@app.route('/historial/borrar_visto/<int:hotel_id>', methods=['POST'])
@login_required
def borrar_visto(hotel_id):
    """
    BORRAR EVENTO DE VISTA DEL HISTORIAL
    """
    InteraccionesUsuario.query.filter_by(
        id_usuario=current_user.id_usuario,
        id_hotel=hotel_id,
        tipo_interaccion='vista'
    ).delete()
    db.session.commit()
    return redirect(url_for('historial'))

@app.route('/historial/borrar_favorito/<int:hotel_id>', methods=['POST'])
@login_required
def borrar_favorito_historial(hotel_id):
    """
    BORRAR EVENTO DE FAVORITO DEL HISTORIAL
    """
    InteraccionesUsuario.query.filter_by(
        id_usuario=current_user.id_usuario,
        id_hotel=hotel_id,
        tipo_interaccion='favorito'
    ).delete()
    db.session.commit()
    return redirect(url_for('historial'))

@app.route('/historial/borrar_evento/<int:id_interaccion>', methods=['POST'])
@login_required
def borrar_evento_historial(id_interaccion):
    """
    BORRAR EVENTO ESPECÍFICO DEL HISTORIAL
    """
    interaccion = InteraccionesUsuario.query.get(id_interaccion)
    if interaccion and interaccion.id_usuario == current_user.id_usuario:
        db.session.delete(interaccion)
        db.session.commit()
    return redirect(url_for('historial'))

@app.route('/historial/borrar_todo', methods=['POST'])
@login_required
def borrar_historial_completo():
    """
    BORRAR TODO EL HISTORIAL DEL USUARIO
    """
    InteraccionesUsuario.query.filter_by(id_usuario=current_user.id_usuario).delete()
    db.session.commit()
    flash('Historial borrado completamente.', 'success')
    return redirect(url_for('historial'))

# =============================================================================
# PANEL DE ADMINISTRACIÓN
# =============================================================================

@app.route('/admin/usuarios')
@login_required
def admin_usuarios():
    """
    PANEL DE ADMINISTRACIÓN - GESTIÓN DE USUARIOS
    
    Lista todos los usuarios del sistema para administración.
    Solo accesible por administradores.
    """
    if not is_admin():
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('home'))
    
    usuarios = Usuario.query.all()
    return render_template('admin_usuarios.html', usuarios=usuarios)

@app.route('/admin/usuario/<int:user_id>/detalle')
@login_required
def admin_usuario_detalle(user_id):
    """
    DETALLE DE USUARIO PARA ADMINISTRADORES
    
    Muestra información detallada de un usuario específico:
    - Datos personales
    - Preferencias
    - Historial de actividad
    - Valoraciones realizadas
    """
    if not is_admin():
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('home'))
    
    usuario = Usuario.query.get_or_404(user_id)
    preferencias = usuario.preferencias
    valoraciones = Valoraciones.query.filter_by(id_usuario=user_id).all()
    interacciones = InteraccionesUsuario.query.filter_by(id_usuario=user_id).all()
    
    # Obtener información de hoteles
    hoteles_dict = {h.id_hotel: h for h in Hoteles.query.all()}
    
    return render_template('admin_usuario_detalle.html',
                         usuario=usuario,
                         preferencias=preferencias,
                         valoraciones=valoraciones,
                         interacciones=interacciones,
                         hoteles_dict=hoteles_dict)

@app.route('/admin/usuario/<int:user_id>/borrar_historial', methods=['POST'])
@login_required
def admin_borrar_historial_usuario(user_id):
    """
    BORRAR HISTORIAL DE USUARIO (ADMIN)
    """
    if not is_admin():
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('admin_usuarios'))
    
    # Eliminar valoraciones
    Valoraciones.query.filter_by(id_usuario=user_id).delete()
    
    # Eliminar interacciones
    InteraccionesUsuario.query.filter_by(id_usuario=user_id).delete()
    
    db.session.commit()
    flash('Historial del usuario borrado exitosamente.', 'success')
    return redirect(url_for('admin_usuario_detalle', user_id=user_id))

@app.route('/admin/usuario/<int:user_id>/eliminar', methods=['POST'])
@login_required
def admin_usuario_eliminar(user_id):
    """
    ELIMINAR USUARIO (ADMIN)
    """
    if not is_admin():
        flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
        return redirect(url_for('admin_usuarios'))
    
    usuario = Usuario.query.get_or_404(user_id)
    
    # No permitir eliminar al admin principal
    if usuario.email == 'admin@gmail.com':
        flash('No se puede eliminar al administrador principal.', 'danger')
        return redirect(url_for('admin_usuario_detalle', user_id=user_id))
    
    # Eliminar preferencias
    if usuario.preferencias:
        db.session.delete(usuario.preferencias)
    
    # Eliminar valoraciones
    Valoraciones.query.filter_by(id_usuario=user_id).delete()
    
    # Eliminar interacciones
    InteraccionesUsuario.query.filter_by(id_usuario=user_id).delete()
    
    # Eliminar usuario
    db.session.delete(usuario)
    db.session.commit()
    
    flash('Usuario eliminado exitosamente.', 'success')
    return redirect(url_for('admin_usuarios'))

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def slugify(value):
    """
    Convierte un string en un slug para URLs amigables
    Ejemplo: "Hotel Cartagena" -> "hotel-cartagena"
    """
    value = unicodedata.normalize('NFD', value).encode('ascii', 'ignore').decode('utf-8')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    return value

# =============================================================================
# RUTAS DE HOTELES
# =============================================================================

@app.route('/hotel/<slug>')
def hotel_detalle(slug):
    """
    PÁGINA DE DETALLE DE HOTEL
    
    Muestra información completa de un hotel específico:
    - Datos básicos (nombre, ubicación, precio)
    - Amenities y características
    - Imágenes y galería
    - Reviews y valoraciones
    - Formulario para valorar
    """
    hotel = Hoteles.query.filter_by(slug=slug).first_or_404()
    
    # Registrar vista si el usuario está autenticado
    if current_user.is_authenticated:
        vista = InteraccionesUsuario(
            id_usuario=current_user.id_usuario,
            id_hotel=hotel.id_hotel,
            tipo_interaccion='vista',
            valor=1.0,
            fecha_interaccion=datetime.now()
        )
        db.session.add(vista)
        db.session.commit()
    
    return render_template('hotel_detalle.html', hotel=hotel)

@app.route('/opinar/<nombre>', methods=['POST'])
@login_required
def opinar(nombre):
    """
    VALORAR HOTEL DESDE LA PÁGINA DE DETALLE
    
    Permite a los usuarios valorar hoteles directamente desde la página
    de detalle del hotel.
    """
    hotel = Hoteles.query.filter_by(nombre=nombre).first_or_404()
    puntuacion = request.form.get('puntuacion', type=float)
    comentario = request.form.get('comentario', '')
    
    if not puntuacion:
        flash('Debes proporcionar una puntuación.', 'danger')
        return redirect(url_for('hotel_detalle', slug=hotel.slug))
    
    # Crear valoración
    valoracion = Valoraciones(
        id_usuario=current_user.id_usuario,
        id_hotel=hotel.nombre,
        puntuacion=puntuacion,
        comentario=comentario,
        fecha_valoracion=datetime.now()
    )
    
    db.session.add(valoracion)
    db.session.commit()
    
    flash('Valoración registrada exitosamente.', 'success')
    return redirect(url_for('hotel_detalle', slug=hotel.slug))

@app.route('/hotel/<slug>/favorito', methods=['POST'])
@login_required
def marcar_favorito(slug):
    """
    MARCAR/DESMARCAR HOTEL COMO FAVORITO
    
    Permite a los usuarios marcar hoteles como favoritos o quitar
    la marca de favorito.
    """
    hotel = Hoteles.query.filter_by(slug=slug).first_or_404()
    accion = request.form.get('accion', 'marcar')
    
    # Buscar favorito existente
    favorito_existente = InteraccionesUsuario.query.filter_by(
        id_usuario=current_user.id_usuario,
        id_hotel=hotel.id_hotel,
        tipo_interaccion='favorito'
    ).first()
    
    if accion == 'marcar' and not favorito_existente:
        # Marcar como favorito
        favorito = InteraccionesUsuario(
            id_usuario=current_user.id_usuario,
            id_hotel=hotel.id_hotel,
            tipo_interaccion='favorito',
            valor=1.0,
            fecha_interaccion=datetime.now()
        )
        db.session.add(favorito)
        flash('Hotel marcado como favorito.', 'success')
    elif accion == 'desmarcar' and favorito_existente:
        # Quitar de favoritos
        db.session.delete(favorito_existente)
        flash('Hotel quitado de favoritos.', 'info')
    
    db.session.commit()
    return redirect(url_for('hotel_detalle', slug=slug))

@app.route('/favoritos')
@login_required
def favoritos():
    """
    PÁGINA DE FAVORITOS DEL USUARIO
    
    Muestra todos los hoteles marcados como favoritos por el usuario.
    """
    # Obtener favoritos del usuario
    favoritos = InteraccionesUsuario.query.filter_by(
        id_usuario=current_user.id_usuario,
        tipo_interaccion='favorito'
    ).all()
    
    # Obtener información de hoteles
    hoteles_favoritos = []
    for favorito in favoritos:
        hotel = Hoteles.query.get(favorito.id_hotel)
        if hotel:
            hoteles_favoritos.append(hotel)
    
    return render_template('favoritos.html', hoteles=hoteles_favoritos)

@app.route('/hoteles')
@login_required
def hoteles():
    """
    PÁGINA DE LISTA DE HOTELES
    
    Muestra todos los hoteles disponibles en el sistema.
    """
    hoteles = Hoteles.query.all()
    return render_template('hoteles.html', hoteles=hoteles)

@app.route('/gestion_cuenta')
@login_required
def gestion_cuenta():
    """
    PÁGINA DE GESTIÓN DE CUENTA
    
    Permite a los usuarios gestionar su cuenta y configuración.
    """
    return render_template('gestion_cuenta.html')

# =============================================================================
# CONFIGURACIÓN DE SEGURIDAD
# =============================================================================

@app.before_request
def before_request_https():
    """
    Forzar HTTPS en producción para mayor seguridad
    """
    if not app.debug and not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

# =============================================================================
# COMANDOS CLI
# =============================================================================

@app.cli.command('crear_admin')
@click.option('--email', prompt='Email del admin', default='admin@gmail.com')
@click.option('--password', prompt='Contraseña', hide_input=True, confirmation_prompt=True)
def crear_admin(email, password):
    """
    COMANDO CLI: CREAR USUARIO ADMINISTRADOR
    
    Crea un usuario con privilegios de administrador en el sistema.
    Se puede ejecutar desde la línea de comandos con Flask CLI.
    
    Uso:
        flask crear-admin --email admin@gmail.com --password admin123
    """
    # Verificar si el usuario ya existe
    existing_user = Usuario.query.filter_by(email=email).first()
    if existing_user:
        click.echo(f'El usuario {email} ya existe.')
        return
    
    # Encriptar contraseña
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Crear usuario administrador
    admin_user = Usuario(
        nombre_usuario='Administrador',
        email=email,
        password_hash=hashed_password,
        es_admin=True,
        fecha_registro=datetime.now()
    )
    
    # Guardar en base de datos
    db.session.add(admin_user)
    db.session.commit()
    
    click.echo(f'Usuario administrador creado exitosamente: {email}')

# =============================================================================
# SISTEMA DE RECUPERACIÓN DE CONTRASEÑA
# =============================================================================

@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    """
    PÁGINA DE RECUPERACIÓN DE CONTRASEÑA
    
    Permite a los usuarios solicitar la recuperación de su contraseña
    mediante envío de código por email.
    """
    if request.method == 'POST':
        email = request.form.get('email')
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario:
            # Generar código de verificación
            codigo = ''.join(random.choices('0123456789', k=6))
            
            # Crear registro de código
            codigo_verificacion = CodigoVerificacion(
                id_usuario=usuario.id_usuario,
                canal='email',
                codigo=codigo,
                expiracion=datetime.now() + timedelta(minutes=15),
                usado=False,
                fecha_envio=datetime.now()
            )
            
            db.session.add(codigo_verificacion)
            db.session.commit()
            
            # Enviar email (implementación pendiente)
            # msg = Message('Recuperación de Contraseña', recipients=[email])
            # msg.body = f'Tu código de verificación es: {codigo}'
            # mail.send(msg)
            
            flash('Se ha enviado un código de verificación a tu email.', 'success')
            return redirect(url_for('verificar_codigo', user_id=usuario.id_usuario))
        else:
            flash('No se encontró un usuario con ese email.', 'danger')
    
    return render_template('recuperar.html')

@app.route('/verificar_codigo/<int:user_id>', methods=['GET', 'POST'])
def verificar_codigo(user_id):
    """
    VERIFICACIÓN DE CÓDIGO DE RECUPERACIÓN
    
    Permite a los usuarios verificar el código enviado por email
    para proceder con la recuperación de contraseña.
    """
    if request.method == 'POST':
        codigo_ingresado = request.form.get('codigo')
        
        # Buscar código válido
        codigo_verificacion = CodigoVerificacion.query.filter_by(
            id_usuario=user_id,
            codigo=codigo_ingresado,
            usado=False
        ).first()
        
        if codigo_verificacion and codigo_verificacion.expiracion > datetime.now():
            # Marcar código como usado
            codigo_verificacion.usado = True
            db.session.commit()
            
            return redirect(url_for('restablecer_contrasena', user_id=user_id))
        else:
            flash('Código inválido o expirado.', 'danger')
    
    return render_template('verificar_codigo.html')

@app.route('/restablecer_contrasena/<int:user_id>', methods=['GET', 'POST'])
def restablecer_contrasena(user_id):
    """
    RESTABLECER CONTRASEÑA
    
    Permite a los usuarios establecer una nueva contraseña
    después de verificar el código de recuperación.
    """
    if request.method == 'POST':
        nueva_contrasena = request.form.get('nueva_contrasena')
        confirmar_contrasena = request.form.get('confirmar_contrasena')
        
        if nueva_contrasena == confirmar_contrasena:
            # Actualizar contraseña
            usuario = Usuario.query.get(user_id)
            usuario.password_hash = bcrypt.generate_password_hash(nueva_contrasena).decode('utf-8')
            db.session.commit()
            
            flash('Contraseña actualizada exitosamente.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Las contraseñas no coinciden.', 'danger')
    
    return render_template('restablecer_contrasena.html') 

if __name__ == '__main__':
    app.run(debug=True)