#!/usr/bin/env python
from flask import Flask, Blueprint
from flask_restx import Api, Resource, fields
from User import Usuario
import Roles

api_v1 = Blueprint("api", __name__, url_prefix="/api/v1")

api = Api(
    api_v1,
    version="1.0",
    title="Merendar API",
    description="Una api de meriendas",
)

ns = api.namespace("meriendas", description="merienda operations")

#Esto es una base de datos
USUARIOS = {
    "nico": { Usuario("nicog","admin123","mail@com.com",[Roles.PersonRole])},
    "ivana" : { Usuario("ivana","admin345","iva@na.com",[Roles.GastroRole])}
}
print(USUARIOS)
print(list(USUARIOS['nico'])[0])

user = api.model(
    "Usuario", {
        "username"  : fields.String(required=True,  description="El usuario"),
        "password"  : fields.String(required=True,  description="La contraseña"),
        "email"     : fields.String(required=True,  description="El correo"),
        "rol"       : fields.String(required=False, description="Rol del usuario (resto, persona, etc)" )
        }
)

userList = api.model(
    "Usuarios", {
            "id": fields.String(required=True, description="id de usuario"),
            "username": fields.Nested(user, description="El usuario"),
    }
)
#TODO un apimodel para cada cosa (menu item, roles, review, etc)

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
    "role", type=str, required=False, help="Rol", location="form"
)


@ns.route("/<string:username>")
@api.doc(responses={404:"Usuario no encontrado"}, params={"username":"El Usuario"})
class Usuario(Resource):
    """
    Muestra un usuario
    """
    @api.doc(description="Usuario should be in {0}".format(", ".join(USUARIOS.keys())))
    @api.marshal_with(user)
    def get(self, todo_id):
        """Fetch a given resource"""
        return USUARIOS[todo_id]
    
    @api.doc(responses={204: "Todo deleted"})
    def delete(self, todo_id):
        """Delete a given resource"""
        del USUARIOS[todo_id]
        return "", 204

@ns.route("/")
class TodoList(Resource):
    """Shows a list of all todos, and lets you POST to add new tasks"""

    @api.marshal_list_with(userList)
    def get(self):
        """Lista todos los usuarios"""
        return [{"id": id, "user": user} for id, user in USUARIOS.items()]

    @api.doc(parser=parser)
    @api.marshal_with(user, code=201)
    def post(self):
        """Create a user"""
        args = parser.parse_args()
        USUARIOS[args['username']] = Usuario(
            args['username'], args['password'], args['email'], args['role'])
        return USUARIOS[args['username']], 201
    
if __name__ == "__main__":
    app = Flask(__name__)
    app.register_blueprint(api_v1)
    app.run(debug=True)
