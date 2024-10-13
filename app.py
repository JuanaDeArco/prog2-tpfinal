from flask import Flask, jsonify
from flask_restful import Resource, Api

app = Flask(__name__)

@app.route("/")
def index():
    return "ACA VA LO QUE DEVUELVE CUANDO UNO VA A LA PAG -- LOGIN?"

@app.route("/login")
def login():
    return "quiero loggearme"

@app.route("/login/user")
def mi_ferfil():
    return "mi perfil"

api = Api(app)

class HelloWorld(Resource):
    def get(self):
        return {"hello": "world"}
    
api.add_resource(HelloWorld, "/")

if __name__ == "__main__":
    app.run(debug=True)
