# 🏨 Sistema Recomendador de Hoteles

## 📋 Descripción General

Este Sistema de recomendación de hoteles está desarrollado en **Python Flask** con scraping multi-fuente, búsqueda avanzada, historial de usuario, favoritos, valoraciones, panel de administración y seguridad.

### 🎯 Objetivos del Sistema

- **Recomendación Personalizada**: Basada en preferencias del usuario y historial de valoraciones
- **Scraping Multi-fuente**: Booking.com, Trivago y otros sitios de reservas
- **Interfaz Moderna**: Diseño responsive con búsqueda avanzada y autocompletado
- **Gestión de Usuarios**: Sistema completo de autenticación y perfiles
- **Panel Administrativo**: Control total del sistema para administradores

## 🚀 Características Principales

### 🔍 Búsqueda y Filtrado Avanzado
- **Búsqueda Fuzzy**: Búsqueda inteligente con Fuse.js
- **Filtros Múltiples**: Por amenities, estrellas, ubicación, precio
- **Autocompletado**: Sugerencias en tiempo real
- **Búsqueda Natural**: Interpreta consultas en lenguaje natural

### 📊 Sistema de Recomendaciones
- **Filtrado Colaborativo**: Basado en valoraciones de otros usuarios
- **Filtrado por Contenido**: Según preferencias del usuario
- **Algoritmo Híbrido**: Combina ambos enfoques para mejores resultados

### 👤 Gestión de Usuarios
- **Registro/Login**: Sistema completo de autenticación
- **Perfiles Personalizados**: Preferencias y configuración individual
- **Historial Completo**: Vistas, favoritos y valoraciones
- **Recuperación de Contraseña**: Por email con códigos de verificación, este paso está en proceso para la autenticación de la recuperación de contraseña.

### 🏨 Gestión de Hoteles
- **Scraping Automático**: Extracción de datos de múltiples fuentes (Por el momento solo Booking.com)
- **Enriquecimiento de Datos**: Normalización y limpieza automática
- **Imágenes y Reviews**: Contenido multimedia completo
- **Información Detallada**: Precios, amenities, ubicación, contactos

### 🛡️ Seguridad y Administración
- **Panel de Admin**: Gestión completa de usuarios y datos
- **Protección CSRF**: Seguridad contra ataques
- **Validación Estricta**: Sanitización de entradas
- **Logs Detallados**: Monitoreo de operaciones

## 🏗️ Arquitectura del Sistema

### 📁 Estructura de Archivos

```
Sistema Recomendador Final/
├── app.py                 # Aplicación principal Flask
├── models.py              # Modelos de base de datos
├── scraper.py             # Sistema de scraping
├── config.py              # Configuración del sistema
├── forms.py               # Formularios web
├── requirements.txt       # Dependencias Python
├── database_sistema_recomendador.sql  # Esquema de BD
├── static/                # Archivos estáticos
│   ├── css/
│   │   └── styles.css     # Estilos CSS
│   ├── js/
│   │   └── main.js        # JavaScript del frontend
│   └── images/            # Imágenes del sistema
├── templates/             # Plantillas HTML
│   ├── base.html          # Plantilla base
│   ├── auth.html          # Autenticación
│   ├── hoteles.html       # Lista de hoteles
│   ├── hotel_detalle.html # Detalle de hotel
│   ├── perfil.html        # Perfil de usuario
│   ├── historial.html     # Historial de usuario
│   └── admin_*.html       # Paneles administrativos
└── venv/                  # Entorno virtual Python
```
Tener en cuenta que usé Python 3.10

### 🗄️ Base de Datos

#### Tablas Principales

1. **`usuario`** - Información de usuarios
   - `id_usuario`, `nombre_usuario`, `email`, `password_hash`
   - `fecha_registro`, `ultimo_login`, `es_admin`

2. **`hoteles`** - Datos de hoteles scrapeados
   - `id_hotel`, `nombre`, `slug`, `descripcion`, `ubicacion`
   - `precio_*`, `rating_*`, `stars_*`, `amenities`
   - `imagen_url`, `reviews`, `contacto`, `coordenadas`

3. **`valoraciones`** - Opiniones de usuarios
   - `id_valoracion`, `id_usuario`, `id_hotel`
   - `puntuacion`, `comentario`, `fecha_valoracion`

4. **`interacciones_usuario`** - Historial de actividad
   - `id_interaccion`, `id_usuario`, `id_hotel`
   - `tipo_interaccion` (vista/valoracion/favorito)
   - `valor`, `fecha_interaccion`

5. **`preferencias_usuario`** - Configuración personal
   - `id_preferencias`, `id_usuario`
   - `tipo_viaje`, `presupuesto`, `ubicacion_preferida`
   - `amenities_importantes`, `rating_minimo`, `estrellas`

la demás tablas están en la carpeta database_sistema_recomendador.sql


## 🛠️ Instalación y Configuración

### 📋 Prerrequisitos

- **Python 3.8+**
- **MySQL/MariaDB** (o SQLite para desarrollo)
- **Chrome/Chromium** (para scraping)
- **Git** (para clonar el repositorio)

### 🔧 Instalación Paso a Paso

#### 1. Clonar el Repositorio
```bash
git clone [URL_DEL_REPOSITORIO]
cd Sistema\ Recomendador\ Final
```

#### 2. Crear Entorno Virtual
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

#### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

#### 4. Configurar Base de Datos

**Opción A: MySQL (Recomendado para producción)**
```sql
CREATE DATABASE sistema_recomendador_hoteles;
CREATE USER 'usuario'@'localhost' IDENTIFIED BY 'contraseña';
GRANT ALL PRIVILEGES ON sistema_recomendador_hoteles.* TO 'usuario'@'localhost';
FLUSH PRIVILEGES;
```
//**Para que funcione correctamente, asegúrate de tener instalado el motor de base de datos MySQL y que esté en tu sistema operativo.**//

**Opción B: SQLite (Para desarrollo)**
```python
# En config.py cambiar:
SQLALCHEMY_DATABASE_URI = 'sqlite:///hoteles.db'
```

#### 5. Configurar Variables de Entorno

Crear archivo `.env`:
```env
SECRET_KEY=tu_clave_secreta_muy_segura
DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost/sistema_recomendador_hoteles
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_contraseña_de_aplicacion
MAIL_DEFAULT_SENDER=tu_email@gmail.com
```

#### 6. Crear Usuario Administrador
```bash
flask crear_admin --email admin@gmail.com --password admin123 

Si sale error ejecuta:   python -m flask crear_admin  
                              --email admin@gmail.com 
                              --password admin123
```

#### 7. Ejecutar Migraciones
```bash
flask run
# La primera vez creará automáticamente las tablas
```

## 🚀 Uso del Sistema

### 🏠 Página Principal
- **URL**: `http://localhost:5000`
- **Acceso**: Requiere login
- **Funcionalidad**: Dashboard con hoteles recomendados

### 🔐 Autenticación
- **Registro**: `/auth?tab=register`
- **Login**: `/auth?tab=login`
- **Recuperación**: `/recuperar`

### 🏨 Exploración de Hoteles
- **Lista General**: `/hoteles`
- **Detalle de Hotel**: `/hotel/<slug>`
- **Favoritos**: `/favoritos`
- **Historial**: `/historial`

### 👤 Perfil de Usuario
- **Configuración**: `/ajustes`
- **Perfil**: `/perfil`
- **Gestión de Cuenta**: `/gestion_cuenta`

### 🔧 Panel Administrativo
- **Usuarios**: `/admin/usuarios`
- **Ajustes**: `/admin/ajustes`
- **Acceso**: Solo usuarios con `es_admin = True`

## 🔍 Sistema de Scraping

### 📊 Fuentes de Datos
- **Booking.com**: Información principal de hoteles
- **Trivago**: Precios y comparaciones
- **Google**: Información adicional y reviews

### 🛠️ Ejecutar Scraping

#### Scraping Manual
```bash
python scraper.py
```

#### Scraping desde la Aplicación
```bash
# Acceder como admin y usar el panel de ajustes
# O ejecutar directamente:
flask run
# Ir a /admin/ajustes
```

### ⚙️ Configuración del Scraper

*Tengan en cuenta que el Scraping tiene un limite de 200 hoteles, por qué Booking comienza a bloquear la API, por lo que es mejor ser algo precavidos y no usarlo para hacer scrapings de grandes cantidades de hoteles. Lo mas recomendable usar 50 hoteles por scraper, para que no se bloqueen.*
## Como lo sé?, pues ya lo intenté. Pero no me funcionó.


#### Parámetros Principales
- **`hotel_limit`**: Número máximo de hoteles a scrapear
- **`destination`**: Ciudad o destino a buscar
- **`checkin/checkout`**: Fechas de búsqueda
- **`headless`**: Modo sin interfaz gráfica

#### Configuración Avanzada
```python
# En scraper.py
SCRAPING_CONFIG = {
    'max_retries': 3,
    'delay_between_requests': 2,
    'timeout': 30,
    'user_agent_rotation': True
}
```

## 🔧 API REST

### 📡 Endpoints Disponibles

#### Hoteles
```http
GET /api/hotels
# Retorna: Lista de todos los hoteles en JSON
```

#### Recomendaciones
```http
GET /api/recomendaciones
# Headers: Authorization required
# Retorna: Hoteles recomendados para el usuario
```

#### Valoraciones
```http
POST /api/valorar
# Body: {"hotel_id": 1, "puntuacion": 8.5, "comentario": "..."}
# Retorna: Confirmación de valoración
```

## 🎨 Frontend y UX

### 🎯 Características de la Interfaz

#### Búsqueda Avanzada
- **Fuzzy Search**: Búsqueda inteligente con Fuse.js
- **Autocompletado**: Sugerencias en tiempo real
- **Filtros Dinámicos**: Por precio, estrellas, amenities
- **Búsqueda Natural**: Interpreta consultas como "hoteles con piscina en Cartagena"

#### Diseño Responsive
- **Mobile First**: Optimizado para dispositivos móviles
- **Glassmorphism**: Diseño moderno con efectos de cristal
- **Animaciones**: Transiciones suaves y feedback visual
- **Accesibilidad**: Cumple estándares WCAG

#### Componentes Principales
- **Search Bar**: Búsqueda principal con autocompletado
- **Hotel Cards**: Tarjetas de hoteles con información completa
- **Amenity Chips**: Amenities mostradas como chips con emojis
- **Rating System**: Sistema de valoración con estrellas
- **History Timeline**: Historial de usuario en formato timeline

### 🎨 Tecnologías Frontend
- **HTML5**: Estructura semántica
- **CSS3**: Estilos modernos con Flexbox y Grid
- **JavaScript ES6+**: Funcionalidad interactiva
- **Fuse.js**: Búsqueda fuzzy
- **Toastify**: Notificaciones elegantes

## 🔒 Seguridad

### 🛡️ Medidas Implementadas

#### Autenticación y Autorización
- **Flask-Login**: Gestión de sesiones segura
- **Bcrypt**: Encriptación de contraseñas
- **CSRF Protection**: Protección contra ataques CSRF
- **Role-based Access**: Control de acceso por roles

#### Validación y Sanitización
- **WTForms**: Validación de formularios
- **SQLAlchemy**: Prevención de SQL Injection
- **Input Sanitization**: Limpieza de entradas
- **XSS Protection**: Protección contra XSS

#### Configuración de Producción
- **HTTPS**: Forzado en producción
- **Secure Cookies**: Cookies seguras
- **Environment Variables**: Configuración externa
- **Logging**: Registro de actividades críticas

## 📊 Sistema de Recomendaciones

### 🧠 Algoritmos Implementados

#### 1. Filtrado Colaborativo
```python
# Basado en valoraciones de usuarios similares
def collaborative_filtering(user_id):
    # 1. Encontrar usuarios similares
    # 2. Obtener hoteles valorados positivamente
    # 3. Recomendar hoteles no vistos
```

#### 2. Filtrado por Contenido
```python
# Basado en preferencias del usuario
def content_based_filtering(user_preferences):
    # 1. Analizar preferencias (estrellas, amenities, ubicación)
    # 2. Buscar hoteles que coincidan
    # 3. Ordenar por relevancia
```

#### 3. Algoritmo Híbrido
```python
# Combina ambos enfoques
def hybrid_recommendation(user_id):
    collaborative = collaborative_filtering(user_id)
    content_based = content_based_filtering(user_preferences)
    return combine_recommendations(collaborative, content_based)
```

### 📈 Métricas de Evaluación
- **Precision@K**: Precisión en las top-K recomendaciones
- **Recall@K**: Cobertura de recomendaciones relevantes
- **NDCG**: Normalized Discounted Cumulative Gain
- **User Satisfaction**: Feedback directo de usuarios

## 🧪 Testing

## ARCHIVOS DEBUG - EXPLICACIÓN DETALLADA:
Los archivos **debug_*.html**  que ves en el proyecto son archivos de debugging que se generaron
automáticamente durante el desarrollo del sistema de scraping. 

Te explico para qué sirven:

*LOS ARCHIVOS DEBUG*
Los archivos debug son capturas del HTML de Booking.com que se guardan cuando el scraper
encuentra problemas para extraer información de ciertos hoteles. Por ejemplo, cuando no
puede encontrar el precio de un hotel específico.

*¿PARA QUÉ SIRVEN LOS ARCHIVOS DEBUG?*

1. PARA IDENTIFICAR PROBLEMAS: Cuando el scraper no puede extraer el precio de un hotel,
   se guarda el HTML completo en un archivo debug para que podamos analizar por qué falló.

2. PARA ENTENDER LA ESTRUCTURA DE BOOKING: *Booking.com cambia constantemente su estructura HTML*, 
   por lo que estos archivos nos ayudan a ver cómo está organizada
   la información actualmente.

3. PARA MEJORAR EL SCRAPER: Al analizar estos archivos, podemos ajustar los
   selectores CSS en scraper.py para que funcionen con la nueva estructura.

4. PARA DETECTAR BLOQUEOS: Booking.com bloquea el scraping, así que estos archivos
   nos muestran cuando nos están bloqueando o mostrando captchas.

### Archivo de Logs (`scraper.log`)

El archivo `scraper.log` es un **archivo de registro (log)** que se genera automáticamente durante la ejecución del sistema de scraping.

#### QUÉ ES SCRAPER.LOG?
Es un archivo de **logging** que registra todas las actividades y eventos que ocurren durante el proceso de scraping. Se crea automáticamente para ayudar a diagnosticar problemas y monitorear el funcionamiento del scraper.

#### PARA QUÉ SIRVE SCRAPER.LOG?

**1. Debugging y Diagnóstico**
- Registra errores cuando el scraper falla
- Muestra qué hoteles se procesaron exitosamente
- Indica cuándo Booking.com bloquea las peticiones

**2. Monitoreo de Actividad**
- Registra cuántos hoteles se encontraron en cada página
- Muestra el progreso del scraping (hotel 1, hotel 2, etc.)
- Indica cuándo se completan las peticiones

**3. Análisis de Problemas**
- Registra cuando no se pueden extraer precios
- Muestra errores de conexión o timeout
- Indica cuando Booking.com muestra captchas
- Muestra cuándo Booking.com bloquea las peticiones

## archivos test_*.py
Los archivos test_*.py son archivos de prueba que se encuentran en el directorio tests. Estos archivos contienen pruebas unitarias y de integración para diferentes componentes del sistema.
*Espero que estos archivos de prueba sean útiles, ya que ayudarán a identificar problemas y asegurarte de que el sistema funcione correctamente.*
 
## archivo fix_amenities_json.py
El archivo fix_amenities_json.py es un script que se encuentra en la carpeta scripts. Este script se utiliza para corregir los datos de amenities en el archivo de datos de Booking.com. Este archivo se utiliza para actualizar los datos de amenities en el archivo de datos de Booking.com.
*Este script es muy útil, ya que te ayudará a actualizar los datos de amenities en el archivo de datos de Booking.com.*

## form.py
El archivo form.py es un archivo de código que se encuentra en la carpeta forms. Este archivo contiene todos los formularios del sistema utilizando Flask-WTF. Cada formulario define los campos, validaciones y comportamiento específico para diferentes funcionalidades del sistema.
*Este archivo es muy importante, ya que te ayudará a entender cómo se crean los formularios del sistema. Entendiste mij@, aqui miras como se crean los formularios del sistema. Despues no andes preguntando... Lee lee lee.*

## models.py
El archivo models.py es un archivo de código que se encuentra en la carpeta models. Este archivo contiene todas las clases de modelo del sistema utilizando SQLAlchemy. Cada clase define las tablas y las relaciones entre ellas.
*Este archivo es muy importante, ya que te ayudará a entender cómo se crean las tablas y las relaciones entre ellas. Entendiste señor, aqui miras como se crean las tablas y las relaciones entre ellas. Despues no andes preguntando... Lee lee lee.*

## pruebas.txt (HTML)
En el archivo está el HTML de la página de Booking.com que utilicé para extraer los datos de los hoteles. Este archivo es un archivo de texto plano que contiene el HTML de la página de Booking.com. Aquí puedes encontar su estructura y su contenido.

## update_app_for_new_db.py
Este script se utiliza para actualizar el código del sistema para utilizar una base de datos diferente. Es un Script para actualizar la aplicación Flask para usar la nueva estructura de base de datos enriquecida.

## hoteles_scrapeados.json
Este es un archivo JSON que se encuentra en la carpeta data. Este archivo contiene los datos de hoteles extraídos de Booking.com. Cada hotel se representa como un objeto JSON que contiene información sobre el hotel, como su nombre, ubicación, precio, etc. Este archivo se utiliza para almacenar los datos de hoteles scrapeados.
*Este archivo es muy importante, ya que te ayudará a almacenar los datos de hoteles scrapeados. Entendiste señor, aqui miras como se almacenan los datos de hoteles scrapeados. Despues no andes preguntando... Lee lee lee.*

### 🧪 Pruebas Implementadas

#### Pruebas Unitarias
```bash
# Ejecutar todas las pruebas
python -m pytest

# Pruebas específicas
python -m pytest test_hotels.py
python -m pytest test_app.py
```

#### Pruebas de Integración
```bash
# Pruebas del scraper
python test_selenium.py

# Pruebas de la API
python test_api.py
```

### 📋 Casos de Prueba

#### Funcionalidades Principales
- ✅ Registro y login de usuarios
- ✅ Scraping de hoteles
- ✅ Sistema de recomendaciones
- ✅ Valoraciones y comentarios
- ✅ Gestión de favoritos
- ✅ Panel administrativo

#### Casos Edge 
- ✅ Usuario sin preferencias
- ✅ Hoteles sin valoraciones
- ✅ Errores de scraping
- ✅ Validación de formularios
- ✅ Manejo de errores 404/500

## 🚀 Despliegue: Es para producción

### 🐳 Docker (Recomendado)

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

#### Docker Compose
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql://user:pass@db:3306/hoteles
    depends_on:
      - db
  
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: hoteles
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```
Esta parte de Docker no es necesaria para la ejecución del sistema, pero se recomienda para su despliegue en la nube.
**Quedó claro Señor(Opcional)**

### ☁️ Despliegue en la Nube
Este despliegue no es necesario para la ejecución del sistema, pero se recomienda para su despliegue en la nube.
**Quedó claro joven(Opcional)**

#### Heroku
Si no sabes que es Heroku, es un servicio de despliegue en la nube gratuito. Puedes usarlo para desplegar tu aplicación en la nube.
**Mij@ esto es (Opcional)**

```bash
# Crear app en Heroku
heroku create mi-sistema-hoteles

# Configurar variables de entorno
heroku config:set SECRET_KEY=tu_clave_secreta
heroku config:set DATABASE_URL=tu_url_de_base_de_datos

# Desplegar
git push heroku main
```

#### AWS/GCP/Azure
Si no sabes que es AWS, es un servicio de despliegue en la nube, gratuito. Puedes usarlo para desplegar la app en la nube. **Quedo claro Señor(Opcional)**

- **EC2/Compute Engine**: Servidor virtual
- **RDS/Cloud SQL**: Base de datos gestionada
- **S3/Cloud Storage**: Almacenamiento de archivos
- **CloudFront/CDN**: Distribución de contenido

### 🔧 Configuración de Producción

#### Gunicorn + Nginx
Esta parte de configuración es opcional, pero se recomienda para su despliegue en producción. Todo esto es opcional y puedes usar otro servidor de tu preferencia. Y no es necesario para la ejecución del sistema. **Quedó claro Señor(Opcional)**


```bash
# Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Nginx config
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /path/to/static;
    }
}
```

#### Variables de Entorno de Producción
Esta parte de configuración es opcional, pero se recomienda para su despliegue en producción. Todo esto es opcional y puedes usar otro servidor de tu gusto. Y no es necesario para la ejecución del sistema.    **Quedó claro Señor(Opcional)**

```env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=clave_super_secreta_y_larga
DATABASE_URL=mysql://user:pass@host:3306/db
MAIL_USERNAME=tu_email
MAIL_PASSWORD=tu_app_password
```

## 📚 Documentación de Código

### 📖 Comentarios y Documentación

El código está completamente comentado con:
- **Docstrings**: Documentación de funciones y clases
- **Comentarios Inline**: Explicación de lógica compleja
- **Secciones Organizadas**: Código dividido en secciones lógicas
- **Ejemplos de Uso**: Casos de uso comunes

### 🔍 Estructura de Comentarios

```python
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

AUTOR: [Wilson Muñoz]
FECHA: [12-07-2025]
VERSIÓN: Ultima jaja
"""

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
    # ... resto del código
```

## 🤝 Contribución

### 📋 Guías de Contribución

#### Estándares de Código
- **PEP 8**: Estilo de código Python
- **Type Hints**: Anotaciones de tipos
- **Docstrings**: Documentación obligatoria
- **Tests**: Pruebas para nuevas funcionalidades

#### Proceso de Desarrollo
1. **Fork** del repositorio
2. **Crear rama** para nueva funcionalidad
3. **Desarrollar** con tests incluidos
4. **Commit** con mensajes descriptivos
5. **Pull Request** con descripción detallada

#### Estructura de Commits
```
feat: agregar búsqueda avanzada
fix: corregir error en scraping de precios
docs: actualizar documentación de API
test: agregar pruebas para recomendaciones
refactor: optimizar algoritmo de filtrado
```


## 👥 Autores

- **Desarrollador Principal**: [Wilson Muñoz Serrano](https://github.com/MunozS18)
- **Fecha de Creación**: [12-07-2025]
- **Versión**: Creo que es la ultima jajaja
- **Contacto**: [munozserranow@gmail.com]

## 🙏 Agradecimientos

- **Flask**: Framework web elegante
- **SQLAlchemy**: ORM potente y flexible
- **Selenium**: Automatización de navegadores
- **Fuse.js**: Búsqueda fuzzy en JavaScript
- **Bootstrap**: Framework CSS para diseño responsive


---

## 📞 Soporte

Para cualquier preguntas sobre el sistema:

- **Email**: [munozserranow@gmail.com]
- **GITHUB**: Puedes descargar el codigo en el repositorio de GitHub https://github.com/MunozS18/Sistema_Recomendador.git
- **Documentación**: Lee este README.md para obtener más información de como funciona el sistema.

