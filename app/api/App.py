"""
Este es el codigo de la api
"""
from flask import Flask, Blueprint, render_template, request, redirect, url_for, jsonify
from flask_restx import Api, Resource, fields, Namespace
from src.User import Usuario
from . import api, app
from src.GatronomicUser import UsuarioGastronomico
from src.PersonalUser import UsuarioPersonal
from src.MenuItem import MenuItem
import src.Roles as Roles
from api.Auth import decode_token, generate_token
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'usuarios.txt')

ns = Namespace("meriendas", description="merienda operations")

# Esto es una base de datos
USUARIOS = {
    "nico": Usuario("nicog", "admin123", "mail@com.com", [Roles.PersonRole]),
    "ivana": Usuario("ivana", "admin345", "iva@na.com", [Roles.GastroRole])
}

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
    def get():
        return render_template('login.html')

@ns.route('/register')
class Register(Resource):
    def get():
        return render_template('register.html')
    def post():
        '''Crea un usuario nuevo y lo agrega al archivo de texto donde por ahora tenemos todos los usuarios.
        Esto más adelante va a ser una base de datos.
        Restricciones:
        - Todos los campos tienen que ser completados
        - La contraseña tiene que tener mínimo 6 caracteres
        - Para que el mail sea válido, tiene que tener un @ en algún lado
        - No se pueden repetir usuarios ni emails'''
        username = request.form.get("usuario")
        password = request.form.get("password") # ojo, se está guardando en texto plano
        email = request.form.get("email")
        user_type = request.form.get("user_type")
        
        if not username or not password or not email or not user_type:
            return jsonify({'message': 'Ningún campo puede estar vacío'}), 400
        if "@" not in email:
            return jsonify({'message': 'El correo electrónico debe tener un formato adecuado'}), 400
        if len(password) < 6:
            return jsonify({'message': 'La contraseña debe tener al menos 6 caracteres'}), 400
        
        with open(file_path, 'r') as f: 
            lista = f.readlines()
            for linea in lista:
                if username in linea:
                    return jsonify({'message': 'El nombre de usuario ya está siendo utilizado'}), 400
                if email in linea:
                    return jsonify({'message': 'El correo electrónico ya está siendo utilizado'}), 400

        if user_type == 'gastronomico':
            usuario = UsuarioGastronomico(username=username, password=password, email=email)
        elif user_type == 'personal':
            usuario = UsuarioPersonal(username=username, password=password, email=email)
        else:
            return jsonify({'message': 'Tipo de usuario no válido'}), 400

        with open(file_path, 'a+') as f:
            f.write(f"{usuario.id},{usuario.username},{usuario.password},{usuario.email},{user_type}\n")
            return jsonify({'message': 'Usuario creado con éxito'}), 200

if __name__ == "__main__":
    app = Flask(__name__)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

