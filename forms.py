"""
FORMULARIOS DEL SISTEMA - SISTEMA RECOMENDADOR DE HOTELES
========================================================

Este archivo contiene todos los formularios del sistema usando Flask-WTF.
Cada formulario define los campos, validaciones y comportamiento específico
para diferentes funcionalidades del sistema.

FORMULARIOS INCLUIDOS:
- RegisterForm: Registro de nuevos usuarios
- LoginForm: Inicio de sesión
- PreferenciasForm: Configuración de preferencias de usuario
- ScrapingForm: Configuración de scraping para administradores

CARACTERÍSTICAS:
- Validación automática de campos
- Mensajes de error personalizados
- Protección CSRF integrada
- Campos con prefijos para formularios múltiples

AUTOR: Wilson Munoz Serrano
FECHA: 1 mes jajaja y mucho desvelo
VERSIÓN: 2.0
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, IntegerField, DateField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, NumberRange
from wtforms.widgets import TextArea
import re

# =============================================================================
# VALIDACIONES PERSONALIZADAS
# =============================================================================

def validate_password_strength(form, field):
    """
    VALIDACIÓN DE FORTALEZA DE CONTRASEÑA
    
    Verifica que la contraseña cumpla con los requisitos de seguridad:
    - Mínimo 8 caracteres
    - Al menos una letra mayúscula
    - Al menos una letra minúscula
    - Al menos un número
    - Al menos un carácter especial
    
    Args:
        form: Formulario que contiene el campo
        field: Campo de contraseña a validar
        
    Raises:
        ValidationError: Si la contraseña no cumple los requisitos
    """
    password = field.data
    
    if len(password) < 8:
        raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError('La contraseña debe contener al menos una letra mayúscula.')
    
    if not re.search(r'[a-z]', password):
        raise ValidationError('La contraseña debe contener al menos una letra minúscula.')
    
    if not re.search(r'\d', password):
        raise ValidationError('La contraseña debe contener al menos un número.')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('La contraseña debe contener al menos un carácter especial.')

def validate_email_format(form, field):
    """
    VALIDACIÓN DE FORMATO DE EMAIL
    
    Verifica que el email tenga un formato válido y no contenga caracteres
    problemáticos.
    
    Args:
        form: Formulario que contiene el campo
        field: Campo de email a validar
        
    Raises:
        ValidationError: Si el email no tiene formato válido
    """
    email = field.data
    
    # Verificar formato básico de email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValidationError('Por favor ingresa un email válido.')
    
    # Verificar que no contenga caracteres problemáticos
    if any(char in email for char in ['<', '>', '"', "'", ';', '(', ')']):
        raise ValidationError('El email no puede contener caracteres especiales.')

def validate_username_format(form, field):
    """
    VALIDACIÓN DE FORMATO DE NOMBRE DE USUARIO
    
    Verifica que el nombre de usuario cumpla con los requisitos:
    - Solo letras, números y guiones bajos
    - Entre 3 y 20 caracteres
    - No puede empezar con número
    
    Args:
        form: Formulario que contiene el campo
        field: Campo de nombre de usuario a validar
        
    Raises:
        ValidationError: Si el nombre de usuario no cumple los requisitos
    """
    username = field.data
    
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]{2,19}$', username):
        raise ValidationError('El nombre de usuario debe tener entre 3 y 20 caracteres, '
                           'solo letras, números y guiones bajos, y no puede empezar con número.')

# =============================================================================
# FORMULARIO DE REGISTRO
# =============================================================================

class RegisterForm(FlaskForm):
    """
    FORMULARIO DE REGISTRO DE USUARIO
    
    Permite a los usuarios crear una nueva cuenta en el sistema.
    Incluye validaciones de seguridad y formato.
    
    CAMPOS:
    - nombre_usuario: Nombre de usuario único
    - email: Email válido y único
    - contrasena: Contraseña segura
    - confirmar_contrasena: Confirmación de contraseña
    - submit: Botón de envío
    """
    
    # ===== CAMPOS DEL FORMULARIO =====
    
    nombre_usuario = StringField(
        'Nombre de Usuario',
        validators=[
            DataRequired(message='El nombre de usuario es obligatorio.'),
            Length(min=3, max=20, message='El nombre debe tener entre 3 y 20 caracteres.'),
            validate_username_format
        ],
        render_kw={
            'placeholder': 'Ingresa tu nombre de usuario',
            'class': 'form-control',
            'autocomplete': 'username'
        }
    )
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(message='El email es obligatorio.'),
            Email(message='Por favor ingresa un email válido.'),
            validate_email_format
        ],
        render_kw={
            'placeholder': 'ejemplo@correo.com',
            'class': 'form-control',
            'autocomplete': 'email'
        }
    )
    
    contrasena = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message='La contraseña es obligatoria.'),
            Length(min=8, message='La contraseña debe tener al menos 8 caracteres.'),
            validate_password_strength
        ],
        render_kw={
            'placeholder': 'Ingresa tu contraseña',
            'class': 'form-control',
            'autocomplete': 'new-password'
        }
    )
    
    confirmar_contrasena = PasswordField(
        'Confirmar Contraseña',
        validators=[
            DataRequired(message='Debes confirmar tu contraseña.'),
            EqualTo('contrasena', message='Las contraseñas no coinciden.')
        ],
        render_kw={
            'placeholder': 'Confirma tu contraseña',
            'class': 'form-control',
            'autocomplete': 'new-password'
        }
    )
    
    submit = SubmitField(
        'Registrarse',
        render_kw={'class': 'btn btn-primary btn-block'}
    )

# =============================================================================
# FORMULARIO DE LOGIN
# =============================================================================

class LoginForm(FlaskForm):
    """
    FORMULARIO DE INICIO DE SESIÓN
    
    Permite a los usuarios autenticarse en el sistema.
    Campos simples para email y contraseña.
    
    CAMPOS:
    - email: Email del usuario
    - contrasena: Contraseña del usuario
    - submit: Botón de envío
    """
    
    # ===== CAMPOS DEL FORMULARIO =====
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(message='El email es obligatorio.'),
            Email(message='Por favor ingresa un email válido.')
        ],
        render_kw={
            'placeholder': 'ejemplo@correo.com',
            'class': 'form-control',
            'autocomplete': 'email'
        }
    )
    
    contrasena = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message='La contraseña es obligatoria.')
        ],
        render_kw={
            'placeholder': 'Ingresa tu contraseña',
            'class': 'form-control',
            'autocomplete': 'current-password'
        }
    )
    
    submit = SubmitField(
        'Iniciar Sesión',
        render_kw={'class': 'btn btn-primary btn-block'}
    )

# =============================================================================
# FORMULARIO DE PREFERENCIAS
# =============================================================================

class PreferenciasForm(FlaskForm):
    """
    FORMULARIO DE CONFIGURACIÓN DE PREFERENCIAS
    
    Permite a los usuarios configurar sus preferencias para el sistema
    de recomendación. Incluye criterios como tipo de viaje, presupuesto,
    ubicación, amenities, etc.
    
    CAMPOS:
    - tipo_viaje: Tipo de viaje preferido
    - presupuesto: Rango de presupuesto
    - ubicacion_preferida: Zona preferida
    - amenities_importantes: Amenities prioritarias
    - rating_minimo: Rating mínimo aceptable
    - estrellas: Estrellas preferidas
    - submit: Botón de envío
    """
    
    # ===== CAMPOS DEL FORMULARIO =====
    
    tipo_viaje = SelectField(
        'Tipo de Viaje',
        choices=[
            ('', 'Selecciona el tipo de viaje'),
            ('turismo', 'Turismo'),
            ('negocios', 'Negocios'),
            ('familiar', 'Familiar'),
            ('romantico', 'Romántico'),
            ('aventura', 'Aventura'),
            ('cultural', 'Cultural'),
            ('relax', 'Relax')
        ],
        validators=[
            Optional()
        ],
        render_kw={
            'class': 'form-control'
        }
    )
    
    presupuesto = SelectField(
        'Presupuesto',
        choices=[
            ('', 'Selecciona tu presupuesto'),
            ('economico', 'Económico (< $100,000)'),
            ('medio', 'Medio ($100,000 - $300,000)'),
            ('alto', 'Alto ($300,000 - $500,000)'),
            ('lujo', 'Lujo (> $500,000)')
        ],
        validators=[
            Optional()
        ],
        render_kw={
            'class': 'form-control'
        }
    )
    
    ubicacion_preferida = StringField(
        'Ubicación Preferida',
        validators=[
            Optional(),
            Length(max=100, message='La ubicación no puede exceder 100 caracteres.')
        ],
        render_kw={
            'placeholder': 'Ej: Centro histórico, Bocagrande, Getsemaní',
            'class': 'form-control'
        }
    )
    
    amenities_importantes = TextAreaField(
        'Amenities Importantes',
        validators=[
            Optional(),
            Length(max=500, message='Las amenities no pueden exceder 500 caracteres.')
        ],
        widget=TextArea(),
        render_kw={
            'placeholder': 'Ej: WiFi, Piscina, Gimnasio, Restaurante, Estacionamiento',
            'class': 'form-control',
            'rows': '3'
        }
    )
    
    rating_minimo = SelectField(
        'Rating Mínimo',
        choices=[
            ('', 'Sin preferencia'),
            ('7.0', '7.0 o superior'),
            ('7.5', '7.5 o superior'),
            ('8.0', '8.0 o superior'),
            ('8.5', '8.5 o superior'),
            ('9.0', '9.0 o superior')
        ],
        validators=[
            Optional()
        ],
        render_kw={
            'class': 'form-control'
        }
    )
    
    estrellas = SelectField(
        'Estrellas Preferidas',
        choices=[
            ('', 'Sin preferencia'),
            ('3', '3 estrellas'),
            ('4', '4 estrellas'),
            ('5', '5 estrellas'),
            ('3,4', '3-4 estrellas'),
            ('4,5', '4-5 estrellas'),
            ('3,4,5', '3-5 estrellas')
        ],
        validators=[
            Optional()
        ],
        render_kw={
            'class': 'form-control'
        }
    )
    
    submit = SubmitField(
        'Guardar Preferencias',
        render_kw={'class': 'btn btn-primary btn-block'}
    )

# =============================================================================
# FORMULARIO DE SCRAPING (ADMIN)
# =============================================================================

class ScrapingForm(FlaskForm):
    """
    FORMULARIO DE CONFIGURACIÓN DE SCRAPING
    
    Permite a los administradores configurar y ejecutar el scraping
    de hoteles desde diferentes fuentes.
    
    CAMPOS:
    - destino: Ciudad o destino a scrapear
    - checkin: Fecha de check-in
    - checkout: Fecha de check-out
    - hotel_limit: Número máximo de hoteles
    - submit: Botón de envío
    """
    
    # ===== CAMPOS DEL FORMULARIO =====
    
    destino = StringField(
        'Destino',
        validators=[
            DataRequired(message='El destino es obligatorio.'),
            Length(min=2, max=50, message='El destino debe tener entre 2 y 50 caracteres.')
        ],
        render_kw={
            'placeholder': 'Ej: Cartagena, Medellín, Bogotá',
            'class': 'form-control',
            'value': 'Cartagena'
        }
    )
    
    checkin = DateField(
        'Fecha de Check-in',
        validators=[
            Optional()
        ],
        format='%Y-%m-%d',
        render_kw={
            'class': 'form-control',
            'type': 'date'
        }
    )
    
    checkout = DateField(
        'Fecha de Check-out',
        validators=[
            Optional()
        ],
        format='%Y-%m-%d',
        render_kw={
            'class': 'form-control',
            'type': 'date'
        }
    )
    
    hotel_limit = IntegerField(
        'Límite de Hoteles',
        validators=[
            Optional(),
            NumberRange(min=1, max=100, message='El límite debe estar entre 1 y 100.')
        ],
        render_kw={
            'placeholder': '20',
            'class': 'form-control',
            'value': 20
        }
    )
    
    submit = SubmitField(
        'Ejecutar Scraping',
        render_kw={'class': 'btn btn-warning btn-block'}
    )

# =============================================================================
# FORMULARIO DE RECUPERACIÓN DE CONTRASEÑA
# =============================================================================

class RecuperarPasswordForm(FlaskForm):
    """
    FORMULARIO DE RECUPERACIÓN DE CONTRASEÑA
    
    Permite a los usuarios solicitar la recuperación de su contraseña
    mediante envío de código por email.
    
    CAMPOS:
    - email: Email del usuario
    - submit: Botón de envío
    """
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(message='El email es obligatorio.'),
            Email(message='Por favor ingresa un email válido.')
        ],
        render_kw={
            'placeholder': 'ejemplo@correo.com',
            'class': 'form-control',
            'autocomplete': 'email'
        }
    )
    
    submit = SubmitField(
        'Enviar Código de Recuperación',
        render_kw={'class': 'btn btn-primary btn-block'}
    )

# =============================================================================
# FORMULARIO DE VERIFICACIÓN DE CÓDIGO
# =============================================================================

class VerificarCodigoForm(FlaskForm):
    """
    FORMULARIO DE VERIFICACIÓN DE CÓDIGO
    
    Permite a los usuarios verificar el código enviado por email
    para proceder con la recuperación de contraseña.
    
    CAMPOS:
    - codigo: Código de verificación
    - submit: Botón de envío
    """
    
    codigo = StringField(
        'Código de Verificación',
        validators=[
            DataRequired(message='El código es obligatorio.'),
            Length(min=6, max=6, message='El código debe tener 6 dígitos.')
        ],
        render_kw={
            'placeholder': '123456',
            'class': 'form-control',
            'maxlength': '6'
        }
    )
    
    submit = SubmitField(
        'Verificar Código',
        render_kw={'class': 'btn btn-primary btn-block'}
    )

# =============================================================================
# FORMULARIO DE RESTABLECER CONTRASEÑA
# =============================================================================

class RestablecerPasswordForm(FlaskForm):
    """
    FORMULARIO DE RESTABLECER CONTRASEÑA
    
    Permite a los usuarios establecer una nueva contraseña
    después de verificar el código de recuperación.
    
    CAMPOS:
    - nueva_contrasena: Nueva contraseña
    - confirmar_contrasena: Confirmación de nueva contraseña
    - submit: Botón de envío
    """
    
    nueva_contrasena = PasswordField(
        'Nueva Contraseña',
        validators=[
            DataRequired(message='La nueva contraseña es obligatoria.'),
            Length(min=8, message='La contraseña debe tener al menos 8 caracteres.'),
            validate_password_strength
        ],
        render_kw={
            'placeholder': 'Ingresa tu nueva contraseña',
            'class': 'form-control',
            'autocomplete': 'new-password'
        }
    )
    
    confirmar_contrasena = PasswordField(
        'Confirmar Nueva Contraseña',
        validators=[
            DataRequired(message='Debes confirmar tu nueva contraseña.'),
            EqualTo('nueva_contrasena', message='Las contraseñas no coinciden.')
        ],
        render_kw={
            'placeholder': 'Confirma tu nueva contraseña',
            'class': 'form-control',
            'autocomplete': 'new-password'
        }
    )
    
    submit = SubmitField(
        'Restablecer Contraseña',
        render_kw={'class': 'btn btn-primary btn-block'}
    )

# =============================================================================
# FORMULARIO DE VALORACIÓN
# =============================================================================

class ValoracionForm(FlaskForm):
    """
    FORMULARIO DE VALORACIÓN DE HOTEL
    
    Permite a los usuarios valorar hoteles con puntuación y comentarios.
    
    CAMPOS:
    - puntuacion: Puntuación del hotel (1-10)
    - comentario: Comentario opcional
    - submit: Botón de envío
    """
    
    puntuacion = SelectField(
        'Puntuación',
        choices=[
            ('', 'Selecciona una puntuación'),
            ('1', '1 - Muy malo'),
            ('2', '2 - Malo'),
            ('3', '3 - Regular'),
            ('4', '4 - Aceptable'),
            ('5', '5 - Bueno'),
            ('6', '6 - Muy bueno'),
            ('7', '7 - Excelente'),
            ('8', '8 - Sobresaliente'),
            ('9', '9 - Excepcional'),
            ('10', '10 - Perfecto')
        ],
        validators=[
            DataRequired(message='Debes seleccionar una puntuación.')
        ],
        render_kw={
            'class': 'form-control'
        }
    )
    
    comentario = TextAreaField(
        'Comentario (Opcional)',
        validators=[
            Optional(),
            Length(max=500, message='El comentario no puede exceder 500 caracteres.')
        ],
        widget=TextArea(),
        render_kw={
            'placeholder': 'Comparte tu experiencia con este hotel...',
            'class': 'form-control',
            'rows': '4'
        }
    )
    
    submit = SubmitField(
        'Enviar Valoración',
        render_kw={'class': 'btn btn-success btn-block'}
    ) 