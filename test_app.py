import pytest
from app import app, db, Usuario, PreferenciasUsuario
from flask import url_for

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_register_and_login(client):
    # Registro
    resp = client.post('/auth?tab=register', data={
        'register-nombre_usuario': 'TestUser',
        'register-email': 'test@example.com',
        'register-contrasena': '12345678',
        'register-confirmar_contrasena': '12345678',
        'register-submit': True
    }, follow_redirects=True)
    assert b'Registro exitoso' in resp.data
    # Login
    resp = client.post('/auth?tab=login', data={
        'login-email': 'test@example.com',
        'login-contrasena': '12345678',
        'login-submit': True
    }, follow_redirects=True)
    assert b'Bienvenido de nuevo' in resp.data or b'Preferencias' in resp.data

def test_preferencias(client):
    # Crear usuario y login
    u = Usuario(nombre='PrefUser', email='pref@example.com', password_hash='hash')
    db.session.add(u)
    db.session.commit()
    with client.session_transaction() as sess:
        sess['user_id'] = u.id_usuario
    # Guardar preferencias
    resp = client.post('/preferencias', data={
        'tipo_viaje': 'Negocios',
        'presupuesto': 'Medio',
        'ubicacion_preferida': 'Centro Histórico',
        'estrellas': ['3', '4'],
        'puntuaciones': ['8', '9'],
        'servicios': ['WiFi'],
        'ubicaciones': ['Centro Histórico'],
        'rating_minimo': 8.0,
        'submit': True
    }, follow_redirects=True)
    assert b'Preferencias guardadas' in resp.data

def test_endpoint_protegido(client):
    # Sin login
    resp = client.post('/perfil/borrar_historial', follow_redirects=True)
    assert b'Iniciar sesi' in resp.data or resp.status_code == 401

# Puedes agregar más tests para valorar, favoritos, errores, etc. 