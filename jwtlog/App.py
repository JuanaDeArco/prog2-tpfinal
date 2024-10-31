from flask import Flask, Blueprint, render_template, request, redirect, url_for
from flask_restx import Api, Resource, fields
from User import Usuario
import Roles

app = Flask(__name__, template_folder='paginas')
api_v1 = Blueprint("api", __name__, url_prefix="/api")

api = Api(
    api_v1,
    version="1.0",
    title="MerendAR",
    description="Merendate esta",
)

ns = api.namespace("meriendas", description="merienda operations")

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

@ns.route("/<string:username>")
@api.doc(responses={404: "Usuario no encontrado"}, params={"username": "El Usuario"})
class UsuarioResource(Resource):
    @api.doc(description="Usuario should be in {0}".format(", ".join(USUARIOS.keys())))
    @api.marshal_with(user)
    def get(self, username):
        return USUARIOS[username]

    @api.doc(responses={204: "Todo deleted"})
    def delete(self, username):
        del USUARIOS[username]
        return "", 204

@ns.route("/")
class TodoList(Resource):
    @api.marshal_list_with(userList)
    def get(self):
        return [{"id": id, "user": user} for id, user in USUARIOS.items()]

    @api.doc(parser=parser)
    @api.marshal_with(user, code=201)
    def post(self):
        args = parser.parse_args()
        role = role_mapping.get(args['role'])
        USUARIOS[args['username']] = Usuario(
            args['username'], args['password'], args['email'], [role])
        return redirect(url_for('login'))  # Redirige al login después de registrarse

app.register_blueprint(api_v1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

if __name__ == "__main__":
    app.run(debug=True)
