"""
MODELOS DE BASE DE DATOS - SISTEMA RECOMENDADOR DE HOTELES
==========================================================

Este archivo define todos los modelos de base de datos usando SQLAlchemy.
Cada modelo representa una tabla en la base de datos y define las relaciones
entre las diferentes entidades del sistema.

ESTRUCTURA DE LA BASE DE DATOS:
- Usuario: Información de usuarios del sistema
- Hoteles: Datos de hoteles scrapeados
- Valoraciones: Opiniones de usuarios sobre hoteles
- InteraccionesUsuario: Historial de vistas y favoritos
- PreferenciasUsuario: Preferencias personalizadas de cada usuario
- ReviewsScraping: Reviews scrapeados de sitios externos
- CodigoVerificacion: Códigos para recuperación de contraseña

AUTOR: Wilson Munoz Serrano
FECHA: 1 mes jajaja y mucho desvelo
VERSIÓN: 2.0
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

# Instancia de SQLAlchemy para manejar la base de datos
db = SQLAlchemy()

# =============================================================================
# MODELO HOTELES - TABLA PRINCIPAL DE HOTELES
# =============================================================================

class Hoteles(db.Model):
    """
    MODELO HOTELES
    
    Almacena toda la información de los hoteles scrapeados de diferentes fuentes.
    Incluye datos básicos, precios, ratings, amenities, imágenes y metadatos.
    
    RELACIONES:
    - Uno a muchos con Valoraciones (a través de id_hotel)
    - Uno a muchos con InteraccionesUsuario (a través de id_hotel)
    """
    __tablename__ = 'hoteles'
    
    # ===== CAMPOS PRINCIPALES =====
    id_hotel = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)  # URL amigable
    
    # ===== INFORMACIÓN BÁSICA =====
    descripcion = db.Column(db.Text)
    ubicacion = db.Column(db.String(255))
    
    # ===== INFORMACIÓN DE PRECIOS =====
    precio_amount = db.Column(db.Integer)  # Precio en números
    precio_currency = db.Column(db.String(10), default='COP')  # Moneda
    precio_formatted = db.Column(db.String(50))  # Precio formateado
    precio_source = db.Column(db.String(50))  # Fuente del precio
    
    # ===== INFORMACIÓN DE RATINGS =====
    rating_score = db.Column(db.Float)  # Puntuación numérica
    rating_max_score = db.Column(db.Integer, default=10)  # Puntuación máxima
    rating_formatted = db.Column(db.String(20))  # Rating formateado
    
    # ===== INFORMACIÓN DE ESTRELLAS =====
    stars_count = db.Column(db.Integer)  # Número de estrellas
    stars_formatted = db.Column(db.String(20))  # Estrellas formateadas
    
    # ===== INFORMACIÓN DE REVIEWS =====
    reviews_count = db.Column(db.Integer, default=0)  # Número de reviews
    
    # ===== AMENITIES Y CARACTERÍSTICAS =====
    amenities = db.Column(db.Text)  # Amenities procesadas
    amenities_raw = db.Column(db.Text)  # Amenities originales
    
    # ===== INFORMACIÓN VISUAL =====
    imagen_url = db.Column(db.String(512))  # Imagen principal
    imagenes = db.Column(db.Text)  # Lista de imágenes en JSON
    
    # ===== REVIEWS Y COMENTARIOS =====
    reviews = db.Column(db.Text)  # Reviews en formato JSON
    reviews_summary = db.Column(db.String(255))  # Resumen de reviews
    
    # ===== INFORMACIÓN DE CONTACTO =====
    telefono = db.Column(db.String(50))
    email = db.Column(db.String(120))
    website = db.Column(db.String(255))
    
    # ===== INFORMACIÓN GEOGRÁFICA =====
    latitud = db.Column(db.Float)
    longitud = db.Column(db.Float)
    
    # ===== ENLACES EXTERNOS =====
    link_booking = db.Column(db.String(512))  # Enlace a Booking.com
    link_trivago = db.Column(db.String(512))  # Enlace a Trivago
    
    # ===== METADATOS DE SCRAPING =====
    fuente_principal = db.Column(db.String(50), default='booking')  # Fuente principal
    fecha_scraping = db.Column(db.DateTime)  # Fecha del scraping
    version_scraping = db.Column(db.String(20), default='2.0')  # Versión del scraper
    metadata_scraping = db.Column(db.Text)  # Metadatos adicionales
    
    # ===== CAMPOS LEGACY Y COMPATIBILIDAD =====
    rating = db.Column(db.Float)  # Rating legacy
    precio_promedio = db.Column(db.Integer)  # Precio promedio
    imagen_url_legacy = db.Column(db.String(512))  # URL de imagen legacy
    fuente = db.Column(db.String(50))  # Fuente legacy
    
    # ===== PUNTUACIONES DETALLADAS =====
    puntuacion_personal = db.Column(db.Float, default=0)
    puntuacion_instalaciones = db.Column(db.Float, default=0)
    puntuacion_limpieza = db.Column(db.Float, default=0)
    puntuacion_confort = db.Column(db.Float, default=0)
    puntuacion_calidad_precio = db.Column(db.Float, default=0)
    puntuacion_ubicacion = db.Column(db.Float, default=0)
    
    # ===== TIMESTAMPS =====
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    
    # ===== MÉTODOS AUXILIARES =====
    
    def valoraciones(self):
        """
        Obtiene las valoraciones asociadas a este hotel
        
        Returns:
            Lista de objetos Valoraciones para este hotel
        """
        return Valoraciones.query.filter_by(id_hotel=self.nombre).all()
    
    def to_dict(self):
        """
        Convierte el objeto hotel a un diccionario para API JSON
        
        Returns:
            Diccionario con todos los datos del hotel formateados
        """
        # Procesar amenities
        amenities = self.amenities
        if amenities:
            if isinstance(amenities, str) and amenities.strip().startswith('['):
                try:
                    amenities = json.loads(amenities)
                except Exception:
                    pass
        
        # Procesar imágenes
        images = []
        if self.imagenes:
            try:
                images = json.loads(self.imagenes)
            except Exception:
                images = []
        
        # Procesar reviews
        todas_opiniones = []
        if self.reviews:
            try:
                todas_opiniones = json.loads(self.reviews)
            except Exception:
                todas_opiniones = []
        
        # Agregar opiniones de usuario si existen
        if hasattr(self, 'opiniones_usuario') and self.opiniones_usuario:
            todas_opiniones += [op.get('comentario', '') for op in self.opiniones_usuario if isinstance(op, dict)]
        
        return {
            'id': self.id_hotel,
            'name': self.nombre or '',
            'slug': self.slug or '',
            'description': self.descripcion or '',
            'location': self.ubicacion or '',
            'price': self.precio_formatted or '',
            'stars': self.stars_formatted or '',
            'stars_count': self.stars_count or 0,
            'image': self.imagen_url or '',
            'images': images,
            'rating': self.rating_formatted or '',
            'rating_score': self.rating_score,
            'rating_max_score': self.rating_max_score or 10,
            'amenities': amenities,
            'reviews': todas_opiniones,
            'todas_opiniones': todas_opiniones,
            'link': self.link_booking or '',
            'fuente_principal': self.fuente_principal or '',
        }
    
    def get_amenities_list(self):
        """
        Obtiene la lista de amenities como una lista de strings
        
        Returns:
            Lista de amenities separadas por comas
        """
        if self.amenities:
            return [a.strip() for a in self.amenities.split(',')]
        return []
    
    def get_reviews_list(self):
        """
        Obtiene la lista de reviews como una lista de diccionarios
        
        Returns:
            Lista de reviews en formato JSON
        """
        if self.reviews:
            try:
                return json.loads(self.reviews)
            except Exception:
                return []
        return []

# =============================================================================
# MODELO VALORACIONES - OPINIONES DE USUARIOS
# =============================================================================

class Valoraciones(db.Model):
    """
    MODELO VALORACIONES
    
    Almacena las opiniones y valoraciones que los usuarios hacen sobre los hoteles.
    Permite el sistema de recomendación colaborativo.
    
    RELACIONES:
    - Muchos a uno con Usuario (a través de id_usuario)
    - Muchos a uno con Hoteles (a través de id_hotel)
    """
    __tablename__ = 'valoraciones'
    
    id_valoracion = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False, index=True)
    id_hotel = db.Column(db.String(255), nullable=False)  # Nombre del hotel del scraping
    puntuacion = db.Column(db.Float, nullable=False)  # Puntuación de 1 a 10
    comentario = db.Column(db.Text)  # Comentario opcional
    fecha_valoracion = db.Column(db.DateTime)  # Fecha de la valoración

# =============================================================================
# MODELO INTERACCIONES USUARIO - HISTORIAL DE ACTIVIDAD
# =============================================================================

class InteraccionesUsuario(db.Model):
    """
    MODELO INTERACCIONES USUARIO
    
    Registra todas las interacciones del usuario con los hoteles:
    - Vistas: Cuando un usuario ve un hotel
    - Valoraciones: Cuando un usuario valora un hotel
    - Favoritos: Cuando un usuario marca un hotel como favorito
    
    RELACIONES:
    - Muchos a uno con Usuario (a través de id_usuario)
    - Muchos a uno con Hoteles (a través de id_hotel)
    """
    __tablename__ = 'interacciones_usuario'
    
    id_interaccion = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False, index=True)
    id_hotel = db.Column(db.Integer, db.ForeignKey('hoteles.id_hotel'), nullable=False, index=True)
    tipo_interaccion = db.Column(db.Enum('vista', 'valoracion', 'favorito'), nullable=False, index=True)
    valor = db.Column(db.Numeric(3,2), nullable=False)  # Valor numérico de la interacción
    fecha_interaccion = db.Column(db.DateTime)  # Fecha y hora de la interacción

# =============================================================================
# MODELO PREFERENCIAS USUARIO - CONFIGURACIÓN PERSONAL
# =============================================================================

class PreferenciasUsuario(db.Model):
    """
    MODELO PREFERENCIAS USUARIO
    
    Almacena las preferencias personalizadas de cada usuario para el sistema
    de recomendación. Incluye criterios como estrellas, ubicación, amenities, etc.
    
    RELACIONES:
    - Uno a uno con Usuario (a través de id_usuario)
    """
    __tablename__ = 'preferencias_usuario'
    
    id_preferencias = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False, unique=True)
    
    # ===== PREFERENCIAS DE VIAJE =====
    tipo_viaje = db.Column(db.String(50))  # Negocios, turismo, familiar, etc.
    presupuesto = db.Column(db.String(20))  # Rango de presupuesto
    ubicacion_preferida = db.Column(db.String(100))  # Zona preferida
    
    # ===== PREFERENCIAS DE HOTEL =====
    amenities_importantes = db.Column(db.Text)  # Amenities prioritarias
    rating_minimo = db.Column(db.Float, default=0)  # Rating mínimo aceptable
    estrellas = db.Column(db.String(50))  # Estrellas preferidas (ej: "3,4,5")
    
    # ===== METADATOS =====
    fecha_actualizacion = db.Column(db.DateTime)  # Última actualización
    
    # ===== RELACIÓN CON USUARIO =====
    usuario = db.relationship('Usuario', back_populates='preferencias', uselist=False)

# =============================================================================
# MODELO USUARIO - USUARIOS DEL SISTEMA
# =============================================================================

class Usuario(UserMixin, db.Model):
    """
    MODELO USUARIO
    
    Almacena la información de todos los usuarios del sistema.
    Hereda de UserMixin para compatibilidad con Flask-Login.
    
    RELACIONES:
    - Uno a uno con PreferenciasUsuario
    - Uno a muchos con Valoraciones
    - Uno a muchos con InteraccionesUsuario
    """
    __tablename__ = 'usuario'
    
    # ===== CAMPOS PRINCIPALES =====
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)  # Contraseña encriptada
    
    # ===== METADATOS DE USUARIO =====
    fecha_registro = db.Column(db.DateTime)  # Fecha de registro
    ultimo_login = db.Column(db.DateTime)  # Último acceso
    es_admin = db.Column(db.Boolean, default=False)  # Rol de administrador
    avatar_url = db.Column(db.String(255), default=None)  # URL del avatar
    
    # ===== RELACIONES =====
    preferencias = db.relationship('PreferenciasUsuario', back_populates='usuario', uselist=False)
    valoraciones = db.relationship('Valoraciones', backref='usuario', lazy=True)
    interacciones = db.relationship('InteraccionesUsuario', backref='usuario', lazy=True)
    
    # ===== MÉTODOS REQUERIDOS POR FLASK-LOGIN =====
    def get_id(self):
        """Retorna el ID del usuario como string (requerido por Flask-Login)"""
        return str(self.id_usuario)
    
    @property
    def id(self):
        """Propiedad para compatibilidad con Flask-Login"""
        return self.id_usuario
    
    @property
    def nombre(self):
        """Propiedad para obtener el nombre de usuario"""
        return self.nombre_usuario

# =============================================================================
# MODELO REVIEWS SCRAPING - REVIEWS EXTERNOS
# =============================================================================

class ReviewsScraping(db.Model):
    """
    MODELO REVIEWS SCRAPING
    
    Almacena reviews scrapeados de sitios externos como Booking.com, Trivago, etc.
    Permite enriquecer la información de los hoteles con opiniones reales.
    
    RELACIONES:
    - Muchos a uno con Hoteles (a través de id_hotel)
    """
    __tablename__ = 'reviews_scraping'
    
    id_review = db.Column(db.Integer, primary_key=True)
    id_hotel = db.Column(db.Integer, db.ForeignKey('hoteles.id_hotel'), nullable=False)
    puntuacion = db.Column(db.Numeric(3,2), nullable=False)  # Puntuación del review
    comentario = db.Column(db.Text)  # Comentario del review
    fecha_review = db.Column(db.Date)  # Fecha del review original
    fuente = db.Column(db.String(50))  # Fuente del review (booking, trivago, etc.)
    fecha_scraping = db.Column(db.DateTime)  # Fecha cuando se scrapeó

# =============================================================================
# MODELO CÓDIGO VERIFICACIÓN - RECUPERACIÓN DE CONTRASEÑA
# =============================================================================

class CodigoVerificacion(db.Model):
    """
    MODELO CÓDIGO VERIFICACIÓN
    
    Almacena códigos de verificación para recuperación de contraseña.
    Los códigos tienen tiempo de expiración y solo pueden usarse una vez.
    
    RELACIONES:
    - Muchos a uno con Usuario (a través de id_usuario)
    """
    __tablename__ = 'codigo_verificacion'
    
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    canal = db.Column(db.String(20), nullable=False)  # email, sms, whatsapp
    codigo = db.Column(db.String(10), nullable=False)  # Código de verificación
    expiracion = db.Column(db.DateTime, nullable=False)  # Fecha de expiración
    usado = db.Column(db.Boolean, default=False)  # Si ya fue usado
    fecha_envio = db.Column(db.DateTime, nullable=False) 