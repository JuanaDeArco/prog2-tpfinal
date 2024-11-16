"""
Este es el codigo de la api
"""
from flask import Flask, Blueprint, render_template, request, redirect, url_for, jsonify, session
from flask_restx import Api, Resource, fields, Namespace
from src.User import Usuario
from . import api, app
from src.GatronomicUser import UsuarioGastronomico
from src.PersonalUser import UsuarioPersonal
from src.MenuItem import MenuItem
import src.Roles as Roles
from api.Auth import decode_token, generate_token
import os
from .models import db, ConfirmedUser, PotentialUser
from datetime import datetime

ns = Namespace("meriendas", description="merienda operations")

user = api.model(
    "Usuario", {
        "username": fields.String(required=True, description="El usuario"),
        "password": fields.String(required=True, description="La contraseña"),
        "email": fields.String(required=True, description="El correo"),
        "rol": fields.String(required=False, description="Rol del usuario (resto, persona, etc)")
    }
)

userList = api.model(
    "Usuarios", {
        "id": fields.String(required=True, description="id de usuario"),
        "username": fields.Nested(user, description="El usuario"),
    }
)

# Diccionario para mapear opciones visibles a roles internos
role_mapping = {
    "Personal": Roles.PersonRole,
    "Gastronómico": Roles.GastroRole
}

parser = api.parser()
parser.add_argument(
    "username", type=str, required=True, help="usuario", location="form"
)
parser.add_argument(
    "password", type=str, required=True, help="<PASSWORD>", location="form"
)
parser.add_argument(
    "email", type=str, required=True, help="correo", location="form"
)
parser.add_argument(
    "role", type=str, required=False, help="Rol", location="form", choices=list(role_mapping.keys())
)

@app.route('/routes')
def show_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f'{rule.endpoint}: {rule.rule}')
    return "<br>".join(routes)

### APP.ROUTE son las visualizaciones de la PAGINA
# O sea, los render template
@app.route('/')
def Index():
    return render_template('index.html')

### NS.ROUTE son los controles de la API
# o sea, los GETS-POSTS
@ns.route('/')
@ns.doc(description="Este seria un endpoint normal")
class Index(Resource):
    def get(self):
        return jsonify({"hotel":"trivago"})

### TODO: Todo lo que esta aca abajo
@ns.route('/login')
class Login(Resource):
    def get(self):
        return render_template('login.html')
    
    def post(self):
        username = request.form.get("username")
        password = request.form.get("password")

        print(username)
        print(password)

        if 1 == 1: #aca va una mejor logica de validacion cuando este lo de alchemy
            session['username'] = username
            session['password'] = password     
            return redirect(url_for('home_page'))
    
@app.route('/login')
def login_page():
    return render_template('login.html')

@ns.route('/register')
class Register(Resource):
    def get(self):
        return render_template('register.html')
        
    def post(self):
        '''Crea un usuario nuevo y lo agrega al archivo de texto donde por ahora tenemos todos los usuarios.
        Esto más adelante va a ser una base de datos.
        Restricciones:
        - Todos los campos tienen que ser completados
        - La contraseña tiene que tener mínimo 6 caracteres
        - Para que el mail sea válido, tiene que tener un @ en algún lado
        - No se pueden repetir usuarios ni emails'''

        user_first_name = request.form.get("user_first_name")
        user_last_name = request.form.get("user_last_name")
        date_of_birth = request.form.get("date_of_birth")
        gender = request.form.get("gender")
        user_phone_number = request.form.get("user_phone_number")
        user_document_type = request.form.get("user_document_type")
        user_document = request.form.get("user_document")
        user_email = request.form.get("user_email")
        user_username = request.form.get("user_username")
        password = request.form.get("password")
        user_type = request.form.get("user_type")
        
        if not all([user_first_name, user_last_name, date_of_birth, gender, user_phone_number, 
                    user_document_type, user_document, user_email, user_username, password, user_type]):
            return jsonify({'message': 'Todos los campos son obligatorios'}), 400

        if "@" not in user_email:
            return jsonify({'message': 'El correo electrónico debe tener un formato válido'}), 400

        if len(password) < 6:
            return jsonify({'message': 'La contraseña debe tener al menos 6 caracteres'}), 400

        existing_user = ConfirmedUser.query.filter(
            (ConfirmedUser.user_username == user_username) | 
            (ConfirmedUser.user_email == user_email)
        ).first()
        if existing_user:
            return jsonify({'message': 'El nombre de usuario o correo electrónico ya está registrado'}), 400

        potential_user = PotentialUser.query.filter(
            (PotentialUser.user_username == user_username) | 
            (PotentialUser.user_email == user_email)
        ).first()
        if potential_user:
            return jsonify({'message': 'El nombre de usuario o correo electrónico ya está registrado'}), 400

        new_user = PotentialUser(
            user_first_name=user_first_name,
            user_last_name=user_last_name,
            date_of_birth=datetime.strptime(date_of_birth, "%Y-%m-%d"),
            gender=gender,
            user_phone_number=user_phone_number,
            user_document_type=user_document_type,
            user_document=user_document,
            user_email=user_email,
            user_username=user_username,
            password_hash=password,
            user_type=user_type,
            is_verified=False
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('confirm_page'))

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/confirm')
def confirm_page():
    return render_template('confirm.html')

##TODO
@app.route('/home')
def home_page():
    return  f"faaaaaa cero seguridad habia"

@app.route('/user/<user>')
def user_page(user):
    return f"Aca va el perfil de {user} - {session['username']}"

@ns.route('/user/<name>')
class UserProfile(Resource):
    def get(self, name):
        pass #LOGICA

if __name__ == "__main__":
    app = Flask(__name__)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

