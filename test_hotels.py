#!/usr/bin/env python3
"""
Script de prueba para verificar la carga de hoteles
"""

import pytest
from app import app, db, Hoteles, Usuario, Valoraciones, InteraccionesUsuario, PreferenciasUsuario

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

# --- Prueba de registro y login ---
def test_register_and_login(client):
    rv = client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass',
        'confirm': 'testpass'
    }, follow_redirects=True)
    assert b'Bienvenido' in rv.data or b'Perfil' in rv.data
    rv = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    assert b'Bienvenido' in rv.data or b'Perfil' in rv.data

# --- Prueba de preferencias ---
def test_preferencias(client):
    user = Usuario(username='prefuser', email='pref@example.com', password_hash='hash')
    db.session.add(user)
    db.session.commit()
    pref = PreferenciasUsuario(id_usuario=user.id_usuario, estrellas='4,5', rating_minimo=8.0, amenities_importantes='wifi,piscina', ubicacion_preferida='Centro', presupuesto=500000)
    db.session.add(pref)
    db.session.commit()
    assert pref.id_usuario == user.id_usuario

# --- Prueba de creación de hotel y valoración ---
def test_hotel_valoracion(client):
    hotel = Hoteles(nombre='Hotel Test', slug='hotel-test', ubicacion='Centro', precio='100000', stars_count=4, rating_score=8.5, amenities='wifi,piscina', imagenes='', latitud=10.0, longitud=-75.0, contacto='')
    db.session.add(hotel)
    db.session.commit()
    user = Usuario(username='valuser', email='val@example.com', password_hash='hash')
    db.session.add(user)
    db.session.commit()
    val = Valoraciones(id_usuario=user.id_usuario, id_hotel=hotel.id_hotel, puntuacion=9.0, comentario='Muy bueno')
    db.session.add(val)
    db.session.commit()
    assert val.id_hotel == hotel.id_hotel
    assert val.puntuacion == 9.0

# --- Prueba de favoritos ---
def test_favoritos(client):
    hotel = Hoteles(nombre='Hotel Fav', slug='hotel-fav', ubicacion='Centro', precio='200000', stars_count=5, rating_score=9.0, amenities='wifi', imagenes='', latitud=10.0, longitud=-75.0, contacto='')
    db.session.add(hotel)
    db.session.commit()
    user = Usuario(username='favuser', email='fav@example.com', password_hash='hash')
    db.session.add(user)
    db.session.commit()
    fav = InteraccionesUsuario(id_usuario=user.id_usuario, id_hotel=hotel.id_hotel, tipo_interaccion='favorito', valor=1)
    db.session.add(fav)
    db.session.commit()
    assert fav.tipo_interaccion == 'favorito'

# --- Prueba de seguridad de endpoints ---
def test_endpoint_security(client):
    rv = client.get('/api/hotels')
    assert rv.status_code == 200 or rv.status_code == 404
    rv = client.post('/api/valorar', json={'id_hotel': 1, 'puntuacion': 8})
    assert rv.status_code in (401, 400, 404) 