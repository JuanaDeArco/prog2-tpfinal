from app.api import app, db
import pytest
from app.api.models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_register_personal_post_all_fields_valid(client):
    """
    Testea la creacion de un usuario desde la API en si
    """
    data = {
        "user_first_name": "John",
        "user_last_name": "Doe",
        "date_of_birth": "2000-01-01",
        "gender": "M",
        "user_phone_number": "1234567890",
        "user_document_type": "DNI",
        "user_document": "12345678",
        "user_email": "john.doe@example.com",
        "user_username": "johndoe",
        "password": "StrongPassword123!",
        "user_province": "Buenos Aires",
        "user_postal_code": "C1000ABC",
    }

    response = client.post('/api/meriendas/personal', data=data)

    assert response.status_code == 302

def test_confirm(client):
    """
    Verifica que la pagina /login existe
    """
    response = client.get('/login')
    assert response.status_code == 200


def test_personal_site(client):
    """
    Verifica que /personal exista
    """
    response = client.get('/personal')
    assert  response.status_code == 200

def test_personal(client):
    """
    Verifica que el endpoint de personal exista
    """
    response = client.get('/api/meriendas/personal')
    assert  response.status_code == 200

def test_register_gastronomic_site(client):
    """
    Verifica que la pagina exista
    """
    response = client.get('/gastronomic')
    assert  response.status_code == 200

def test_register_gastronomic(client):
    """
    Testea la creación de un usuario gastronómico desde la API en si
    """
    data = {
    "user_nombre_comercial": "Mi Empresa",
    "user_phone_number": "1234567890",
    "user_document_type": "CUIT",
    "user_document": "20-301234567-9",
    "user_rep_legal": "Juan Perez",
    "user_province": "Buenos Aires",
    "user_postal_code": "1414",
    "user_username": "mi_empresa",
    "user_email": "miempresa@example.com",
    "user_raz_soc": "Mi Empresa S.A.",
    "user_rep_legal_doc": "DNI",
    "user_address": "Calle Falsa 123",
    "password": "strongPassword123",
    "user_type": "G"
    }
    response = client.post('/api/meriendas/gastronomic', data=data)
    assert response.status_code == 302  # Expected redirect


def test_index(client):
    """
    Verifica que exista el endpoint de meriendas y que devuelva el json adecuado
    """
    response = client.get('/api/meriendas/')
    assert response.status_code == 200
    assert response.json == {'hotel': 'trivago'}

def test_homepage(client):
    """
    Verifica que exista la página
    """
    response = client.get('/')
    assert response.status_code == 200

def test_select(client):
    """
    Verifica que exista la página
    """
    response = client.get('/select')
    assert response.status_code == 200

def test_search_redirect_no_token(client):
    """
    Verifica que el search no sea accesible sin token
    Si no hay un token, la logica del sitio es redireccionar al home, asi que el status code es 302
    """
    response = client.get('/search')
    
    assert response.status_code == 302
    assert response.headers['Location'] == '/'

def test_home_redirect_no_token(client):
    """
    Verifica que haya un redirect cuando no hay token
    Si no hay token, redirecciona (302) y va al home
    """
    response = client.get('/home')
    assert response.status_code == 302
    assert response.headers['Location'] == '/'

def test_create_menu_item_redirect_no_token(client):
    """
    Verifica que haya un redirect cuando no hay token
    en el endpoint de crear menu item
    """
    response = client.get('/user/create_menu_item')
    assert response.status_code == 302
    assert response.headers['Location'] == '/'

def test_create_folder_redirect_no_token(client):
    """
    Verifica que haya un redirect cuando no hay token
    en crear folders
    """
    response = client.get('/user/create_folder')
    assert response.status_code == 302
    assert response.headers['Location'] == '/'