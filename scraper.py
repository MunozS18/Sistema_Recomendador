"""
SCRAPER DE HOTELES - SISTEMA RECOMENDADOR DE HOTELES
====================================================

Este archivo contiene el sistema de scraping web para obtener información
de hoteles desde diferentes fuentes como Booking.com, Trivago, etc.

CARACTERÍSTICAS:
- Scraping automatizado de múltiples fuentes
- Procesamiento y limpieza de datos
- Extracción de amenities, precios, ratings
- Manejo de errores y reintentos
- Configuración flexible de parámetros

FUENTES SOPORTADAS:
- Booking.com (principal)
- Trivago (en desarrollo)
- Otras fuentes (pendientes)

AUTOR: Wilson Munoz Serrano
FECHA: 1 mes jajaja y mucho desvelo
VERSIÓN: 2.0
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime, timedelta
import re
from urllib.parse import urljoin, urlparse
import logging

# =============================================================================
# CONFIGURACIÓN Y CONSTANTES
# =============================================================================

# Configurar logging para debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Headers para simular navegador real
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# URLs base para diferentes fuentes
BOOKING_BASE_URL = "https://www.booking.com"
TRIVAGO_BASE_URL = "https://www.trivago.com"

# =============================================================================
# FUNCIONES AUXILIARES DE SCRAPING
# =============================================================================

def get_random_delay():
    """
    Genera un delay aleatorio para evitar detección como bot
    
    Returns:
        Tiempo de espera en segundos (entre 1 y 3 segundos)
    """
    return random.uniform(1, 3)

def clean_text(text):
    """
    Limpia y normaliza texto extraído del HTML
    
    Args:
        text: Texto a limpiar
        
    Returns:
        Texto limpio y normalizado
    """
    if not text:
        return ""
    
    # Eliminar espacios extra y saltos de línea
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Eliminar caracteres especiales problemáticos
    text = text.replace('\xa0', ' ')
    text = text.replace('\u200b', '')
    
    return text

def extract_price(price_text):
    """
    Extrae y procesa información de precio
    
    Args:
        price_text: Texto que contiene información de precio
        
    Returns:
        Diccionario con información procesada del precio
    """
    if not price_text:
        return {'amount': None, 'currency': 'COP', 'formatted': ''}
    
    # Limpiar texto
    price_text = clean_text(price_text)
    
    # Extraer números
    numbers = re.findall(r'[\d,]+', price_text)
    if numbers:
        # Tomar el primer número encontrado
        amount_str = numbers[0].replace(',', '')
        try:
            amount = int(amount_str)
        except ValueError:
            amount = None
    else:
        amount = None
    
    # Determinar moneda
    currency = 'COP'
    if '$' in price_text or 'USD' in price_text:
        currency = 'USD'
    elif '€' in price_text or 'EUR' in price_text:
        currency = 'EUR'
    
    return {
        'amount': amount,
        'currency': currency,
        'formatted': price_text
    }

def extract_rating(rating_text):
    """
    Extrae y procesa información de rating
    
    Args:
        rating_text: Texto que contiene información de rating
        
    Returns:
        Diccionario con información procesada del rating
    """
    if not rating_text:
        return {'score': None, 'max_score': 10, 'formatted': ''}
    
    # Limpiar texto
    rating_text = clean_text(rating_text)
    
    # Buscar patrones de rating
    patterns = [
        r'(\d+(?:\.\d+)?)\s*/\s*(\d+)',  # 8.5/10
        r'(\d+(?:\.\d+)?)\s*de\s*(\d+)',  # 8.5 de 10
        r'(\d+(?:\.\d+)?)',  # Solo número
    ]
    
    for pattern in patterns:
        match = re.search(pattern, rating_text)
        if match:
            try:
                score = float(match.group(1))
                max_score = int(match.group(2)) if len(match.groups()) > 1 else 10
                return {
                    'score': score,
                    'max_score': max_score,
                    'formatted': rating_text
                }
            except ValueError:
                continue
    
    return {
        'score': None,
        'max_score': 10,
        'formatted': rating_text
    }

def extract_stars(stars_text):
    """
    Extrae y procesa información de estrellas
    
    Args:
        stars_text: Texto que contiene información de estrellas
        
    Returns:
        Diccionario con información procesada de estrellas
    """
    if not stars_text:
        return {'count': None, 'formatted': ''}
    
    # Limpiar texto
    stars_text = clean_text(stars_text)
    
    # Buscar número de estrellas
    star_match = re.search(r'(\d+)\s*estrellas?', stars_text, re.IGNORECASE)
    if star_match:
        try:
            count = int(star_match.group(1))
            return {
                'count': count,
                'formatted': stars_text
            }
        except ValueError:
            pass
    
    # Buscar estrellas con símbolos
    star_symbols = stars_text.count('★') + stars_text.count('⭐')
    if star_symbols > 0:
        return {
            'count': star_symbols,
            'formatted': stars_text
        }
    
    return {
        'count': None,
        'formatted': stars_text
    }

def extract_amenities(amenities_elements):
    """
    Extrae y procesa amenities de los elementos HTML
    
    Args:
        amenities_elements: Lista de elementos HTML con amenities
        
    Returns:
        Lista de amenities procesadas
    """
    amenities = []
    
    if not amenities_elements:
        return amenities
    
    for element in amenities_elements:
        # Extraer texto del elemento
        text = element.get_text() if hasattr(element, 'get_text') else str(element)
        text = clean_text(text)
        
        if text and len(text) > 2:  # Filtrar textos muy cortos
            amenities.append(text)
    
    return amenities

def make_request(url, retries=3):
    """
    Realiza una petición HTTP con reintentos y delays
    
    Args:
        url: URL a consultar
        retries: Número de reintentos en caso de error
        
    Returns:
        Objeto Response de requests o None si falla
    """
    for attempt in range(retries):
        try:
            # Delay aleatorio para evitar detección
            time.sleep(get_random_delay())
            
            # Realizar petición
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            
            return response
            
        except requests.RequestException as e:
            logger.warning(f"Intento {attempt + 1} falló para {url}: {e}")
            
            if attempt < retries - 1:
                # Esperar más tiempo antes del siguiente intento
                time.sleep(random.uniform(2, 5))
            else:
                logger.error(f"Todos los intentos fallaron para {url}")
                return None
    
    return None

# =============================================================================
# SCRAPER DE BOOKING.COM
# =============================================================================

def scrape_booking_hotels(destino="Cartagena", checkin=None, checkout=None, hotel_limit=200):
    """
    SCRAPER PRINCIPAL DE BOOKING.COM
    
    Extrae información de hoteles desde Booking.com con los parámetros especificados.
    
    Args:
        destino: Ciudad o destino a buscar
        checkin: Fecha de check-in (formato YYYY-MM-DD)
        checkout: Fecha de check-out (formato YYYY-MM-DD)
        hotel_limit: Número máximo de hoteles a scrapear
        
    Returns:
        Lista de diccionarios con información de hoteles
    """
    logger.info(f"Iniciando scraping de Booking.com para {destino}")
    
    # Configurar fechas por defecto si no se proporcionan
    if not checkin:
        checkin = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    if not checkout:
        checkout = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
    
    # Construir URL de búsqueda
    search_url = f"{BOOKING_BASE_URL}/searchresults.html"
    params = {
        'ss': destino,
        'checkin': checkin,
        'checkout': checkout,
        'group_adults': '2',
        'no_rooms': '1',
        'selected_currency': 'COP'
    }
    
    # Realizar petición inicial
    response = make_request(search_url, params=params)
    if not response:
        logger.error("No se pudo obtener la página de búsqueda")
        return []
    
    # Parsear HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Encontrar contenedores de hoteles
    hotel_containers = soup.find_all('div', {'data-testid': 'property-card'})
    
    if not hotel_containers:
        # Intentar con selectores alternativos
        hotel_containers = soup.find_all('div', class_='sr_property_block')
    
    logger.info(f"Encontrados {len(hotel_containers)} hoteles en la página")
    
    hotels_data = []
    processed_count = 0
    
    for container in hotel_containers:
        if processed_count >= hotel_limit:
            break
        
        try:
            hotel_info = extract_hotel_info_booking(container)
            if hotel_info:
                hotels_data.append(hotel_info)
                processed_count += 1
                logger.info(f"Procesado hotel {processed_count}: {hotel_info.get('name', 'Sin nombre')}")
        
        except Exception as e:
            logger.error(f"Error procesando hotel: {e}")
            continue
    
    logger.info(f"Scraping completado. {len(hotels_data)} hoteles procesados")
    return hotels_data

def extract_hotel_info_booking(container):
    """
    Extrae información detallada de un hotel desde el contenedor HTML de Booking.com
    
    Args:
        container: Elemento HTML que contiene la información del hotel
        
    Returns:
        Diccionario con toda la información del hotel
    """
    hotel_info = {}
    
    try:
        # ===== NOMBRE DEL HOTEL =====
        name_element = container.find('div', {'data-testid': 'title'})
        if not name_element:
            name_element = container.find('h3', class_='sr-hotel__name')
        if not name_element:
            name_element = container.find('a', class_='sr-hotel__name')
        
        if name_element:
            hotel_info['name'] = clean_text(name_element.get_text())
        
        # ===== DESCRIPCIÓN =====
        description_element = container.find('div', {'data-testid': 'description'})
        if description_element:
            hotel_info['description'] = clean_text(description_element.get_text())
        
        # ===== UBICACIÓN =====
        location_element = container.find('div', {'data-testid': 'address'})
        if not location_element:
            location_element = container.find('span', class_='sr-hotel__address')
        
        if location_element:
            hotel_info['location'] = clean_text(location_element.get_text())
        
        # ===== PRECIO =====
        price_element = container.find('span', {'data-testid': 'price-and-discounted-price'})
        if not price_element:
            price_element = container.find('span', class_='bui-price-display__value')
        
        if price_element:
            price_data = extract_price(price_element.get_text())
            hotel_info['price'] = price_data['formatted']
            hotel_info['price_amount'] = price_data['amount']
            hotel_info['price_currency'] = price_data['currency']
        
        # ===== RATING =====
        rating_element = container.find('div', {'data-testid': 'review-score'})
        if not rating_element:
            rating_element = container.find('div', class_='bui-review-score__badge')
        
        if rating_element:
            rating_data = extract_rating(rating_element.get_text())
            hotel_info['rating'] = rating_data['formatted']
            hotel_info['rating_score'] = rating_data['score']
            hotel_info['rating_max_score'] = rating_data['max_score']
        
        # ===== ESTRELLAS =====
        stars_element = container.find('div', {'data-testid': 'stars'})
        if not stars_element:
            stars_element = container.find('div', class_='sr-hotel__stars')
        
        if stars_element:
            stars_data = extract_stars(stars_element.get_text())
            hotel_info['stars'] = stars_data['formatted']
            hotel_info['stars_count'] = stars_data['count']
        
        # ===== AMENITIES =====
        amenities_elements = container.find_all('div', {'data-testid': 'amenity'})
        if not amenities_elements:
            amenities_elements = container.find_all('span', class_='sr-hotel__amenity')
        
        if amenities_elements:
            amenities = extract_amenities(amenities_elements)
            hotel_info['amenities'] = amenities
        
        # ===== IMAGEN =====
        image_element = container.find('img', {'data-testid': 'image'})
        if not image_element:
            image_element = container.find('img', class_='sr-hotel__image')
        
        if image_element:
            hotel_info['image'] = image_element.get('src') or image_element.get('data-src')
        
        # ===== ENLACE =====
        link_element = container.find('a', {'data-testid': 'title-link'})
        if not link_element:
            link_element = container.find('a', class_='sr-hotel__name')
        
        if link_element:
            hotel_info['link'] = urljoin(BOOKING_BASE_URL, link_element.get('href', ''))
        
        # ===== REVIEWS =====
        reviews_element = container.find('div', {'data-testid': 'review-score'})
        if reviews_element:
            # Intentar extraer número de reviews
            reviews_text = reviews_element.get_text()
            reviews_match = re.search(r'(\d+)\s*reviews?', reviews_text, re.IGNORECASE)
            if reviews_match:
                hotel_info['reviews_count'] = int(reviews_match.group(1))
        
        # ===== METADATOS =====
        hotel_info['source'] = 'booking'
        hotel_info['scraped_at'] = datetime.now().isoformat()
        
        # Validar que tenemos al menos el nombre
        if not hotel_info.get('name'):
            return None
        
        return hotel_info
        
    except Exception as e:
        logger.error(f"Error extrayendo información del hotel: {e}")
        return None

# =============================================================================
# SCRAPER DE TRIVAGO (EN DESARROLLO)
# =============================================================================

def scrape_trivago_hotels(destino="Cartagena", hotel_limit=10):
    """
    SCRAPER DE TRIVAGO (EN DESARROLLO)
    
    Extrae información de hoteles desde Trivago.
    Esta función está en desarrollo y puede no funcionar completamente.
    
    Args:
        destino: Ciudad o destino a buscar
        hotel_limit: Número máximo de hoteles a scrapear
        
    Returns:
        Lista de diccionarios con información de hoteles
    """
    logger.info(f"Iniciando scraping de Trivago para {destino}")
    
    # Construir URL de búsqueda
    search_url = f"{TRIVAGO_BASE_URL}/search"
    params = {
        'query': destino,
        'currency': 'COP'
    }
    
    # Realizar petición
    response = make_request(search_url, params=params)
    if not response:
        logger.error("No se pudo obtener la página de Trivago")
        return []
    
    # Parsear HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Encontrar contenedores de hoteles
    hotel_containers = soup.find_all('div', class_='hotel-item')
    
    logger.info(f"Encontrados {len(hotel_containers)} hoteles en Trivago")
    
    hotels_data = []
    processed_count = 0
    
    for container in hotel_containers:
        if processed_count >= hotel_limit:
            break
        
        try:
            hotel_info = extract_hotel_info_trivago(container)
            if hotel_info:
                hotels_data.append(hotel_info)
                processed_count += 1
        
        except Exception as e:
            logger.error(f"Error procesando hotel de Trivago: {e}")
            continue
    
    logger.info(f"Scraping de Trivago completado. {len(hotels_data)} hoteles procesados")
    return hotels_data

def extract_hotel_info_trivago(container):
    """
    Extrae información de un hotel desde el contenedor HTML de Trivago
    
    Args:
        container: Elemento HTML que contiene la información del hotel
        
    Returns:
        Diccionario con la información del hotel
    """
    hotel_info = {}
    
    try:
        # ===== NOMBRE DEL HOTEL =====
        name_element = container.find('h3', class_='hotel-name')
        if name_element:
            hotel_info['name'] = clean_text(name_element.get_text())
        
        # ===== PRECIO =====
        price_element = container.find('span', class_='price')
        if price_element:
            price_data = extract_price(price_element.get_text())
            hotel_info['price'] = price_data['formatted']
        
        # ===== RATING =====
        rating_element = container.find('span', class_='rating')
        if rating_element:
            rating_data = extract_rating(rating_element.get_text())
            hotel_info['rating'] = rating_data['formatted']
        
        # ===== METADATOS =====
        hotel_info['source'] = 'trivago'
        hotel_info['scraped_at'] = datetime.now().isoformat()
        
        return hotel_info if hotel_info.get('name') else None
        
    except Exception as e:
        logger.error(f"Error extrayendo información de Trivago: {e}")
        return None

# =============================================================================
# FUNCIÓN PRINCIPAL DE SCRAPING
# =============================================================================

def scrape_hotels(destino="Cartagena", hotel_limit=20, sources=['booking']):
    """
    FUNCIÓN PRINCIPAL DE SCRAPING
    
    Coordina el scraping de múltiples fuentes y combina los resultados.
    
    Args:
        destino: Ciudad o destino a buscar
        hotel_limit: Número máximo de hoteles por fuente
        sources: Lista de fuentes a scrapear ('booking', 'trivago')
        
    Returns:
        Diccionario con hoteles de todas las fuentes
    """
    logger.info(f"Iniciando scraping multi-fuente para {destino}")
    
    all_hotels = {}
    
    # Scraping de Booking.com
    if 'booking' in sources:
        try:
            booking_hotels = scrape_booking_hotels(destino=destino, hotel_limit=hotel_limit)
            all_hotels['booking'] = booking_hotels
            logger.info(f"Booking.com: {len(booking_hotels)} hoteles obtenidos")
        except Exception as e:
            logger.error(f"Error en scraping de Booking.com: {e}")
            all_hotels['booking'] = []
    
    # Scraping de Trivago
    if 'trivago' in sources:
        try:
            trivago_hotels = scrape_trivago_hotels(destino=destino, hotel_limit=hotel_limit)
            all_hotels['trivago'] = trivago_hotels
            logger.info(f"Trivago: {len(trivago_hotels)} hoteles obtenidos")
        except Exception as e:
            logger.error(f"Error en scraping de Trivago: {e}")
            all_hotels['trivago'] = []
    
    # Combinar todos los hoteles
    combined_hotels = []
    for source, hotels in all_hotels.items():
        for hotel in hotels:
            hotel['source'] = source
            combined_hotels.append(hotel)
    
    logger.info(f"Scraping completado. Total: {len(combined_hotels)} hoteles")
    
    return {
        'hotels': combined_hotels,
        'sources': all_hotels,
        'metadata': {
            'destino': destino,
            'hotel_limit': hotel_limit,
            'sources': sources,
            'scraped_at': datetime.now().isoformat(),
            'total_hotels': len(combined_hotels)
        }
    }

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def save_hotels_to_json(hotels_data, filename='hotels_scraped.json'):
    """
    Guarda los datos de hoteles en un archivo JSON
    
    Args:
        hotels_data: Datos de hoteles a guardar
        filename: Nombre del archivo de salida
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(hotels_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Datos guardados en {filename}")
    except Exception as e:
        logger.error(f"Error guardando datos: {e}")

def load_hotels_from_json(filename='hotels_scraped.json'):
    """
    Carga datos de hoteles desde un archivo JSON
    
    Args:
        filename: Nombre del archivo a cargar
        
    Returns:
        Datos de hoteles cargados
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error cargando datos: {e}")
        return None

# =============================================================================
# EJECUCIÓN DIRECTA (PARA TESTING)
# =============================================================================

if __name__ == "__main__":
    """
    Ejecución directa del scraper para testing
    """
    print("Iniciando scraper de hoteles...")
    
    # Configurar logging para consola
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Ejecutar scraping
    result = scrape_hotels(
        destino="Cartagena",
        hotel_limit=5,
        sources=['booking']
    )
    
    # Mostrar resultados
    print(f"\nScraping completado:")
    print(f"Total de hoteles: {len(result['hotels'])}")
    
    for source, hotels in result['sources'].items():
        print(f"{source}: {len(hotels)} hoteles")
    
    # Guardar resultados
    save_hotels_to_json(result)
    
    print("\nResultados guardados en hotels_scraped.json")


  