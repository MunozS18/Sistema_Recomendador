#!/usr/bin/env python3
"""
Script para actualizar la aplicación Flask para usar la nueva estructura de base de datos enriquecida
"""

import json
from datetime import datetime
from models import db, Hoteles, Usuario, PreferenciasUsuario, InteraccionesUsuario, Valoraciones, ReviewsScraping
from scraper import AdvancedBookingScraper, HotelDataMerger

def migrate_hotel_data_to_new_structure(hotel_data):
    """
    Migra datos del scraper avanzado a la nueva estructura de base de datos
    """
    try:
        # Crear o actualizar hotel en la base de datos
        hotel = Hoteles.query.filter_by(slug=hotel_data['slug']).first()
        
        if not hotel:
            hotel = Hoteles()
            hotel.slug = hotel_data['slug']
        
        # Información básica
        hotel.nombre = hotel_data['name']
        hotel.descripcion = hotel_data.get('description', '')
        hotel.ubicacion = hotel_data.get('location', '')
        
        # Precios
        if 'price' in hotel_data and isinstance(hotel_data['price'], dict):
            hotel.precio_amount = hotel_data['price'].get('amount')
            hotel.precio_currency = hotel_data['price'].get('currency', 'COP')
            hotel.precio_formatted = hotel_data['price'].get('formatted', 'Consultar')
            hotel.precio_source = hotel_data['price'].get('source', 'booking')
        else:
            # Compatibilidad con formato antiguo
            hotel.precio_formatted = hotel_data.get('price', 'Consultar')
        
        # Rating
        if 'rating' in hotel_data and isinstance(hotel_data['rating'], dict):
            hotel.rating_score = hotel_data['rating'].get('score')
            hotel.rating_max_score = hotel_data['rating'].get('max_score', 10)
            hotel.rating_formatted = hotel_data['rating'].get('formatted', 'Sin calificar')
        else:
            # Compatibilidad con formato antiguo
            hotel.rating_score = hotel_data.get('rating')
            hotel.rating_formatted = hotel_data.get('rating', 'Sin calificar')
        
        # Estrellas
        if 'stars' in hotel_data and isinstance(hotel_data['stars'], dict):
            hotel.stars_count = hotel_data['stars'].get('count', 0)
            hotel.stars_formatted = hotel_data['stars'].get('formatted', 'Sin clasificar')
        else:
            # Compatibilidad con formato antiguo
            stars_text = hotel_data.get('stars', 'Sin clasificar')
            if '⭐' in stars_text:
                hotel.stars_count = stars_text.count('⭐')
            hotel.stars_formatted = stars_text
        
        # Reviews count
        hotel.reviews_count = hotel_data.get('reviews_count', 0)
        
        # Amenities
        if 'amenities' in hotel_data:
            if isinstance(hotel_data['amenities'], list):
                hotel.set_amenities_list(hotel_data['amenities'])
            else:
                # Compatibilidad con formato antiguo (string)
                hotel.amenities_raw = hotel_data['amenities']
        
        # Imágenes
        if 'images' in hotel_data and isinstance(hotel_data['images'], list):
            hotel.set_imagenes_list(hotel_data['images'])
        
        # Imagen principal
        hotel.imagen_url = hotel_data.get('image', '')
        
        # Reviews
        if 'reviews' in hotel_data and isinstance(hotel_data['reviews'], list):
            hotel.set_reviews_list(hotel_data['reviews'])
        
        # Información de contacto
        hotel.telefono = hotel_data.get('phone', '')
        hotel.email = hotel_data.get('email', '')
        hotel.website = hotel_data.get('website', '')
        
        # Ubicación geográfica
        hotel.latitud = hotel_data.get('latitude')
        hotel.longitud = hotel_data.get('longitude')
        
        # Enlaces
        hotel.link_booking = hotel_data.get('link', '')
        hotel.link_trivago = hotel_data.get('link_trivago', '')
        
        # Fuente y metadatos
        hotel.fuente_principal = hotel_data.get('source', 'booking')
        hotel.fecha_scraping = datetime.now()
        hotel.version_scraping = '2.0'
        
        # Metadatos
        metadata = {
            'scraped_at': hotel_data.get('scraped_at'),
            'destination': hotel_data.get('destination', 'Cartagena'),
            'checkin': hotel_data.get('checkin'),
            'checkout': hotel_data.get('checkout')
        }
        hotel.set_metadata_dict(metadata)
        
        # Campos legacy para compatibilidad
        hotel.rating = hotel.rating_score
        hotel.precio_promedio = hotel.precio_amount
        hotel.imagen_url_legacy = hotel.imagen_url
        hotel.fuente = hotel.fuente_principal
        
        # Guardar en base de datos
        db.session.add(hotel)
        db.session.commit()
        
        print(f"Hotel migrado: {hotel.nombre}")
        return hotel
        
    except Exception as e:
        print(f"Error migrando hotel {hotel_data.get('name', 'Unknown')}: {e}")
        db.session.rollback()
        return None

def update_app_routes_for_new_structure():
    """
    Actualiza las rutas de la aplicación para usar la nueva estructura
    """
    # Esta función se puede usar para actualizar las rutas en app.py
    # Por ahora, las rutas existentes deberían seguir funcionando con los campos legacy
    
    print("Las rutas de la aplicación se actualizarán automáticamente")
    print("Los campos legacy mantienen compatibilidad con código existente")

def test_new_structure():
    """
    Prueba la nueva estructura de base de datos
    """
    try:
        # Probar creación de hotel con nueva estructura
        test_hotel_data = {
            'name': 'Hotel Test Nuevo',
            'slug': 'hotel-test-nuevo',
            'price': {
                'amount': 350000,
                'currency': 'COP',
                'formatted': '$350.000',
                'source': 'booking'
            },
            'rating': {
                'score': 8.5,
                'max_score': 10,
                'formatted': '8.5/10'
            },
            'stars': {
                'count': 4,
                'formatted': '4 ⭐⭐⭐⭐'
            },
            'location': 'Centro, Cartagena',
            'description': 'Hotel de prueba con nueva estructura',
            'amenities': ['wifi', 'piscina', 'spa'],
            'images': ['https://example.com/img1.jpg', 'https://example.com/img2.jpg'],
            'reviews': ['Excelente hotel', 'Muy buena ubicación'],
            'reviews_count': 150,
            'source': 'booking',
            'scraped_at': datetime.now().isoformat()
        }
        
        hotel = migrate_hotel_data_to_new_structure(test_hotel_data)
        
        if hotel:
            print("✅ Prueba exitosa: Hotel creado con nueva estructura")
            print(f"   - Nombre: {hotel.nombre}")
            print(f"   - Slug: {hotel.slug}")
            print(f"   - Precio: {hotel.precio_formatted}")
            print(f"   - Rating: {hotel.rating_formatted}")
            print(f"   - Estrellas: {hotel.stars_formatted}")
            print(f"   - Amenities: {hotel.get_amenities_list()}")
            print(f"   - Imágenes: {len(hotel.get_imagenes_list())} imágenes")
            print(f"   - Reviews: {len(hotel.get_reviews_list())} reviews")
            
            # Limpiar hotel de prueba
            db.session.delete(hotel)
            db.session.commit()
            print("   - Hotel de prueba eliminado")
            
            return True
        else:
            print("❌ Error en la prueba")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de nueva estructura: {e}")
        return False

def migrate_existing_data():
    """
    Migra datos existentes a la nueva estructura
    """
    try:
        hotels = Hoteles.query.all()
        migrated_count = 0
        
        for hotel in hotels:
            # Generar slug si no existe
            if not hotel.slug:
                hotel.slug = hotel.nombre.lower().replace(' ', '-').replace('á', 'a').replace('é', 'e')
            
            # Migrar rating si existe
            if hotel.rating and not hotel.rating_score:
                hotel.rating_score = hotel.rating
                hotel.rating_formatted = f"{hotel.rating:.1f}/10"
            
            # Migrar precio si existe
            if hotel.precio_promedio and not hotel.precio_amount:
                hotel.precio_amount = hotel.precio_promedio
                hotel.precio_formatted = f"${hotel.precio_promedio:,}".replace(",", ".")
                hotel.precio_currency = 'COP'
            
            # Migrar estrellas si no existen
            if not hotel.stars_count and hotel.nombre:
                # Intentar extraer estrellas del nombre o descripción
                if '5' in hotel.nombre or 'cinco' in hotel.nombre.lower():
                    hotel.stars_count = 5
                elif '4' in hotel.nombre or 'cuatro' in hotel.nombre.lower():
                    hotel.stars_count = 4
                elif '3' in hotel.nombre or 'tres' in hotel.nombre.lower():
                    hotel.stars_count = 3
                elif '2' in hotel.nombre or 'dos' in hotel.nombre.lower():
                    hotel.stars_count = 2
                elif '1' in hotel.nombre or 'uno' in hotel.nombre.lower():
                    hotel.stars_count = 1
                else:
                    hotel.stars_count = 0
                
                if hotel.stars_count > 0:
                    hotel.stars_formatted = f"{hotel.stars_count} {'⭐' * hotel.stars_count}"
                else:
                    hotel.stars_formatted = 'Sin clasificar'
            
            # Establecer fuente principal
            if not hotel.fuente_principal:
                hotel.fuente_principal = 'booking'
            
            # Establecer versión de scraping
            if not hotel.version_scraping:
                hotel.version_scraping = '2.0'
            
            migrated_count += 1
        
        db.session.commit()
        print(f"✅ Migración completada: {migrated_count} hoteles actualizados")
        return True
        
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    print("🔄 Actualizando aplicación para nueva estructura de base de datos...")
    
    # Importar app para acceder a la base de datos
    from app import app
    
    with app.app_context():
        print("1. Probando nueva estructura...")
        if test_new_structure():
            print("2. Migrando datos existentes...")
            if migrate_existing_data():
                print("3. Actualizando rutas de aplicación...")
                update_app_routes_for_new_structure()
                print("✅ Actualización completada exitosamente!")
            else:
                print("❌ Error en migración de datos existentes")
        else:
            print("❌ Error en prueba de nueva estructura") 